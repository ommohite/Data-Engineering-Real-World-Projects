CREATE DATABASE IF NOT EXISTS test_case_16;
USE test_case_16;

CREATE TABLE sales (
    sale_id INT,
    customer_id INT,
    product_id INT,
    order_date DATE,
    quantity INT,
    unit_price DECIMAL(10,2),
    total_amount DECIMAL(10,2)
);

CREATE TABLE data_quality_issues (
    issue_id INT AUTO_INCREMENT PRIMARY KEY,
    pipeline_name VARCHAR(100),
    table_name VARCHAR(100),
    rule_name VARCHAR(100),
    severity VARCHAR(20),
    failed_records INT,
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'OPEN'
);

INSERT INTO sales
(sale_id, customer_id, product_id, order_date, quantity, unit_price, total_amount)
VALUES
(101, 1, 501, '2026-11-01', 2, 500.00, 1000.00),
(102, 2, 502, '2026-11-02', 1, 250.00, 250.00),
(103, 3, 503, '2026-11-03', 5, 100.00, 500.00),
(104, 4, 504, '2026-11-04', 3, 200.00, 600.00),
(105, 5, 505, '2026-11-05', 4, 150.00, 600.00),
(106, NULL, 506, '2026-11-06', 2, 300.00, 600.00),
(107, 7, 507, NULL, 3, 100.00, 300.00),
(108, 8, 508, '2026-11-08', NULL, 100.00, 300.00),
(109, 9, 509, '2026-11-09', 2, NULL, 200.00),
(110, 10, 510, '2026-11-10', 2, 100.00, NULL),
(111, 11, 511, '2026-11-11', -2, 100.00, -200.00),
(112, 12, 512, '2026-11-12', 0, 200.00, 0.00),
(113, 13, 513, '2026-11-13', 3, -100.00, -300.00),
(114, 14, 514, '2026-11-14', 2, 100.00, 500.00),
(115, 15, 515, '2026-11-15', 4, 250.00, 900.00),
(116, 16, 516, '2026-11-16', 1, 100.00, 100.00),
(116, 17, 517, '2026-11-17', 2, 150.00, 300.00),
(118, NULL, 518, NULL, -1, -50.00, 100.00);
