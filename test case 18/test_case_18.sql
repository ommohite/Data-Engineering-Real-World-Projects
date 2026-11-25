CREATE DATABASE IF NOT EXISTS aggregation_test;
USE aggregation_test;

DROP TABLE IF EXISTS sales;

CREATE TABLE sales (
    sale_id INT PRIMARY KEY,
    sale_date DATE NOT NULL,
    region VARCHAR(50) NOT NULL,
    product_id INT NOT NULL,
    customer_id INT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    total_amount DECIMAL(12,2) NOT NULL
);

INSERT INTO sales (
    sale_id,
    sale_date,
    region,
    product_id,
    customer_id,
    quantity,
    unit_price,
    total_amount
)
WITH digits AS (
    SELECT 0 AS n UNION ALL SELECT 1 UNION ALL SELECT 2
    UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5
    UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8
    UNION ALL SELECT 9
),
numbers AS (
    SELECT
        a.n + (b.n * 10) + (c.n * 100) + (d.n * 1000) + (e.n * 10000) AS n
    FROM digits AS a
    CROSS JOIN digits AS b
    CROSS JOIN digits AS c
    CROSS JOIN digits AS d
    CROSS JOIN digits AS e
)
SELECT
    n + 1,
    DATE_ADD('2023-01-01', INTERVAL MOD(n, 1461) DAY),
    CASE MOD(n, 5)
        WHEN 0 THEN 'North'
        WHEN 1 THEN 'South'
        WHEN 2 THEN 'East'
        WHEN 3 THEN 'West'
        ELSE 'Central'
    END,
    MOD(n, 100) + 1,
    MOD(n, 10000) + 1,
    MOD(n, 10) + 1,
    MOD(n, 500) + 100,
    (MOD(n, 10) + 1) * (MOD(n, 500) + 100)
FROM numbers
WHERE n < 100000;
