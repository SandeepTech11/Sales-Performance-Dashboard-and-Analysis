# Sales Performance Dashboard and Analysis

An end-to-end sales intelligence and data engineering portfolio project built completely in **100% Python**. The project ingests raw transactional data (Excel/CSV), sanitizes it via a Python ETL pipeline, loads it into an in-memory SQL database, executes analytical SQL audits, and presents interactive visual reports using **Streamlit** and **Plotly** (no HTML, CSS, or JavaScript required).

---

## 🌟 Key Features

1. **Python ETL Data Cleaning**: Sanitizes mixed date formats, resolves title casing mismatches, imputes missing customer names, fills empty discount values, and eliminates duplicate entries using `pandas`.
2. **Relational Database Modeling**: Automatically transitions flat transactional records into a normalized 3-table relational schema (`customers`, `products`, `orders`) inside an in-memory SQLite database.
3. **Interactive Python Dashboard**: Visualizes net revenue, order volume, Average Order Value (AOV), monthly seasonality, category splits, and geographic regions. Includes dynamic sidebar selectors to filter metrics instantly.
4. **SQL Query Workbench**: An interactive SQL sandbox directly in the application interface. Run pre-loaded analytical query templates or write custom SQL scripts to query tables using SQLite syntax.
5. **Excel Transaction Explorer**: Browse, search, filter, and paginate the cleaned transaction database using a built-in search index, with an option to download the filtered dataset as a CSV.
6. **Unified Architecture Showcase**: Integrates the Python ETL pipeline metrics, code snippets, visual comparison cards, and system architecture details.

---

## 📂 Project Structure

```text
├── .streamlit/
│   └── config.toml               # Streamlit custom dark mode appearance settings
├── data/
│   ├── raw_sales_data.csv        # Dirty transaction records simulating manual Excel entries
│   └── cleaned_sales_data.csv    # Deduplicated, normalized outputs from Python ETL
├── scripts/
│   ├── data_generator.py         # Python generator scripting dirty entries (duplicates, missing, casing)
│   └── data_analysis.py          # Python ETL processor parsing, cleaning, and calculating data
├── sql/
│   ├── schema.sql                # Relational DDL tables definition with primary/foreign keys
│   └── queries.sql               # Prepared analytical queries auditing margins, top products, trends
├── app.py                        # 100% Python Streamlit dashboard & SQL Query Sandbox app
└── README.md                     # System documentation & insights overview
```

---

## 🛠️ Tech Stack & Setup

- **Backend & GUI Framework**: Python 3.9+ (Streamlit)
- **Data Wrangling & ETL**: Pandas, Numpy
- **Database Engine**: SQLite3 (Standard Python Library)
- **Data Visualizations**: Plotly Express, Plotly Graph Objects

### Local Installation & Execution

To run the data generation, ETL pipeline, and interactive dashboard locally on your machine:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/SandeepTech11/Sales-Performance-Dashboard-and-Analysis.git
   cd "Sales Performance Dashboard and Analysis"
   ```

2. **Install requirements**:
   Install the required libraries using pip:
   ```bash
   pip install pandas numpy streamlit plotly
   ```

3. **Generate & Clean Data** (Optional - pre-generated data is included):
   Run the raw generator followed by the cleaning ETL script:
   ```bash
   python scripts/data_generator.py
   python scripts/data_analysis.py
   ```

4. **Launch the Dashboard**:
   Start the local Streamlit web server:
   ```bash
   streamlit run app.py
   ```
   *This will automatically launch the dashboard in your default browser at `http://localhost:8501`.*

---

## 📊 Database Schema (Entity-Relationship)

The SQL workbench creates the following relational database schema:

```text
       ┌───────────────┐                  ┌──────────────┐
       │   customers   │                  │   products   │
       ├───────────────┤                  ├──────────────┤
       │ customer_id   │──┐            ┌──│ product_id   │
       │ customer_name │  │            │  │ product_name │
       │ city          │  │            │  │ category     │
       │ region        │  │            │  │ unit_price   │
       └───────────────┘  │            │  └──────────────┘
                           │            │
                         1 │            │ 1
                           │            │
                           ▼            ▼
                        * ┌──────────────┐ *
                          │    orders    │
                          ├──────────────┤
                          │ order_id     │
                          │ order_date   │
                          │ customer_id  │ (FK)
                          │ product_id   │ (FK)
                          │ quantity     │
                          │ discount     │
                          └──────────────┘
```

---

## 💡 Key Analytical Findings

- **Core Revenue Generator**: Product sales in the **Electronics** category account for **50.7%** of cumulative company revenues, led by *Enterprise Laptops* ($17,820.00) and *Pro Smartphones* ($16,447.50).
- **Geographic Center**: The **West** region leads all regions in total net revenue ($31,215.50), closely followed by active hubs in New York (East) and San Antonio (South).
- **Margin Recoveries**: Auditing promotional discounts revealed that **15.6%** of transactions have discount levels at 15% or above. Enforcing a strict 10% maximum discount ceiling on electronics can reclaim over **$1,200.00** in margin loss.
