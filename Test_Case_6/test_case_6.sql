CREATE DATABASE IF NOT EXISTS test_case_6;
USE test_case_6;

CREATE TABLE IF NOT EXISTS sales (
    sale_id INT PRIMARY KEY,
    sale_date DATE NOT NULL,
    region VARCHAR(50),
    category VARCHAR(50),
    revenue DECIMAL(10, 2) NOT NULL
);

INSERT INTO sales (sale_id, sale_date, region, category, revenue) VALUES
-- 2024 Data (North Region)
(1, '2024-01-15', 'North', 'Electronics', 12000.00),
(2, '2024-02-18', 'North', 'Electronics', 13500.00),
(3, '2024-03-20', 'North', 'Electronics', 11000.00),
(4, '2024-04-12', 'North', 'Electronics', 15000.00),
(5, '2024-05-25', 'North', 'Electronics', 16500.00),
(6, '2024-06-14', 'North', 'Electronics', 18000.00),
-- 2024 Data (South Region)
(7, '2024-01-10', 'South', 'Electronics', 9500.00),
(8, '2024-02-22', 'South', 'Electronics', 10200.00),
(9, '2024-03-19', 'South', 'Electronics', 11800.00),
(10, '2024-04-15', 'South', 'Electronics', 11200.00),
(11, '2024-05-28', 'South', 'Electronics', 13000.00),
(12, '2024-06-30', 'South', 'Electronics', 14500.00),
-- 2025 Data (North Region)
(13, '2025-01-14', 'North', 'Electronics', 14400.00),
(14, '2025-02-17', 'North', 'Electronics', 15000.00),
(15, '2025-03-21', 'North', 'Electronics', 16200.00),
(16, '2025-04-11', 'North', 'Electronics', 15800.00),
(17, '2025-05-24', 'North', 'Electronics', 19000.00),
(18, '2025-06-15', 'North', 'Electronics', 21600.00),
-- 2025 Data (South Region)
(19, '2025-01-12', 'South', 'Electronics', 10450.00),
(20, '2025-02-20', 'South', 'Electronics', 11500.00),
(21, '2025-03-18', 'South', 'Electronics', 12000.00),
(22, '2025-04-16', 'South', 'Electronics', 13400.00),
(23, '2025-05-27', 'South', 'Electronics', 14200.00),
(24, '2025-06-29', 'South', 'Electronics', 16000.00);
