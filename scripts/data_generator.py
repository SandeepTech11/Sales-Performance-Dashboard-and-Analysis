import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import os

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

def generate_dirty_sales_data(num_rows=1000):
    # Customer Data
    customers = [
        {"CustomerID": f"CUST{i:03d}", "CustomerName": name, "City": city, "Region": region}
        for i, (name, city, region) in enumerate([
            ("TechCorp Solutions", "New York", "East"),
            ("Apex Global", "Los Angeles", "West"),
            ("Quantum Systems", "Chicago", "Midwest"),
            ("Summit Enterprise", "Houston", "South"),
            ("Nova Industries", "Phoenix", "West"),
            ("Vanguard Labs", "Philadelphia", "East"),
            ("Horizon Retail", "San Antonio", "South"),
            ("Infinity Partners", "San Diego", "West"),
            ("Pinnacle Group", "Dallas", "South"),
            ("Centurion Ltd", "San Jose", "West"),
            ("Starlight Co", "Austin", "South"),
            ("BlueSky Ventures", "Jacksonville", "South"),
            ("Redwood Logistics", "San Francisco", "West"),
            ("Ironclad Security", "Indianapolis", "Midwest"),
            ("AeroTech Dynamics", "Columbus", "Midwest"),
            ("Velocity Commerce", "Fort Worth", "South"),
            ("NextGen Media", "Charlotte", "East"),
            ("Silverline Group", "Seattle", "West"),
            ("Beacon Services", "Denver", "West"),
            ("Zephyr Tech", "El Paso", "South")
        ], start=1)
    ]
    
    # Product Data
    products = [
        {"ProductID": "PROD001", "ProductName": "Enterprise Laptop", "Category": "Electronics", "UnitPrice": 1200.00},
        {"ProductID": "PROD002", "ProductName": "Pro Smartphone", "Category": "Electronics", "UnitPrice": 850.00},
        {"ProductID": "PROD003", "ProductName": "Ultra Tablet", "Category": "Electronics", "UnitPrice": 450.00},
        {"ProductID": "PROD004", "ProductName": "Ergonomic Office Chair", "Category": "Furniture", "UnitPrice": 350.00},
        {"ProductID": "PROD005", "ProductName": "Standing Desk", "Category": "Furniture", "UnitPrice": 650.00},
        {"ProductID": "PROD006", "ProductName": "Noise-Cancelling Headphones", "Category": "Accessories", "UnitPrice": 200.00},
        {"ProductID": "PROD007", "ProductName": "Mechanical Keyboard", "Category": "Accessories", "UnitPrice": 120.00},
        {"ProductID": "PROD008", "ProductName": "4K UltraHD Monitor", "Category": "Electronics", "UnitPrice": 400.00},
        {"ProductID": "PROD009", "ProductName": "Wireless Laser Printer", "Category": "Office Supplies", "UnitPrice": 250.00},
        {"ProductID": "PROD010", "ProductName": "Smart Office Whiteboard", "Category": "Office Supplies", "UnitPrice": 180.00}
    ]
    
    start_date = datetime(2025, 1, 1)
    end_date = datetime(2025, 12, 31)
    date_range = (end_date - start_date).days
    
    data = []
    
    for i in range(1, num_rows + 1):
        order_id = f"ORD{i:05d}"
        
        # Select random customer and product
        cust = random.choice(customers)
        prod = random.choice(products)
        
        # Random date
        random_days = random.randint(0, date_range)
        order_date_obj = start_date + timedelta(days=random_days)
        
        # Introduce inconsistent date formatting (some MM/DD/YYYY, some YYYY-MM-DD)
        if random.random() < 0.15:
            order_date = order_date_obj.strftime("%m/%d/%Y")
        else:
            order_date = order_date_obj.strftime("%Y-%m-%d")
            
        quantity = random.randint(1, 8)
        
        # Introduce missing values in discount (NaN)
        if random.random() < 0.12:
            discount = np.nan
        else:
            discount = random.choice([0.0, 0.05, 0.10, 0.15, 0.20])
            
        # Inconsistent casing for category and region
        category = prod["Category"]
        if random.random() < 0.08:
            category = category.upper() if random.random() < 0.5 else category.lower()
            
        region = cust["Region"]
        if random.random() < 0.08:
            region = region.lower() if random.random() < 0.5 else region.upper()
            
        row = {
            "OrderID": order_id,
            "OrderDate": order_date,
            "CustomerID": cust["CustomerID"],
            "CustomerName": cust["CustomerName"] if random.random() > 0.03 else np.nan, # Introduce missing customer names
            "City": cust["City"],
            "Region": region,
            "ProductID": prod["ProductID"],
            "ProductName": prod["ProductName"],
            "Category": category,
            "UnitPrice": prod["UnitPrice"],
            "Quantity": quantity,
            "Discount": discount
        }
        data.append(row)
        
    df = pd.DataFrame(data)
    
    # Add duplicate rows (about 2%)
    duplicates = df.sample(n=int(num_rows * 0.02), replace=True)
    df = pd.concat([df, duplicates], ignore_index=True)
    
    # Shuffle dataset
    df = df.sample(frac=1).reset_index(drop=True)
    
    return df

if __name__ == "__main__":
    # Create data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    
    print("Generating dirty sales dataset...")
    df_raw = generate_dirty_sales_data(1200)
    
    raw_path = "data/raw_sales_data.csv"
    df_raw.to_csv(raw_path, index=False)
    print(f"Dirty sales dataset saved to '{raw_path}' with {len(df_raw)} records.")
