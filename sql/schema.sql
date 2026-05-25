-- SQL Database Schema for Sales Performance Dashboard and Analysis
-- Supported by PostgreSQL, MySQL, and SQLite

-- 1. Customers Table
CREATE TABLE IF NOT EXISTS customers (
    customer_id VARCHAR(10) PRIMARY KEY,
    customer_name VARCHAR(100) NOT NULL,
    city VARCHAR(50) NOT NULL,
    region VARCHAR(20) NOT NULL
);

-- 2. Products Table
CREATE TABLE IF NOT EXISTS products (
    product_id VARCHAR(10) PRIMARY KEY,
    product_name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL CHECK (unit_price >= 0)
);

-- 3. Orders Table
CREATE TABLE IF NOT EXISTS orders (
    order_id VARCHAR(10),
    order_date DATE NOT NULL,
    customer_id VARCHAR(10),
    product_id VARCHAR(10),
    quantity INT NOT NULL CHECK (quantity > 0),
    discount DECIMAL(3, 2) DEFAULT 0.00 CHECK (discount >= 0.00 AND discount <= 1.00),
    PRIMARY KEY (order_id, product_id), -- Composite primary key in case of multiple products per order
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
);

-- Indexing for performance optimization
CREATE INDEX idx_orders_date ON orders(order_date);
CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_orders_product ON orders(product_id);
CREATE INDEX idx_customers_region ON customers(region);
