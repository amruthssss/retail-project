import streamlit as st

light_css = """
[data-testid="stSidebar"] {
    background-color: #f4f6fb !important;
}
.stSelectbox, .stDateInput, .stTextInput, .stNumberInput, .stMultiSelect, .stSlider, .stButton>button {
    background-color: #fff !important;
    color: #222 !important;
}
.stDateInput input, .stTextInput input, .stNumberInput input {
    background-color: #fff !important;
    color: #222 !important;
    border: 1px solid #007bff !important;
}
.stDateInput label, .stSelectbox label, .stTextInput label, .stNumberInput label {
    color: #222 !important;
}
.stDateInput [data-baseweb="input"] {
    background-color: #fff !important;
    color: #222 !important;
}
.stDateInput [data-baseweb="calendar"] {
    background-color: #fff !important;
    color: #222 !important;
}
.stDateInput [data-baseweb="calendar"] * { 
    color: #222 !important;
}
"""

dark_css = """
    <style>
        html, body, .stApp {{
            font-size: 20px !important;
            font-family: 'Segoe UI', 'Arial', sans-serif !important;
            background-color: #232946 !important;
            color: #fff !important;
        }}
        h1, h2, h3, h4, h5, h6 {{
            font-size: 2.2rem !important;
            font-weight: 800 !important;
            letter-spacing: 0.5px;
            color: #fff !important;
        }}
        .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {{
            font-size: 2rem !important;
            font-weight: 700 !important;
            color: #fff !important;
        }}
        .stMetric {{
            font-size: 2.2rem !important;
            font-weight: 700 !important;
            color: #fff !important;
        }}
        .block-container .stMetric {{
            background: #232946 !important;
            border-radius: 22px;
            box-shadow: 0 4px 24px rgba(0,0,0,0.18);
            padding: 36px 0 28px 0;
            margin-bottom: 28px;
            font-size: 2.2rem !important;
            border: 2px solid #eebbc3;
            transition: box-shadow 0.2s;
        }}
        .block-container .stMetric:hover {{
            box-shadow: 0 8px 32px rgba(238,187,195,0.18);
            border-color: #007bff;
        }}
        .stTabs [data-baseweb="tab-list"] {{
            gap: 32px !important;
        }}
        .stTabs [data-baseweb="tab"] {{
            font-size: 1.4rem !important;
            padding: 18px 40px !important;
            border-radius: 16px 16px 0 0 !important;
            background: #232946 !important;
            color: #fff !important;
            border: 2px solid #eebbc3 !important;
            margin-right: 8px;
            transition: background 0.2s, color 0.2s;
        }}
        .stTabs [data-baseweb="tab"]:hover {{
            background: #eebbc3 !important;
            color: #232946 !important;
        }}
        .stTabs [aria-selected="true"] {{
            background: #eebbc3 !important;
            color: #232946 !important;
            font-weight: 700 !important;
        }}
        .stSidebar {{
            background: #232946 !important;
            border-radius: 18px !important;
            box-shadow: 0 4px 24px rgba(0,0,0,0.18);
            padding: 24px 18px !important;
        }}
        .stSidebar .st-expanderHeader {{
            font-size: 1.4rem !important;
            padding: 18px 0 !important;
            color: #eebbc3 !important;
        }}
        .stSelectbox, .stDateInput, .stTextInput, .stNumberInput, .stMultiSelect, .stSlider, .stButton>button {{
            min-height: 56px !important;
            font-size: 1.25rem !important;
            padding: 16px 22px !important;
            border-radius: 14px !important;
            margin-bottom: 24px !important;
            background: #181d2f !important;
            color: #fff !important;
            border: 2px solid #eebbc3 !important;
            box-shadow: 0 2px 8px rgba(0,0,0,0.10);
            transition: border 0.2s, box-shadow 0.2s;
        }}
        .stSelectbox:focus, .stDateInput:focus, .stTextInput:focus, .stNumberInput:focus, .stMultiSelect:focus {{
            border: 2px solid #007bff !important;
            box-shadow: 0 4px 16px rgba(0,123,255,0.10);
        }}
        .stDateInput input, .stTextInput input, .stNumberInput input {{
            min-height: 48px !important;
            font-size: 1.2rem !important;
            padding: 12px 18px !important;
            border-radius: 10px !important;
            background: #232946 !important;
            color: #fff !important;
            border: 2px solid #eebbc3 !important;
        }}
        .stDateInput label, .stSelectbox label, .stTextInput label, .stNumberInput label {{
            color: #eebbc3 !important;
            font-size: 1.1rem !important;
            font-weight: 600 !important;
        }}
        .stDateInput [data-baseweb="input"] {{
            background-color: #232946 !important;
            color: #fff !important;
        }}
        .stDateInput [data-baseweb="calendar"] {{
            background-color: #232946 !important;
            color: #fff !important;
        }}
        .stDateInput [data-baseweb="calendar"] * {{
            color: #fff !important;
        }}
        /* Inventory cards grid */
        .inventory-card {{
            background: #181d2f;
            border: 2.5px solid #eebbc3;
            border-radius: 22px;
            box-shadow: 0 4px 24px rgba(238,187,195,0.10);
            padding: 32px 18px 28px 18px;
            margin-bottom: 28px;
            min-height: 260px;
            display: flex;
            flex-direction: column;
            align-items: center;
            transition: box-shadow 0.2s, border 0.2s;
        }}
        .inventory-card:hover {{
            box-shadow: 0 8px 32px rgba(238,187,195,0.18);
            border-color: #007bff;
        }}
        .inventory-card img {{
            max-width: 160px;
            max-height: 160px;
            margin-bottom: 18px;
            border-radius: 16px;
            background: #232946;
            border: 2px solid #eebbc3;
        }}
        .inventory-card .product-title {{
            font-size: 1.35rem;
            font-weight: bold;
            margin-bottom: 8px;
            text-align: center;
            color: #eebbc3;
        }}
        .inventory-card .product-category {{
            color: #007bff;
            font-size: 1.15rem;
            margin-bottom: 8px;
            text-align: center;
            font-weight: 600;
        }}
        .inventory-card .product-stock {{
            font-size: 1.15rem;
            margin-bottom: 4px;
            text-align: center;
            color: #fff;
        }}
        /* DataFrame/Table */
        .stDataFrame, .stTable {{
            font-size: 1.15rem !important;
            background: #181d2f !important;
            color: #fff !important;
            border-radius: 14px !important;
            border: 2px solid #eebbc3 !important;
            box-shadow: 0 2px 12px rgba(238,187,195,0.10);
        }}
        /* Download buttons */
        .stDownloadButton > button {{
            font-size: 1.2rem !important;
            padding: 14px 32px !important;
            border-radius: 12px !important;
            background: #eebbc3 !important;
            color: #232946 !important;
            font-weight: 700 !important;
            border: none !important;
            margin-top: 18px !important;
            transition: background 0.2s, color 0.2s;
        }}
        .stDownloadButton > button:hover {{
            background: #007bff !important;
            color: #fff !important;
        }}
        /* Floating Action Button */
        .fab {{
            position: fixed;
            bottom: 40px;
            right: 40px;
            background: #007bff;
            color: white;
            border-radius: 50%;
            width: 70px;
            height: 70px;
            font-size: 2.5rem;
            text-align: center;
            line-height: 70px;
            box-shadow: 2px 2px 18px #888;
            z-index: 100;
            cursor: pointer;
            transition: background 0.2s;
        }}
        .fab:hover {{
            background: #eebbc3;
            color: #232946;
        }}
        /* Responsive adjustments */
        @media (max-width: 900px) {{
            html, body, .stApp {{ font-size: 16px !important; }}
            .stTabs [data-baseweb="tab"] {{ font-size: 1rem !important; padding: 8px 12px !important; }}
            .inventory-card img {{ max-width: 100px; max-height: 100px; }}
            .inventory-card {{ padding: 12px 6px 10px 6px; }}
        }}
    </style>
"""

def apply_theme(theme):
    if theme == "Light":
        st.markdown(f"<style>{light_css}</style>", unsafe_allow_html=True)
    else:
        st.markdown(dark_css, unsafe_allow_html=True)

def apply_custom_theme():
    dark_css = """
    ...your dark_css string here...
    """
    st.markdown(dark_css, unsafe_allow_html=True)