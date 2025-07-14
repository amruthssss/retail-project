import streamlit as st
import pandas as pd
from db import insert_or_update_product, get_product_by_id

def admin_panel():
    st.subheader("🛠 Admin Panel: Add/Update Product")

    # --- CSV Upload Section ---
    st.markdown("### 📤 Bulk Upload Products via CSV")
    csv_file = st.file_uploader("Upload CSV", type=["csv"])
    if csv_file is not None:
        df_csv = pd.read_csv(csv_file)
        st.dataframe(df_csv)
        if st.button("Import CSV"):
            for idx, row in df_csv.iterrows():
                try:
                    insert_or_update_product(
                        product_id=int(row["product_id"]) if not pd.isna(row.get("product_id", None)) else None,
                        name=row["name"],
                        category=row["category"],
                        supplier=row["supplier"],
                        price=row["price"],
                        reorder_level=row["reorder_level"],
                        quantity=row["quantity"]
                    )
                except Exception as e:
                    st.error(f"Row {idx+1} failed: {e}")
            st.success("CSV imported successfully!")

    # --- Manual Add/Update Section (your existing form) ---
    with st.form("product_form"):
        prod_id = st.text_input("Product ID (leave blank to insert new)")
        name = st.text_input("Name")
        category = st.text_input("Category")
        supplier = st.text_input("Supplier")
        price = st.number_input("Price", min_value=0.0, format="%.2f")
        reorder_level = st.number_input("Reorder Level", min_value=0, step=1)
        quantity = st.number_input("Quantity", min_value=0, step=1)
        submitted = st.form_submit_button("Submit")

    if submitted:
        if name and category and supplier:
            pid = int(prod_id) if prod_id.strip() else None
            insert_or_update_product(
                product_id=pid,
                name=name,
                category=category,
                supplier=supplier,
                price=price,
                reorder_level=reorder_level,
                quantity=quantity
            )
            st.success("✅ Product inserted/updated successfully!")

            # Fetch and display updated product
            if pid:
                last_product = get_product_by_id(pid)
                if last_product is not None and not last_product.empty:
                    st.success("🟢 Last Change Applied:")
                    st.dataframe(last_product, use_container_width=True)
                    qty = last_product.iloc[0].get("quantity_in_stock", None)
                    pname = last_product.iloc[0].get("product_name", name)
                    if qty is not None and qty < 10:
                        st.warning(f"⚠️ Low stock alert: Only {qty} units left for '{pname}'!")
        else:
            st.error("❌ Please fill all required fields (Name, Category, Supplier)")
