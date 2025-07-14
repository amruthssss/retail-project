import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
from datetime import datetime, timedelta
import random
import os

# --- DB CONFIG (adjust as needed) ---
DB_USER = 'root'
DB_PASSWORD = os.getenv("DB_PASSWORD", "Amruth%408050")
DB_NAME = 'retail_system'
DB_HOST = '34.93.172.75'
DB_PORT = 3306

engine = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

# --- Sample Products ---
products = [
    {"product_name": "Wireless Mouse", "category": "Electronics", "supplier_name": "TechWare", "unit_price": 599.99, "reorder_level": 20},
    {"product_name": "LED Bulb 9W", "category": "Lighting", "supplier_name": "BrightLite", "unit_price": 89.50, "reorder_level": 50},
    {"product_name": "Notebook A5", "category": "Stationery", "supplier_name": "OfficeMart", "unit_price": 45.00, "reorder_level": 100},
    {"product_name": "Desk Chair", "category": "Furniture", "supplier_name": "HomeComfort", "unit_price": 3499.00, "reorder_level": 10},
    {"product_name": "Bluetooth Speaker", "category": "Electronics", "supplier_name": "SoundMax", "unit_price": 1299.00, "reorder_level": 15},
    {"product_name": "Table Lamp", "category": "Lighting", "supplier_name": "BrightLite", "unit_price": 499.00, "reorder_level": 30},
    {"product_name": "Gel Pen", "category": "Stationery", "supplier_name": "OfficeMart", "unit_price": 15.00, "reorder_level": 200},
    {"product_name": "Office Desk", "category": "Furniture", "supplier_name": "HomeComfort", "unit_price": 5999.00, "reorder_level": 5},
    {"product_name": "USB-C Cable", "category": "Electronics", "supplier_name": "TechWare", "unit_price": 199.00, "reorder_level": 40},
    {"product_name": "Sticky Notes", "category": "Stationery", "supplier_name": "OfficeMart", "unit_price": 25.00, "reorder_level": 150},
    {"product_name": "Floor Lamp", "category": "Lighting", "supplier_name": "BrightLite", "unit_price": 1299.00, "reorder_level": 20},
    {"product_name": "Bookshelf", "category": "Furniture", "supplier_name": "HomeComfort", "unit_price": 2499.00, "reorder_level": 8},
]

# --- Insert Products (if not already present) ---
with engine.begin() as conn:
    for prod in products:
        conn.execute(
            text("""
                INSERT IGNORE INTO products (product_name, category, supplier_name, unit_price, reorder_level)
                VALUES (:product_name, :category, :supplier_name, :unit_price, :reorder_level)
            """), prod
        )

# --- Get product IDs ---
df_products = pd.read_sql("SELECT product_id, product_name FROM products", engine)
product_map = {row['product_name']: row['product_id'] for _, row in df_products.iterrows()}

# --- Inventory (random initial stock) ---
with engine.begin() as conn:
    for prod in products:
        conn.execute(
            text("""
                INSERT IGNORE INTO inventory (product_id, quantity_in_stock)
                VALUES (:product_id, :quantity_in_stock)
            """),
            {"product_id": product_map[prod["product_name"]], "quantity_in_stock": random.randint(50, 200)}
        )

# --- Generate 2 years of sales data ---
start_date = datetime.now() - timedelta(days=730)
end_date = datetime.now()
date_range = pd.date_range(start=start_date, end=end_date, freq='D')

sales_data = []
for single_date in date_range:
    for prod in products:
        # Randomly decide if there was a sale that day
        if random.random() < 0.7:  # 70% chance of a sale per product per day
            sales_data.append({
                "product_id": product_map[prod["product_name"]],
                "quantity_sold": random.randint(1, 10),
                "sale_date": single_date.strftime('%Y-%m-%d')
            })

# --- Insert sales data in batches ---
batch_size = 1000
with engine.begin() as conn:
    for i in range(0, len(sales_data), batch_size):
        batch = sales_data[i:i+batch_size]
        conn.execute(
            text("""
                INSERT INTO sales (product_id, quantity_sold, sale_date)
                VALUES (:product_id, :quantity_sold, :sale_date)
            """),
            batch
        )

# --- After inserting sales data, simulate restock alerts ---
with engine.begin() as conn:
    for prod in products:
        product_id = product_map[prod["product_name"]]
        # Get current stock
        result = conn.execute(
            text("SELECT quantity_in_stock FROM inventory WHERE product_id = :pid"),
            {"pid": product_id}
        ).fetchone()
        if result and result[0] < prod["reorder_level"]:
            conn.execute(
                text("""
                    INSERT INTO restock_alerts (product_id, quantity_in_stock, threshold, sent_at, alert_sent)
                    VALUES (:product_id, :quantity_in_stock, :threshold, NOW(), TRUE)
                """),
                {
                    "product_id": product_id,
                    "quantity_in_stock": result[0],
                    "threshold": prod["reorder_level"]
                }
            )

print(f"Inserted {len(sales_data)} sales records for 2 years.")