CREATE DATABASE IF NOT EXISTS test_case_14;
USE test_case_14;

CREATE TABLE customers (
    customer_id INT PRIMARY KEY,
    customer_name VARCHAR(100),
    city VARCHAR(50),
    signup_date DATE
);

CREATE TABLE products (
    product_id INT PRIMARY KEY,
    product_name VARCHAR(100),
    category VARCHAR(50),
    price DECIMAL(10,2)
);

CREATE TABLE orders (
    order_id INT PRIMARY KEY,
    customer_id INT,
    product_id INT,
    order_date DATETIME,
    quantity INT,
    total_amount DECIMAL(10,2),
    order_status VARCHAR(30),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

CREATE TABLE daily_sales_analytics (
    sales_date DATE,
    city VARCHAR(50),
    category VARCHAR(50),
    total_orders INT,
    total_quantity INT,
    total_revenue DECIMAL(15,2),
    average_order_value DECIMAL(15,2),
    batch_timestamp DATETIME,
    PRIMARY KEY (sales_date, city, category)
);

INSERT INTO customers VALUES
(1, 'Rahul Sharma', 'Pune', '2025-01-10'),
(2, 'Amit Verma', 'Mumbai', '2025-02-15'),
(3, 'Priya Patil', 'Pune', '2025-03-20'),
(4, 'Sneha Joshi', 'Nashik', '2025-04-05'),
(5, 'Karan Mehta', 'Mumbai', '2025-05-12'),
(6, 'Neha Kulkarni', 'Pune', '2025-06-18'),
(7, 'Rohan Desai', 'Delhi', '2025-07-22'),
(8, 'Anjali Shah', 'Nashik', '2025-08-30');

INSERT INTO products VALUES
(101, 'Laptop', 'Electronics', 55000),
(102, 'Mouse', 'Electronics', 800),
(103, 'Keyboard', 'Electronics', 1500),
(104, 'Office Chair', 'Furniture', 7500),
(105, 'Desk', 'Furniture', 12000),
(106, 'Headphones', 'Electronics', 2500),
(107, 'Notebook', 'Stationery', 100),
(108, 'Pen Set', 'Stationery', 250);

INSERT INTO orders VALUES
(1001, 1, 101, '2026-11-01 10:30:00', 1, 55000, 'Completed'),
(1002, 2, 102, '2026-11-01 11:15:00', 2, 1600, 'Completed'),
(1003, 3, 104, '2026-11-02 09:20:00', 1, 7500, 'Completed'),
(1004, 1, 106, '2026-11-02 14:10:00', 2, 5000, 'Completed'),
(1005, 4, 105, '2026-11-03 12:00:00', 1, 12000, 'Pending'),
(1006, 5, 103, '2026-11-03 15:30:00', 1, 1500, 'Completed'),
(1007, 6, 101, '2026-11-04 16:45:00', 1, 55000, 'Completed'),
(1008, 2, 108, '2026-11-04 17:10:00', 3, 750, 'Completed'),
(1009, 7, 107, '2026-11-05 13:25:00', 5, 500, 'Cancelled'),
(1010, 8, 104, '2026-11-05 18:00:00', 2, 15000, 'Completed'),
(1011, 3, 102, '2026-11-06 10:00:00', 3, 2400, 'Completed'),
(1012, 1, 103, '2026-11-06 11:30:00', 2, 3000, 'Completed'),
(1013, 5, 106, '2026-11-07 12:45:00', 1, 2500, 'Pending'),
(1014, 6, 108, '2026-11-07 14:20:00', 4, 1000, 'Completed'),
(1015, 4, 101, '2026-11-08 16:00:00', 1, 55000, 'Completed'),
(1016, 7, 105, '2026-11-08 17:30:00', 1, 12000, 'Completed'),
(1017, 8, 107, '2026-11-09 09:45:00', 10, 1000, 'Completed'),
(1018, 2, 104, '2026-11-09 13:15:00', 1, 7500, 'Completed'),
(1019, 3, 106, '2026-11-10 15:00:00', 2, 5000, 'Completed'),
(1020, 1, 105, '2026-11-10 18:30:00', 1, 12000, 'Completed');

SELECT * FROM daily_sales_analytics;
