-- Test Case 8: Monthly sales pivot fixture
CREATE DATABASE IF NOT EXISTS test_case_8;
USE test_case_8;

CREATE TABLE IF NOT EXISTS sales (
    sale_id INT PRIMARY KEY AUTO_INCREMENT,
    product_name VARCHAR(100),
    category VARCHAR(50),
    sale_date DATE,
    quantity INT,
    unit_price DECIMAL(10,2),
    total_amount DECIMAL(12,2)
);

DELETE FROM sales;
INSERT INTO sales (product_name, category, sale_date, quantity, unit_price, total_amount)
VALUES
('Laptop', 'Electronics', '2025-01-05', 2, 55000, 110000),
('Mobile', 'Electronics', '2025-01-10', 3, 20000, 60000),
('Chair', 'Furniture', '2025-01-12', 5, 3000, 15000),
('Table', 'Furniture', '2025-01-18', 2, 7000, 14000),
('Shirt', 'Clothing', '2025-01-20', 10, 800, 8000),
('Jeans', 'Clothing', '2025-01-25', 5, 1500, 7500),
('Laptop', 'Electronics', '2025-02-03', 1, 55000, 55000),
('Mobile', 'Electronics', '2025-02-08', 4, 20000, 80000),
('Chair', 'Furniture', '2025-02-11', 3, 3000, 9000),
('Table', 'Furniture', '2025-02-15', 4, 7000, 28000),
('Shirt', 'Clothing', '2025-02-19', 8, 800, 6400),
('Jeans', 'Clothing', '2025-02-23', 6, 1500, 9000),
('Laptop', 'Electronics', '2025-03-04', 3, 55000, 165000),
('Mobile', 'Electronics', '2025-03-09', 2, 20000, 40000),
('Chair', 'Furniture', '2025-03-13', 6, 3000, 18000),
('Table', 'Furniture', '2025-03-17', 3, 7000, 21000),
('Shirt', 'Clothing', '2025-03-21', 12, 800, 9600),
('Jeans', 'Clothing', '2025-03-26', 4, 1500, 6000),
('Laptop', 'Electronics', '2025-04-02', 2, 55000, 110000),
('Mobile', 'Electronics', '2025-04-07', 5, 20000, 100000),
('Chair', 'Furniture', '2025-04-12', 4, 3000, 12000),
('Table', 'Furniture', '2025-04-16', 5, 7000, 35000),
('Shirt', 'Clothing', '2025-04-20', 7, 800, 5600),
('Jeans', 'Clothing', '2025-04-25', 8, 1500, 12000);
