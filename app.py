from streamlit_lottie import st_lottie
from streamlit_autorefresh import st_autorefresh
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import os
from db import get_sales_data, get_inventory_data, get_alert_data
from product_images import product_images
import PIL
from admin_panel import admin_panel
from auth import admin_login
from prophet import Prophet
import numpy as np
import pdfkit

path_to_wkhtmltopdf = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"  # Update if your path is different
config = pdfkit.configuration(wkhtmltopdf=path_to_wkhtmltopdf)

# --- Page Config ---
st.set_page_config(page_title="Retail Dashboard", layout="wide")
st_autorefresh(interval=60000, key="dashboard_refresh")  # Refresh every 1 minute

# --- Lottie Loader ---
def load_lottie_file(path):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception:
        return None

lottie_dashboard = load_lottie_file("assets/dashboard.json")

# --- Modern Header ---
col_logo, col_title = st.columns([3, 8])
with col_logo:
    if lottie_dashboard:
        st_lottie(lottie_dashboard, height=260, width=260)
with col_title:
    st.markdown(
        """
        <div style="display:flex;align-items:center;">
            <span style="font-size:2.7rem; margin-right:12px;">🤖</span>
            <span class="futuristic-header">
                Retail Inventory & Auto-Restock Dashboard
            </span>
        </div>
        <div style="font-size:1.15rem; color:#b0b3b8; margin-top:0.2rem;">
            <em>All your inventory, sales, and alerts in one interactive place.</em>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("---")

# --- Load data ---
df_sales = get_sales_data()
df_inventory = get_inventory_data()
df_alerts = get_alert_data()

# --- Animated KPI Cards ---
kpi1, kpi2, kpi3 = st.columns(3)
with kpi1:
    st.markdown("#### 🛒 <span style='color:#eebbc3'>Total Sales</span>", unsafe_allow_html=True)
    st.metric(label="", value=f"{df_sales['quantity_sold'].sum():,}")
with kpi2:
    st.markdown("#### 📦 <span style='color:#007bff'>Products</span>", unsafe_allow_html=True)
    st.metric(label="", value=f"{df_inventory['product_name'].nunique()}")
with kpi3:
    st.markdown("#### 🚨 <span style='color:#ff4b4b'>Alerts</span>", unsafe_allow_html=True)
    st.metric(label="", value=f"{len(df_alerts)}")

# --- Sidebar Summary & Filters ---
with st.sidebar:
    st.markdown("## 🏪 Quick Stats")
    st.metric("Total Products", f"{df_inventory['product_name'].nunique()}")
    st.metric("Total Sales", f"{df_sales['quantity_sold'].sum():,}")
    st.metric("Active Alerts", f"{len(df_alerts)}")
    st.markdown("---")

    filtered_inventory = df_inventory.copy()
    filtered_sales = df_sales.copy()

    with st.expander("🔍 Filters", expanded=True):
        st.markdown("#### Select Category", unsafe_allow_html=True)
        if not df_inventory.empty:
            category_options = ["All"] + list(df_inventory["category"].unique())
            category_filter = st.selectbox(
                "",
                category_options,
                key="category_filter",
                help="Filter inventory and sales by product category."
            )
            if category_filter != "All":
                filtered_inventory = filtered_inventory[filtered_inventory["category"] == category_filter]
                filtered_sales = filtered_sales[filtered_sales["product_name"].isin(filtered_inventory["product_name"])]

        st.markdown("### 📅 Date Filter")
        if not df_sales.empty and "sale_date" in df_sales.columns:
            min_date = pd.to_datetime(df_sales["sale_date"]).min()
            max_date = pd.to_datetime(df_sales["sale_date"]).max()
            if pd.isna(min_date) or pd.isna(max_date):
                import datetime
                min_date = max_date = datetime.date.today()
            date_range = st.date_input(
                "Select Date Range",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date,
                key="date_range",
                help="Pick a start and end date to filter sales data."
            )
            if isinstance(date_range, (tuple, list)):
                start_date, end_date = date_range
            else:
                start_date = end_date = date_range
            filtered_sales = filtered_sales[
                (pd.to_datetime(filtered_sales["sale_date"]) >= pd.to_datetime(start_date)) &
                (pd.to_datetime(filtered_sales["sale_date"]) <= pd.to_datetime(end_date))
            ]
        else:
            st.info("No sales data available to filter by date.")

    # Admin Mode
    if st.checkbox("🛠 Admin Mode", key="admin_mode"):
        if admin_login():
            admin_panel()

# --- Floating Action Button (FAB) ---
st.markdown("""
    <style>
    .fab {
        position: fixed;
        bottom: 40px;
        right: 40px;
        background: #007bff;
        color: white;
        border-radius: 50%;
        width: 60px;
        height: 60px;
        font-size: 2rem;
        text-align: center;
        line-height: 60px;
        box-shadow: 2px 2px 10px #888;
        z-index: 100;
        cursor: pointer;
    }
    .fab {
        animation: pulse 1.5s infinite;
    }
    @keyframes pulse {
        0% {box-shadow: 0 0 16px #00eaff;}
        50% {box-shadow: 0 0 32px #007bff;}
        100% {box-shadow: 0 0 16px #00eaff;}
    }
    </style>
    <div class="fab" title="Quick Action">+</div>
""", unsafe_allow_html=True)

# --- Tabs ---
inv_tab, sales_tab, alerts_tab = st.tabs([
    "🧱 Inventory", "📈 Sales Analytics", "🚨 Restock Alerts"
])

# --- Inventory Tab ---
with inv_tab:
    st.subheader("📦 Inventory Overview with Images")
    num_cols = 3

    unique_inventory = filtered_inventory.drop_duplicates(subset=["product_name"])
    rows = [unique_inventory.iloc[i:i+num_cols] for i in range(0, len(unique_inventory), num_cols)]
    for row in rows:
        cols = st.columns(num_cols)
        for idx, (_, item) in enumerate(row.iterrows()):
            with cols[idx]:
                product_name = item['product_name']
                lookup_name = product_name.strip().lower()
                normalized_images = {k.strip().lower(): v for k, v in product_images.items()}
                img_url = normalized_images.get(lookup_name)

                if img_url and os.path.exists(img_url):
                    try:
                        st.image(img_url, width=100)
                    except PIL.UnidentifiedImageError:
                        fallback_path = os.path.join("assets", "images", "no_image.png")
                        if os.path.exists(fallback_path):
                            st.image(fallback_path, width=100)
                        else:
                            st.write("No image available")
                else:
                    fallback_path = os.path.join("assets", "images", "no_image.png")
                    if os.path.exists(fallback_path):
                        st.image(fallback_path, width=100)
                    else:
                        st.write("No image available")

                st.markdown(
                    f"<div class='product-title'>{item['product_name']}</div>"
                    f"<div class='product-category'>Category: {item['category']}</div>"
                    f"<div class='product-stock'>In Stock: <b>{item['quantity_in_stock']}</b></div>"
                    f"<div class='product-stock'>Reorder at: <b>{item['reorder_level']}</b></div>",
                    unsafe_allow_html=True
                )

    st.markdown("### 📊 Inventory Distribution")
    col1, col2 = st.columns([2, 1])

    with col1:
        # Inventory by Category Donut
        fig_pie = px.pie(
            df_inventory, names="category", values="quantity_in_stock",
            title="Inventory by Category", hole=0.5,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_pie.update_traces(textfont_size=16)
        st.plotly_chart(fig_pie, use_container_width=True)

    with col2:
        # Inventory Bar Chart
        fig_bar = px.bar(
            df_inventory.sort_values("quantity_in_stock", ascending=False),
            x="quantity_in_stock", y="product_name", orientation="h",
            color="category", title="Stock by Product",
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig_bar.update_layout(yaxis_title="", xaxis_title="Stock", font=dict(size=14), height=400)
        st.plotly_chart(fig_bar, use_container_width=True)

    # Animated Progress Bars for Stock Levels
    st.markdown("### 🟩 Inventory Stock Progress")
    for _, row in df_inventory.iterrows():
        pct = min(100, int(100 * row["quantity_in_stock"] / max(row["reorder_level"], 1)))
        st.markdown(
            f"<b>{row['product_name']}</b> ({row['quantity_in_stock']} in stock)",
            unsafe_allow_html=True
        )
        st.progress(pct)

    st.dataframe(df_inventory, use_container_width=True, height=400)
    st.download_button("⬇ Download Inventory CSV", df_inventory.to_csv(index=False), file_name="inventory.csv")

# --- Sales Tab ---
with sales_tab:
    # --- AI: Product Demand Forecast ---
    st.subheader("🤖 Product Demand Forecast (AI)")
    product_list = df_sales["product_name"].unique().tolist()
    selected_product = st.selectbox("Select a product to forecast", product_list, key="forecast_product")
    product_sales = df_sales[df_sales["product_name"] == selected_product]
    if not product_sales.empty:
        df_prophet = product_sales.groupby("sale_date")["quantity_sold"].sum().reset_index()
        df_prophet.columns = ["ds", "y"]
        if len(df_prophet) > 2:  # Prophet needs at least 2 data points
            m = Prophet()
            m.fit(df_prophet)
            future = m.make_future_dataframe(periods=30)
            forecast = m.predict(future)
            st.line_chart(forecast.set_index("ds")["yhat"])
            st.caption(f"Forecasted demand for {selected_product} (next 30 days)")
        else:
            st.info("Not enough sales data for forecasting this product.")

    # --- AI: Product Recommendations ---
    st.subheader("🧠 Product Recommendations")
    if not df_sales.empty and "category" in df_inventory.columns:
        cat_options = ["All"] + list(df_inventory["category"].unique())
        rec_category = st.selectbox("Select category for recommendations", cat_options, key="rec_category")
        if rec_category != "All":
            top_products = (
                df_sales[df_sales["product_name"].isin(
                    df_inventory[df_inventory["category"] == rec_category]["product_name"]
                )]
                .groupby("product_name")["quantity_sold"].sum()
                .sort_values(ascending=False)
                .head(3)
            )
            st.markdown("**Top recommended products:**")
            for prod, qty in top_products.items():
                st.write(f"- {prod} (sold: {qty})")
        else:
            st.info("Select a category to get recommendations.")

    # --- AI: Sales Anomaly Detection ---
    st.subheader("⚡ Sales Anomaly Detection (AI)")
    if not df_sales.empty:
        sales_daily = df_sales.groupby("sale_date")["quantity_sold"].sum().reset_index()
        sales_daily["zscore"] = (sales_daily["quantity_sold"] - sales_daily["quantity_sold"].mean()) / sales_daily["quantity_sold"].std()
        anomalies = sales_daily[np.abs(sales_daily["zscore"]) > 2]
        if not anomalies.empty:
            st.warning(f"⚠️ Anomalous sales days detected: {len(anomalies)}")
            st.dataframe(anomalies[["sale_date", "quantity_sold", "zscore"]])
        else:
            st.success("No significant anomalies detected in sales.")

    # --- Trending Analytics ---
    col1, col2 = st.columns([2, 1])
    with col1:
        # Sales Over Time (Line)
        if not df_sales.empty:
            df_sales["sale_date"] = pd.to_datetime(df_sales["sale_date"])
            sales_daily = df_sales.groupby("sale_date")["quantity_sold"].sum().reset_index()
            fig_line = px.line(
                sales_daily, x="sale_date", y="quantity_sold",
                title="Total Sales Over Time", markers=True,
                color_discrete_sequence=["#007bff"]
            )
            fig_line.update_layout(xaxis_title="Date", yaxis_title="Units Sold", font=dict(size=14))
            st.plotly_chart(fig_line, use_container_width=True)

            # Cumulative Sales
            sales_daily["cumulative"] = sales_daily["quantity_sold"].cumsum()
            fig_cum = px.area(
                sales_daily, x="sale_date", y="cumulative",
                title="Cumulative Sales", color_discrete_sequence=["#eebbc3"]
            )
            fig_cum.update_layout(xaxis_title="Date", yaxis_title="Cumulative Units", font=dict(size=14))
            st.plotly_chart(fig_cum, use_container_width=True)

    with col2:
        # Top Products Bar
        sales_summary = df_sales.groupby("product_name", as_index=False)["quantity_sold"].sum()
        fig_top = px.bar(
            sales_summary.sort_values("quantity_sold", ascending=True),
            x="quantity_sold", y="product_name", orientation="h",
            title="Top Selling Products",
            color="quantity_sold", color_continuous_scale="Blues"
        )
        fig_top.update_layout(yaxis_title="", xaxis_title="Units Sold", font=dict(size=14), height=400)
        st.plotly_chart(fig_top, use_container_width=True)

    # Sales Funnel Chart
    if not df_sales.empty:
        funnel_df = df_sales.groupby("product_name")["quantity_sold"].sum().reset_index()
        funnel_df = funnel_df.sort_values("quantity_sold", ascending=False)
        fig_funnel = go.Figure(go.Funnel(
            y=funnel_df["product_name"],
            x=funnel_df["quantity_sold"],
            textinfo="value+percent initial"
        ))
        fig_funnel.update_layout(title="Sales Funnel by Product", height=400)
        st.plotly_chart(fig_funnel, use_container_width=True)

    # Sales by Category Donut Chart
    if not df_sales.empty:
        sales_by_category = df_sales.groupby("product_name")["quantity_sold"].sum().reset_index()
        sales_by_category = sales_by_category.merge(
            df_inventory[["product_name", "category"]],
            on="product_name", how="left"
        )
        fig_donut = px.pie(
            sales_by_category, names="category", values="quantity_sold",
            title="Sales by Category", hole=0.5,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_donut.update_traces(textfont_size=16)
        st.plotly_chart(fig_donut, use_container_width=True)

    # Moving Average Sales Trend Chart
    if not df_sales.empty:
        st.markdown("#### 📈 7-Day Moving Average Sales Trend")
        df_sales["sale_date"] = pd.to_datetime(df_sales["sale_date"])
        sales_daily = df_sales.groupby("sale_date")["quantity_sold"].sum().reset_index()
        sales_daily = sales_daily.sort_values("sale_date")
        sales_daily["7d_ma"] = sales_daily["quantity_sold"].rolling(window=7, min_periods=1).mean()
        fig_ma = go.Figure()
        fig_ma.add_trace(go.Scatter(
            x=sales_daily["sale_date"], y=sales_daily["quantity_sold"],
            mode="lines+markers", name="Daily Sales", line=dict(color="#007bff")
        ))
        fig_ma.add_trace(go.Scatter(
            x=sales_daily["sale_date"], y=sales_daily["7d_ma"],
            mode="lines", name="7-Day MA", line=dict(color="#eebbc3", width=4, dash="dash")
        ))
        fig_ma.update_layout(
            title="Daily Sales and 7-Day Moving Average",
            xaxis_title="Date",
            yaxis_title="Units Sold",
            font=dict(size=18),
            height=500,
            legend=dict(font=dict(size=16))
        )
        st.plotly_chart(fig_ma, use_container_width=True)

    if "lat" in df_sales.columns and "lon" in df_sales.columns:
        st.markdown("### 🌍 Sales by Location")
        fig_map = px.scatter_mapbox(
            df_sales, lat="lat", lon="lon", color="quantity_sold",
            size="quantity_sold", hover_name="product_name",
            mapbox_style="carto-darkmatter", zoom=3,
            title="Sales Distribution Map"
        )
        st.plotly_chart(fig_map, use_container_width=True)

    st.dataframe(df_sales, use_container_width=True, height=400)
    st.download_button("⬇ Download Sales CSV", df_sales.to_csv(index=False), file_name="sales.csv")

    # --- Sales Growth Gauge in KPI section ---
    if not df_sales.empty:
        last_month = pd.to_datetime(df_sales["sale_date"]).max() - pd.DateOffset(months=1)
        sales_last_month = df_sales[pd.to_datetime(df_sales["sale_date"]) > last_month]["quantity_sold"].sum()
        sales_prev_month = df_sales[(pd.to_datetime(df_sales["sale_date"]) <= last_month) & (pd.to_datetime(df_sales["sale_date"]) > last_month - pd.DateOffset(months=1))]["quantity_sold"].sum()
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=sales_last_month,
            delta={'reference': sales_prev_month, 'increasing': {'color': "green"}, 'decreasing': {'color': "red"}},
            gauge={'axis': {'range': [None, max(sales_last_month, sales_prev_month, 1000)]}},
            title={'text': "Sales Growth (Last Month)"}
        ))
        st.plotly_chart(fig_gauge, use_container_width=True)

    if st.button("Download Sales Report as PDF"):
        pdfkit.from_string(df_sales.to_html(), "sales_report.pdf", configuration=config)
        with open("sales_report.pdf", "rb") as f:
            st.download_button("Download PDF", f, file_name="sales_report.pdf")

# --- Alerts Tab ---
with alerts_tab:
    st.subheader("🚨 Low Stock Restock Alerts")
    if not df_alerts.empty:
        styled_alerts = df_alerts.style.applymap(
            lambda v: "color: red; font-weight: bold;" if isinstance(v, (int, float)) and v < 10 else ""
        , subset=["quantity_in_stock"])
        st.dataframe(styled_alerts, use_container_width=True, height=300)

        fig_alert = px.bar(
            df_alerts, x="product_name", y="quantity_in_stock",
            color="quantity_in_stock", color_continuous_scale="Reds",
            title="Current Stock for Alerted Products"
        )
        fig_alert.update_layout(font=dict(size=14), xaxis_title="", yaxis_title="Stock", height=400)
        st.plotly_chart(fig_alert, use_container_width=True)

        st.download_button("⬇ Download Alerts CSV", df_alerts.to_csv(index=False), file_name="alerts.csv")
    else:
        st.success("No products currently need restocking! 🎉")

    if not df_alerts.empty and df_alerts["quantity_in_stock"].min() < 5:
        st.toast("🚨 Critical low stock detected!", icon="⚡")

    # Add to Alerts Tab, after low stock table
    if st.session_state.get("admin_logged_in", False) and not df_alerts.empty:
        st.markdown("### 📦 Request Restock")
        selected_products = st.multiselect(
            "Select products to request restock", df_alerts["product_name"].tolist(), key="restock_select"
        )
        if st.button("Send Restock Request"):
            st.success(f"Restock request sent for: {', '.join(selected_products)}")
            # Here you can add code to send an email or update DB

# --- Footer ---
st.markdown("---")
st.caption("Retail Inventory & Restock Monitoring App © 2025 | Developed by Your Amruth")

with open("assets/futuristic.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)



