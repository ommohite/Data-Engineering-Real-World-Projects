CREATE DATABASE test_case_12;

USE test_case_12;

CREATE TABLE customers (
    customer_id INT PRIMARY KEY,
    customer_name VARCHAR(100),
    city VARCHAR(50),
    signup_date DATE
);

CREATE TABLE orders (
    order_id INT PRIMARY KEY,
    customer_id INT,
    order_date DATE,
    total_amount DECIMAL(10,2),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

INSERT INTO customers
(customer_id, customer_name, city, signup_date)
VALUES
(101, 'Rahul Sharma', 'Pune', '2024-01-10'),
(102, 'Amit Verma', 'Mumbai', '2024-02-15'),
(103, 'Priya Patel', 'Pune', '2024-03-20'),
(104, 'Sneha Joshi', 'Nashik', '2024-04-05'),
(105, 'Rohan Mehta', 'Mumbai', '2024-05-12'),
(106, 'Neha Singh', 'Pune', '2024-06-18'),
(107, 'Karan Shah', 'Delhi', '2024-07-22'),
(108, 'Pooja Desai', 'Nashik', '2024-08-30'),
(109, 'Arjun Rao', 'Mumbai', '2024-09-14'),
(110, 'Ananya Kulkarni', 'Pune', '2024-10-01');

INSERT INTO orders
(order_id, customer_id, order_date, total_amount)
VALUES
(1, 101, '2026-11-18', 5000),
(2, 101, '2026-11-10', 4500),
(3, 101, '2026-10-25', 6000),
(4, 101, '2026-10-05', 5500),
(5, 101, '2026-09-15', 7000),
(6, 102, '2026-11-15', 2000),
(7, 102, '2026-10-20', 2500),
(8, 102, '2026-09-10', 1800),
(9, 102, '2026-08-05', 2200),
(10, 103, '2026-11-17', 500),
(11, 103, '2026-07-12', 700),
(12, 104, '2026-03-01', 3000),
(13, 104, '2026-02-10', 2500),
(14, 105, '2026-06-10', 12000),
(15, 105, '2026-05-15', 15000),
(16, 105, '2026-04-20', 10000),
(17, 105, '2026-03-25', 13000),
(18, 106, '2026-11-19', 800),
(19, 107, '2026-09-01', 1500),
(20, 107, '2026-05-01', 2000),
(21, 108, '2025-06-10', 900),
(22, 108, '2025-04-15', 1200),
(23, 109, '2026-11-16', 400),
(24, 109, '2026-11-12', 350),
(25, 109, '2026-11-05', 450),
(26, 109, '2026-10-28', 300),
(27, 109, '2026-10-15', 500),
(28, 110, '2026-11-01', 2500);

SELECT * FROM RFM;
