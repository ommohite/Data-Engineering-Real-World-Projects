-- Test Case 9: Indexing and EXPLAIN query optimization fixture
CREATE DATABASE IF NOT EXISTS test_case_9;
USE test_case_9;

CREATE TABLE IF NOT EXISTS customers (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_name VARCHAR(100), city VARCHAR(50), email VARCHAR(150)
);
CREATE TABLE IF NOT EXISTS products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    product_name VARCHAR(100), category VARCHAR(50), price DECIMAL(10,2)
);
CREATE TABLE IF NOT EXISTS sales (
    sale_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    product_id INT NOT NULL,
    sale_date DATE NOT NULL,
    quantity INT NOT NULL,
    total_amount DECIMAL(12,2) NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

DELETE FROM sales;
DELETE FROM products;
DELETE FROM customers;
INSERT INTO customers (customer_name, city, email) VALUES
('Rahul Sharma', 'Pune', 'rahul@gmail.com'),
('Amit Patil', 'Mumbai', 'amit@gmail.com'),
('Sneha Joshi', 'Pune', 'sneha@gmail.com'),
('Priya Mehta', 'Delhi', 'priya@gmail.com'),
('Rohan Desai', 'Mumbai', 'rohan@gmail.com'),
('Neha Kulkarni', 'Bangalore', 'neha@gmail.com'),
('Karan Shah', 'Pune', 'karan@gmail.com'),
('Pooja Verma', 'Delhi', 'pooja@gmail.com'),
('Vikas Rao', 'Hyderabad', 'vikas@gmail.com'),
('Anjali Singh', 'Mumbai', 'anjali@gmail.com');
INSERT INTO products (product_name, category, price) VALUES
('Laptop', 'Electronics', 65000),
('Mouse', 'Accessories', 800),
('Keyboard', 'Accessories', 1500),
('Monitor', 'Electronics', 12000),
('Headphones', 'Accessories', 2500),
('Mobile', 'Electronics', 35000),
('Tablet', 'Electronics', 22000),
('Chair', 'Furniture', 7500),
('Desk', 'Furniture', 12000),
('USB Cable', 'Accessories', 300);
INSERT INTO sales (customer_id, product_id, sale_date, quantity, total_amount) VALUES
(1, 1, '2026-01-05', 1, 65000),
(2, 2, '2026-01-08', 2, 1600),
(3, 3, '2026-01-12', 1, 1500),
(4, 4, '2026-02-02', 2, 24000),
(5, 5, '2026-02-10', 1, 2500),
(6, 6, '2026-02-15', 1, 35000),
(7, 7, '2026-03-01', 2, 44000),
(8, 8, '2026-03-05', 1, 7500),
(9, 9, '2026-03-12', 1, 12000),
(10, 10, '2026-03-18', 5, 1500),
(1, 2, '2026-04-02', 3, 2400),
(2, 4, '2026-04-05', 1, 12000),
(3, 6, '2026-04-10', 2, 70000),
(4, 1, '2026-04-15', 1, 65000),
(5, 3, '2026-05-01', 2, 3000),
(6, 5, '2026-05-08', 2, 5000),
(7, 8, '2026-05-15', 2, 15000),
(8, 9, '2026-05-20', 1, 12000),
(9, 7, '2026-06-01', 1, 22000),
(10, 10, '2026-06-10', 10, 3000),
(1, 4, '2026-06-15', 2, 24000),
(2, 6, '2026-07-01', 1, 35000),
(3, 1, '2026-07-05', 1, 65000),
(4, 2, '2026-07-12', 4, 3200),
(5, 7, '2026-08-01', 1, 22000),
(6, 3, '2026-08-10', 3, 4500),
(7, 5, '2026-08-15', 1, 2500),
(8, 6, '2026-09-01', 1, 35000),
(9, 1, '2026-09-10', 2, 130000),
(10, 4, '2026-09-15', 1, 12000);

CREATE INDEX idx_sales_customer_id ON sales(customer_id);
CREATE INDEX idx_sales_product_id ON sales(product_id);
CREATE INDEX idx_products_price ON products(price);

EXPLAIN ANALYZE
SELECT product_name FROM products WHERE price > 20000;
