import pandas as pd
import numpy as np
import json
import os

def clean_and_analyze_sales_data():
    raw_path = "data/raw_sales_data.csv"
    clean_path = "data/cleaned_sales_data.csv"
    summary_path = "data/sales_summary.json"
    
    if not os.path.exists(raw_path):
        print(f"Error: {raw_path} not found. Please run data_generator.py first.")
        return
        
    print(f"Loading raw data from '{raw_path}'...")
    df = pd.read_csv(raw_path)
    initial_rows = len(df)
    print(f"Initial row count: {initial_rows}")
    
    # 1. Remove duplicates
    df = df.drop_duplicates()
    duplicates_removed = initial_rows - len(df)
    print(f"Removed {duplicates_removed} duplicate rows.")
    
    # 2. Standardize Date Format
    # OrderDate might have mixed formats. Convert all to datetime, then to YYYY-MM-DD string.
    df['OrderDate'] = pd.to_datetime(df['OrderDate'], errors='coerce')
    # Drop rows where date couldn't be parsed (if any)
    df = df.dropna(subset=['OrderDate'])
    df['OrderDate'] = df['OrderDate'].dt.strftime('%Y-%m-%d')
    
    # 3. Clean Text Casing (Category and Region)
    # Standardize categories to Title case (e.g. 'electronics' -> 'Electronics')
    df['Category'] = df['Category'].astype(str).str.strip().str.title()
    # Standardize region to Title case (e.g. 'east' -> 'East')
    df['Region'] = df['Region'].astype(str).str.strip().str.title()
    
    # 4. Fill missing Discount values (NaN -> 0.0)
    missing_discounts = df['Discount'].isna().sum()
    df['Discount'] = df['Discount'].fillna(0.0)
    print(f"Filled {missing_discounts} missing discount values with 0.0.")
    
    # 5. Handle missing Customer Names
    # Map CustomerID to their most frequent CustomerName in the dataset
    cust_mapping = df.dropna(subset=['CustomerName']).groupby('CustomerID')['CustomerName'].first().to_dict()
    # Apply mapping to fill missing names
    missing_names_before = df['CustomerName'].isna().sum()
    df['CustomerName'] = df['CustomerName'].fillna(df['CustomerID'].map(cust_mapping))
    # If any still missing (unlikely, but safe check), fill with "Unknown Customer"
    df['CustomerName'] = df['CustomerName'].fillna("Unknown Customer")
    print(f"Resolved {missing_names_before} missing customer names using ID mapping.")
    
    # 6. Calculate Revenue
    # Revenue = (UnitPrice * Quantity) * (1 - Discount)
    df['Revenue'] = (df['UnitPrice'] * df['Quantity'] * (1 - df['Discount'])).round(2)
    
    # Save cleaned sales data
    df.to_csv(clean_path, index=False)
    print(f"Cleaned dataset saved to '{clean_path}' with {len(df)} records.")
    
    # 7. Perform Basic Analysis and Generate Summary JSON
    print("\n--- Sales Performance Summary ---")
    total_revenue = float(df['Revenue'].sum())
    total_orders = int(df['OrderID'].nunique())
    avg_order_value = float(df.groupby('OrderID')['Revenue'].sum().mean())
    total_items_sold = int(df['Quantity'].sum())
    
    print(f"Total Revenue: ${total_revenue:,.2f}")
    print(f"Total Orders: {total_orders:,}")
    print(f"Average Order Value: ${avg_order_value:,.2f}")
    print(f"Total Items Sold: {total_items_sold:,}")
    
    # Top Products
    top_products = df.groupby('ProductName').agg(
        Revenue=('Revenue', 'sum'),
        QuantitySold=('Quantity', 'sum')
    ).round(2).sort_values(by='Revenue', ascending=False).head(5).reset_index().to_dict(orient='records')
    
    # Top Customers
    top_customers = df.groupby('CustomerName').agg(
        Revenue=('Revenue', 'sum'),
        OrdersCount=('OrderID', 'nunique')
    ).round(2).sort_values(by='Revenue', ascending=False).head(5).reset_index().to_dict(orient='records')
    
    # Regional Sales
    regional_sales = df.groupby('Region').agg(
        Revenue=('Revenue', 'sum'),
        QuantitySold=('Quantity', 'sum')
    ).round(2).reset_index().to_dict(orient='records')
    
    # Category Sales
    category_sales = df.groupby('Category').agg(
        Revenue=('Revenue', 'sum'),
        QuantitySold=('Quantity', 'sum')
    ).round(2).reset_index().to_dict(orient='records')
    
    # Monthly Sales Trend
    df['Month'] = pd.to_datetime(df['OrderDate']).dt.strftime('%m-%b')
    monthly_sales = df.groupby(['Month']).agg(
        Revenue=('Revenue', 'sum'),
        OrdersCount=('OrderID', 'nunique')
    ).round(2).sort_index().reset_index().to_dict(orient='records')
    
    summary = {
        "kpis": {
            "total_revenue": total_revenue,
            "total_orders": total_orders,
            "avg_order_value": round(avg_order_value, 2),
            "total_items_sold": total_items_sold
        },
        "top_products": top_products,
        "top_customers": top_customers,
        "regional_sales": regional_sales,
        "category_sales": category_sales,
        "monthly_sales": monthly_sales
    }
    
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=4)
    print(f"Summary JSON saved to '{summary_path}'")

if __name__ == "__main__":
    clean_and_analyze_sales_data()
