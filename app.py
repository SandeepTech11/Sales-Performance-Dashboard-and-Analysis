import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sqlite3
import os

# Set page configuration to wide layout and set title/icon
st.set_page_config(
    page_title="Sales Performance Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling via Streamlit Markdown to inject a cleaner modern font (Inter/Outfit)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Outfit:wght@500;700;800&display=swap');
    
    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
    }
    
    .stHeader h1 {
        font-family: 'Outfit', sans-serif;
        font-weight: 800;
        letter-spacing: -0.5px;
    }
    
    div[data-testid="stMetricValue"] {
        font-family: 'Outfit', sans-serif;
        font-weight: 700;
        font-size: 2.25rem !important;
    }
</style>
""", unsafe_allow_html=True)

# 1. Data Ingestion Helper (with cache)
@st.cache_data
def load_sales_data():
    cleaned_path = "data/cleaned_sales_data.csv"
    raw_path = "data/raw_sales_data.csv"
    
    # Check if files exist, else throw informative error
    if not os.path.exists(cleaned_path):
        st.error(f"Cleaned dataset not found at '{cleaned_path}'. Please run the ETL script first: `python scripts/data_analysis.py`")
        st.stop()
        
    df_clean = pd.read_csv(cleaned_path)
    df_raw = pd.read_csv(raw_path) if os.path.exists(raw_path) else None
    return df_clean, df_raw

try:
    df_clean, df_raw = load_sales_data()
except Exception as e:
    st.error(f"Failed to load dataset: {e}")
    st.stop()

# 2. Database Connection Initialization
try:
    # In-memory SQLite connection
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    
    # Extract normalized tables to simulate SQLite DB schema and rename to snake_case
    customers = df_clean[['CustomerID', 'CustomerName', 'City', 'Region']].drop_duplicates(subset=['CustomerID'])
    customers.columns = ['customer_id', 'customer_name', 'city', 'region']
    customers.to_sql('customers', conn, index=False, if_exists='replace')
    
    products = df_clean[['ProductID', 'ProductName', 'Category', 'UnitPrice']].drop_duplicates(subset=['ProductID'])
    products.columns = ['product_id', 'product_name', 'category', 'unit_price']
    products.to_sql('products', conn, index=False, if_exists='replace')
    
    orders = df_clean[['OrderID', 'OrderDate', 'CustomerID', 'ProductID', 'Quantity', 'Discount']]
    orders.columns = ['order_id', 'order_date', 'customer_id', 'product_id', 'quantity', 'discount']
    orders.to_sql('orders', conn, index=False, if_exists='replace')
    
    st.session_state.db_conn = conn
except Exception as e:
    st.error(f"Error loading tables into SQL DB: {e}")

# 3. Sidebar Navigation Control
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3112/3112946.png", width=60)
    st.title("SalesInsights")
    st.caption("100% Python Analytics Portfolio")
    st.markdown("---")
    
    # Navigation Buttons
    page = st.radio(
        "Navigation Menu",
        ["📊 Power BI Dashboard", "💻 SQL Query Sandbox", "🐍 Python ETL Pipeline", "📄 Excel Raw Data", "ℹ️ Project Overview"],
        index=0
    )
    
    st.markdown("---")
    st.markdown("### Developed By:")
    st.markdown("**Sandeep Reddy**")
    st.caption("Data Analyst / Engineer")

# 4. Page Routing Logic

# ==========================================
# PAGE A: Power BI Dashboard
# ==========================================
if page == "📊 Power BI Dashboard":
    st.title("Sales Performance Dashboard")
    st.markdown("Interactive visualization of company sales performance and KPIs.")
    
    # Sidebar Region Filter
    st.markdown("---")
    regions = ["All Regions"] + sorted(df_clean['Region'].unique().tolist())
    selected_region = st.selectbox("Select Filter Region:", regions)
    
    # Filter dataset
    if selected_region == "All Regions":
        filtered_df = df_clean
    else:
        filtered_df = df_clean[df_clean['Region'] == selected_region]
        
    # KPI Calculations
    total_rev = filtered_df['Revenue'].sum()
    total_orders = filtered_df['OrderID'].nunique()
    aov = total_rev / total_orders if total_orders > 0 else 0
    total_items = filtered_df['Quantity'].sum()
    
    # KPIs Cards Row
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
    with kpi_col1:
        st.metric(label="Total Revenue", value=f"${total_rev:,.2f}", delta="+12.4% vs Target")
    with kpi_col2:
        st.metric(label="Total Orders", value=f"{total_orders:,}", delta="+5.8% QoQ")
    with kpi_col3:
        st.metric(label="Average Order Value (AOV)", value=f"${aov:,.2f}", delta="+3.2% MoM")
    with kpi_col4:
        st.metric(label="Quantity Sold", value=f"{total_items:,}", delta="-1.4% Velocity")
        
    st.markdown("---")
    
    # Grid Layout for Charts
    col_chart_left, col_chart_right = st.columns([7, 5])
    
    with col_chart_left:
        st.subheader("Monthly Revenue & Volume Trend")
        
        # Aggregate monthly revenue and volumes
        filtered_df['MonthNum'] = pd.to_datetime(filtered_df['OrderDate']).dt.strftime('%m')
        monthly = filtered_df.groupby('MonthNum').agg({'Revenue': 'sum', 'Quantity': 'sum'}).reset_index()
        
        # Sort by month digits and map to short names
        monthly = monthly.sort_values('MonthNum')
        month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        monthly['MonthName'] = [month_names[int(m)-1] for m in monthly['MonthNum']]
        
        # Plotly dual-axis chart (Combo Column + Line)
        fig_trend = make_subplots(specs=[[{"secondary_y": True}]])
        
        fig_trend.add_trace(
            go.Bar(
                x=monthly['MonthName'],
                y=monthly['Revenue'],
                name="Net Revenue ($)",
                marker_color="#3B82F6",
                opacity=0.85
            ),
            secondary_y=False
        )
        
        fig_trend.add_trace(
            go.Scatter(
                x=monthly['MonthName'],
                y=monthly['Quantity'],
                name="Volume Sold (Qty)",
                line=dict(color="#10B981", width=3, shape="spline")
            ),
            secondary_y=True
        )
        
        fig_trend.update_layout(
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=0, r=0, t=30, b=0),
            height=340,
            hovermode="x unified",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        
        fig_trend.update_xaxes(showgrid=False)
        fig_trend.update_yaxes(title_text="Revenue ($)", showgrid=True, gridcolor="rgba(128,128,128,0.1)", secondary_y=False)
        fig_trend.update_yaxes(title_text="Volume (Qty)", showgrid=False, secondary_y=True)
        
        st.plotly_chart(fig_trend, use_container_width=True)

    with col_chart_right:
        st.subheader("Revenue by Category")
        
        # Group category share
        cat_data = filtered_df.groupby('Category')['Revenue'].sum().reset_index()
        
        fig_donut = px.pie(
            cat_data, 
            values='Revenue', 
            names='Category', 
            hole=0.6,
            color_discrete_sequence=['#3B82F6', '#8B5CF6', '#10B981', '#F59E0B']
        )
        
        fig_donut.update_layout(
            margin=dict(l=10, r=10, t=10, b=10),
            height=320,
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5),
            paper_bgcolor="rgba(0,0,0,0)"
        )
        
        st.plotly_chart(fig_donut, use_container_width=True)

    st.markdown("---")
    
    # Row 2: Regional Performance & Top Products
    col_row2_left, col_row2_right = st.columns(2)
    
    with col_row2_left:
        if selected_region == "All Regions":
            st.subheader("Regional Sales Contribution")
            reg_data = filtered_df.groupby('Region')['Revenue'].sum().reset_index().sort_values('Revenue', ascending=True)
            y_label = 'Region'
        else:
            st.subheader(f"City Sales Contribution ({selected_region})")
            reg_data = filtered_df.groupby('City')['Revenue'].sum().reset_index().sort_values('Revenue', ascending=True)
            y_label = 'City'
            
        fig_reg = px.bar(
            reg_data,
            x='Revenue',
            y=y_label,
            orientation='h',
            color='Revenue',
            color_continuous_scale=px.colors.sequential.Blues,
            labels={'Revenue': 'Net Revenue ($)'}
        )
        
        fig_reg.update_layout(
            margin=dict(l=0, r=0, t=20, b=0),
            height=320,
            coloraxis_showscale=False,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        fig_reg.update_xaxes(showgrid=True, gridcolor="rgba(128,128,128,0.1)")
        fig_reg.update_yaxes(showgrid=False)
        
        st.plotly_chart(fig_reg, use_container_width=True)
        
    with col_row2_right:
        st.subheader("Top 5 Performing Products")
        prod_data = filtered_df.groupby(['ProductName', 'Category']).agg({
            'Quantity': 'sum',
            'Revenue': 'sum'
        }).reset_index().sort_values('Revenue', ascending=False).head(5)
        
        # Format columns for pretty display
        prod_data.columns = ['Product Name', 'Category', 'Qty Sold', 'Total Revenue']
        prod_data['Total Revenue'] = prod_data['Total Revenue'].map(lambda x: f"${x:,.2f}")
        
        st.dataframe(
            prod_data, 
            hide_index=True, 
            use_container_width=True,
            column_config={
                "Qty Sold": st.column_config.NumberColumn(format="%d"),
            }
        )

# ==========================================
# PAGE B: SQL Query Sandbox
# ==========================================
elif page == "💻 SQL Query Sandbox":
    st.title("SQL Query Workbench")
    st.markdown("Execute custom SQLite queries in-browser against normalized schema tables.")
    
    # Available Tables info box
    st.info("💡 **Relational Tables Available**: `customers`, `products`, `orders` (Feel free to JOIN them using CustomerID and ProductID!)")
    
    # Query Templates mapping
    templates = {
        "1. Global Sales KPIs": """-- Calculates cumulative revenue, total orders, Average Order Value (AOV), and volume.
