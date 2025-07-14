import unittest
from db import validate_sales_data, get_inventory_data, get_sales_data

class TestValidation(unittest.TestCase):
    def test_negative_quantity(self):
        with self.assertRaises(ValueError):
            validate_sales_data([{"product_id": 1, "quantity_sold": -5, "sale_date": "2025-06-01"}])

    def test_missing_product_id(self):
        with self.assertRaises(ValueError):
            validate_sales_data([{"product_id": None, "quantity_sold": 5, "sale_date": "2025-06-01"}])

    def test_inventory_data(self):
        df = get_inventory_data()
        self.assertIn("product_name", df.columns)

    def test_sales_data(self):
        df = get_sales_data()
        self.assertIn("sale_date", df.columns)

if __name__ == "__main__":
    unittest.main()