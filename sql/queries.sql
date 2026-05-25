-- SQL Queries for Sales Performance Analysis

-- 1. High-Level KPIs (Total Revenue, Total Orders, Average Order Value, Total Items Sold)
-- Calculates key operational metrics for business health.
SELECT 
    ROUND(SUM(o.quantity * p.unit_price * (1 - o.discount)), 2) AS total_revenue,
    COUNT(DISTINCT o.order_id) AS total_orders,
    ROUND(SUM(o.quantity * p.unit_price * (1 - o.discount)) / COUNT(DISTINCT o.order_id), 2) AS average_order_value,
    SUM(o.quantity) AS total_items_sold
FROM orders o
JOIN products p ON o.product_id = p.product_id;


-- 2. Top 5 Products by Revenue
-- Identifies best-selling products to optimize stock and marketing.
SELECT 
    p.product_id,
    p.product_name,
    p.category,
    SUM(o.quantity) AS total_quantity_sold,
    ROUND(SUM(o.quantity * p.unit_price * (1 - o.discount)), 2) AS total_revenue
FROM orders o
JOIN products p ON o.product_id = p.product_id
GROUP BY p.product_id, p.product_name, p.category
ORDER BY total_revenue DESC
LIMIT 5;


-- 3. Top 5 Customers by Revenue
-- Pinpoints high-value clients for customer retention campaigns.
SELECT 
    c.customer_id,
    c.customer_name,
    c.city,
    c.region,
    COUNT(DISTINCT o.order_id) AS total_orders,
    ROUND(SUM(o.quantity * p.unit_price * (1 - o.discount)), 2) AS total_spend
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN products p ON o.product_id = p.product_id
GROUP BY c.customer_id, c.customer_name, c.city, c.region
ORDER BY total_spend DESC
LIMIT 5;


-- 4. Monthly Revenue and Order Trend
-- Analyzes seasonality and month-over-month performance trends.
SELECT 
    strftime('%Y-%m', o.order_date) AS order_month, -- SQLite syntax. For PostgreSQL: TO_CHAR(o.order_date, 'YYYY-MM')
    COUNT(DISTINCT o.order_id) AS total_orders,
    ROUND(SUM(o.quantity * p.unit_price * (1 - o.discount)), 2) AS monthly_revenue
FROM orders o
JOIN products p ON o.product_id = p.product_id
GROUP BY order_month
ORDER BY order_month ASC;


-- 5. Sales Performance by Region & City
-- Maps geographic distribution of sales to identify regional growth opportunities.
SELECT 
    c.region,
    c.city,
    COUNT(DISTINCT o.order_id) AS total_orders,
    ROUND(SUM(o.quantity * p.unit_price * (1 - o.discount)), 2) AS total_revenue
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN products p ON o.product_id = p.product_id
GROUP BY c.region, c.city
ORDER BY total_revenue DESC;


-- 6. Product Category Breakdown
-- Summarizes sales dynamics across product segments.
SELECT 
    p.category,
    SUM(o.quantity) AS total_items_sold,
    ROUND(SUM(o.quantity * p.unit_price * (1 - o.discount)), 2) AS total_revenue,
    ROUND((SUM(o.quantity * p.unit_price * (1 - o.discount)) / 
           (SELECT SUM(o2.quantity * p2.unit_price * (1 - o2.discount)) FROM orders o2 JOIN products p2 ON o2.product_id = p2.product_id) * 100), 2) AS revenue_percentage
FROM orders o
JOIN products p ON o.product_id = p.product_id
GROUP BY p.category
ORDER BY total_revenue DESC;


-- 7. High-Discount Sales Audit (Discounts >= 15%)
-- Audits sales with high discounts to understand margin leakage.
SELECT 
    o.order_id,
    o.order_date,
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
LIMIT 10;