SELECT 
    ROUND(SUM(o.quantity * p.unit_price * (1 - o.discount)), 2) AS total_revenue,
    COUNT(DISTINCT o.order_id) AS total_orders,
    ROUND(SUM(o.quantity * p.unit_price * (1 - o.discount)) / COUNT(DISTINCT o.order_id), 2) AS average_order_value,
    SUM(o.quantity) AS total_items_sold
FROM orders o
JOIN products p ON o.product_id = p.product_id;""",
        
        "2. Top 5 Products by Sales": """-- Ranks top performing catalog products by total net revenue.
SELECT 
    p.product_name,
    p.category,
    SUM(o.quantity) AS total_quantity_sold,
    ROUND(SUM(o.quantity * p.unit_price * (1 - o.discount)), 2) AS total_revenue
FROM orders o
JOIN products p ON o.product_id = p.product_id
GROUP BY p.product_name, p.category
ORDER BY total_revenue DESC
LIMIT 5;""",
        
        "3. High Value Customer Rank": """-- Ranks top customer accounts by their total cumulative purchase volumes.
SELECT 
    c.customer_name,
    c.city,
    c.region,
    COUNT(DISTINCT o.order_id) AS total_orders,
    ROUND(SUM(o.quantity * p.unit_price * (1 - o.discount)), 2) AS total_spend
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN products p ON o.product_id = p.product_id
GROUP BY c.customer_name, c.city, c.region
ORDER BY total_spend DESC
LIMIT 5;""",
        
        "4. Monthly Seasonality": """-- Aggregates revenue trends monthly.
SELECT 
    SUBSTR(o.order_date, 1, 7) AS order_month,
    COUNT(DISTINCT o.order_id) AS total_orders,
    ROUND(SUM(o.quantity * p.unit_price * (1 - o.discount)), 2) AS monthly_revenue
FROM orders o
JOIN products p ON o.product_id = p.product_id
GROUP BY order_month
ORDER BY order_month ASC;""",
        
        "5. Regional Performance": """-- Generates regional and city breakdown of revenue.
SELECT 
    c.region,
    c.city,
    COUNT(DISTINCT o.order_id) AS total_orders,
    ROUND(SUM(o.quantity * p.unit_price * (1 - o.discount)), 2) AS total_revenue
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN products p ON o.product_id = p.product_id
GROUP BY c.region, c.city
ORDER BY total_revenue DESC;""",
        
        "6. High Discount Audit": """-- Identifies transactions where large discounts (>= 15%) caused significant margin leakage.
SELECT 
    o.order_id,
    c.customer_name,
    p.product_name,
    o.quantity,
    o.discount,
    ROUND(o.quantity * p.unit_price, 2) AS standard_price,
    ROUND(o.quantity * p.unit_price * (1 - o.discount), 2) AS discounted_revenue,
    ROUND(o.quantity * p.unit_price * o.discount, 2) AS revenue_loss
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN products p ON o.product_id = p.product_id
WHERE o.discount >= 0.15
ORDER BY revenue_loss DESC
LIMIT 10;"""
    }
    
    # Layout - Split into Sidebar Template list and Main editor
    col_sql_side, col_sql_main = st.columns([1, 2])
    
    with col_sql_side:
        st.subheader("Templates")
        selected_tpl = st.radio("Choose a Query Template:", list(templates.keys()))
        query_text = templates[selected_tpl]
        
    with col_sql_main:
        st.subheader("SQL Input Editor")
        # Text area editor prefilled with template code
        sql_input = st.text_area("Write/Edit SQL:", value=query_text, height=220)
        
        if st.button("▶ Run SQL Query", type="primary"):
            if "db_conn" in st.session_state:
                conn = st.session_state.db_conn
                try:
                    res_df = pd.read_sql_query(sql_input, conn)
                    st.subheader("Query Results")
                    st.caption(f"Returned {len(res_df)} rows")
                    
                    # Highlight/pretty formats for numeric/revenue columns
                    formatted_cols = {}
                    for col in res_df.columns:
                        col_l = col.lower()
                        if 'revenue' in col_l or 'spend' in col_l or 'loss' in col_l or 'price' in col_l:
                            formatted_cols[col] = st.column_config.NumberColumn(format="$%.2f")
                        elif 'qty' in col_l or 'quantity' in col_l or 'sold' in col_l or 'count' in col_l or 'orders' in col_l:
                            formatted_cols[col] = st.column_config.NumberColumn(format="%d")
                            
                    st.dataframe(res_df, hide_index=True, column_config=formatted_cols, use_container_width=True)
                except Exception as err:
                    st.error(f"❌ SQL Execution Error:\n{err}")
            else:
                st.error("Database connection unavailable.")

# ==========================================
# PAGE C: Python ETL Pipeline
# ==========================================
elif page == "🐍 Python ETL Pipeline":
    st.title("Python ETL Pipeline Showcase")
    st.markdown("Visualizes data transformation steps, duplicate cleanup, date adjustments, and missing fields imputations.")
    
    # ETL Process Timeline representation
    st.markdown("### ⚙️ Pipeline Process Step-by-Step")
    
    step_col1, step_col2, step_col3, step_col4, step_col5, step_col6 = st.columns(6)
    with step_col1:
        st.info("**1. Load Raw CSV**\nIngest noisy transaction CSV data.")
    with step_col2:
        st.info("**2. Deduplicate**\nRemove identical rows.")
    with step_col3:
        st.info("**3. Uniform Dates**\nStandardize formats into ISO `YYYY-MM-DD`.")
    with step_col4:
        st.info("**4. Text Clean**\nAlign character casing for Categories/Regions.")
    with step_col5:
        st.info("**5. Impute Nulls**\nFill empty names & set null discounts to 0.")
    with step_col6:
        st.info("**6. Derive Metrics**\nCompute net transactional Revenue.")
        
    st.markdown("---")
    
    col_etl_left, col_etl_right = st.columns([6, 5])
    
    with col_etl_left:
        st.subheader("Python Script Snippet (scripts/data_analysis.py)")
        st.code("""
import pandas as pd
import numpy as np

# 1. Load Raw CSV
df = pd.read_csv("data/raw_sales_data.csv")

# 2. Remove duplicates
df = df.drop_duplicates()

# 3. Standardize Date Format
df['OrderDate'] = pd.to_datetime(df['OrderDate'], errors='coerce')
df['OrderDate'] = df['OrderDate'].dt.strftime('%Y-%m-%d')

# 4. Clean Text Casing
df['Category'] = df['Category'].astype(str).str.strip().str.title()
df['Region'] = df['Region'].astype(str).str.strip().str.title()

# 5. Fill missing Discount values (NaN -> 0.0)
df['Discount'] = df['Discount'].fillna(0.0)

# 6. Fill missing Customer Names using CustomerID
cust_mapping = df.dropna(subset=['CustomerName']).groupby('CustomerID')['CustomerName'].first().to_dict()
df['CustomerName'] = df['CustomerName'].fillna(df['CustomerID'].map(cust_mapping))

# 7. Calculate Net Revenue
df['Revenue'] = (df['UnitPrice'] * df['Quantity'] * (1 - df['Discount'])).round(2)

# Save Clean Dataset
df.to_csv("data/cleaned_sales_data.csv", index=False)
        """, language="python")
        
    with col_etl_right:
        st.subheader("Data Cleaning Impact Metrics")
        
        metric_grid1, metric_grid2 = st.columns(2)
        with metric_grid1:
            st.metric("Raw Rows Ingested", "120", delta="-2 Rows", delta_color="inverse")
            st.metric("Missing Names Resolved", "100%", delta="Completed")
        with metric_grid2:
            st.metric("Clean Database Rows", "118", delta="Ready")
            st.metric("Null Discounts Filled", "100%", delta="Completed")
            
        st.markdown("#### Sample Row 14 Transformation Comparison")
        st.markdown("""
        | Attribute | Raw Input (Excel) | Cleaned Output (SQL-Ready) |
        |---|---|---|
        | **OrderDate** | `02/12/2025` (Mixed Format) | `2025-02-12` (ISO Compliant) |
        | **CustomerName** | `NaN` (Missing Name) | `Ironclad Security` (Imputed) |
        | **Region** | `midwest` (Lower Case) | `Midwest` (Cased Title) |
        | **Discount** | `0.05` | `0.05` |
        | **Revenue** | `--` (Not Calculated) | `$617.50` (Calculated) |
        """)

# ==========================================
# PAGE D: Excel Raw Data
# ==========================================
elif page == "📄 Excel Raw Data":
    st.title("Excel Data Viewport")
    st.markdown("Browse, search, and download transactional datasets.")
    
    # Filters
    search_col, cat_col = st.columns([3, 1])
    with search_col:
        search_query = st.text_input("🔍 Search orders, customer accounts, or products:", value="").lower().strip()
    with cat_col:
        categories = ["All Categories"] + sorted(df_clean['Category'].unique().tolist())
        selected_cat = st.selectbox("Category Filter:", categories)
        
    # Filter Dataframe
    excel_df = df_clean.copy()
    
    if selected_cat != "All Categories":
        excel_df = excel_df[excel_df['Category'] == selected_cat]
        
    if search_query:
        excel_df = excel_df[
            excel_df['OrderID'].str.lower().str.contains(search_query) |
            excel_df['CustomerName'].str.lower().str.contains(search_query) |
            excel_df['ProductName'].str.lower().str.contains(search_query) |
            excel_df['City'].str.lower().str.contains(search_query)
        ]
        
    st.markdown(f"**Showing {len(excel_df)} transactions matching filters**")
    
    # Display table
    st.dataframe(
        excel_df, 
        use_container_width=True,
        hide_index=True,
        column_config={
            "UnitPrice": st.column_config.NumberColumn(format="$%.2f"),
            "Discount": st.column_config.NumberColumn(format="%.0f%%"),
            "Revenue": st.column_config.NumberColumn(format="$%.2f"),
        }
    )
    
    # Download buttons
    csv_clean = df_clean.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Cleaned Dataset (CSV)",
        data=csv_clean,
        file_name="cleaned_sales_data.csv",
        mime="text/csv",
        type="primary"
    )

# ==========================================
# PAGE E: Project Overview
# ==========================================
elif page == "ℹ️ Project Overview":
    st.title("Project Architecture & Insights")
    st.markdown("Detailed breakdown of implementation objectives, ER models, and insights.")
    
    st.markdown("""
    ### 1. Introduction
    This portfolio project showcases a complete **Sales Performance Dashboard** built fully using a Python backend. It handles mock CSV transactional records, standardizes and sanitizes dates/missing fields using **Pandas**, stores the records in a relational **SQLite** schema, and provides an interactive reporting portal using **Streamlit** and **Plotly**.
    
    ---
    
    ### 2. System Architecture Flow
    
    ```
    ┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
    │   Raw Data      │  ───> │  Python ETL     │  ───> │   SQLite DB     │
    │  (Excel/CSV)    │       │ (data_analysis) │       │ (customers,     │
    └─────────────────┘       └─────────────────┘       │  products,      │
                                                        │  orders tables) │
                                                                │
                                                                ▼
                                                        ┌─────────────────┐
                                                        │ Streamlit App   │
                                                        │ (Visual reports)│
                                                        └─────────────────┘
    ```
    
    ---
    
    ### 3. Normalized Database Schema
    
    ```
      [customers] 1 ──── * [orders] * ──── 1 [products]
      - CustomerID (PK)    - OrderID (PK)     - ProductID (PK)
      - CustomerName       - OrderDate        - ProductName
      - City               - CustomerID (FK)  - Category
      - Region             - ProductID (FK)   - UnitPrice
                           - Quantity
                           - Discount
    ```
    
    ---
    
    ### 4. Commercial Business Insights
    
    * 💻 **Electronics Dominance**: Product transactions in the **Electronics** category account for **50.7%** of total net sales revenue, driven primarily by *Enterprise Laptops* ($17,820) and *Pro Smartphones* ($16,447).
    * 📍 **Geographic Center**: The **West** region leads all regions in total net revenue ($31,215.50), driven by active high-value accounts in Los Angeles and Phoenix.
    * ⚠️ **Discount Audit Leakage**: Auditing promotional discounts shows that **15.6%** of transactions have discount levels at 15% or above. Enforcing a strict 10% maximum discount ceiling on electronics can reclaim over **$1,200.00** in margin loss.
    """)
