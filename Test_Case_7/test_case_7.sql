CREATE DATABASE IF NOT EXISTS test_case_7;
USE test_case_7;

CREATE TABLE IF NOT EXISTS customers (
    customer_id INT PRIMARY KEY,
    customer_name VARCHAR(100),
    email VARCHAR(100),
    city VARCHAR(50),
    region VARCHAR(50),
    registration_date DATE
);

CREATE TABLE IF NOT EXISTS products (
    product_id INT PRIMARY KEY,
    product_name VARCHAR(100),
    category VARCHAR(50),
    unit_price DECIMAL(10, 2),
    stock_quantity INT
);

CREATE TABLE IF NOT EXISTS sales (
    sale_id INT PRIMARY KEY,
    customer_id INT,
    product_id INT,
    sale_date DATE,
    quantity INT,
    total_amount DECIMAL(12, 2),
    payment_status VARCHAR(30),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

INSERT INTO customers VALUES
(1, 'Rahul Sharma', 'rahul@gmail.com', 'Pune', 'West', '2023-01-15'),
(2, 'Amit Verma', 'amit@gmail.com', 'Delhi', 'North', '2023-02-20'),
(3, 'Priya Patel', 'priya@gmail.com', 'Mumbai', 'West', '2023-03-10'),
(4, 'Sneha Desai', 'sneha@gmail.com', 'Bangalore', 'South', '2023-04-05'),
(5, 'Karan Mehta', 'karan@gmail.com', 'Jaipur', 'North', '2023-05-12'),
(6, 'Neha Singh', 'neha@gmail.com', 'Chennai', 'South', '2023-06-18'),
(7, 'Rohan Kulkarni', 'rohan@gmail.com', 'Nagpur', 'Central', '2023-07-22'),
(8, 'Ananya Rao', 'ananya@gmail.com', 'Hyderabad', 'South', '2023-08-14'),
(9, 'Vikram Joshi', 'vikram@gmail.com', 'Nashik', 'West', '2023-09-01'),
(10, 'Pooja Shah', 'pooja@gmail.com', 'Ahmedabad', 'West', '2023-10-11');

INSERT INTO products VALUES
(101, 'Laptop', 'Electronics', 65000, 20),
(102, 'Smartphone', 'Electronics', 25000, 50),
(103, 'Headphones', 'Accessories', 2500, 100),
(104, 'Keyboard', 'Accessories', 1500, 80),
(105, 'Office Chair', 'Furniture', 8500, 30),
(106, 'Study Table', 'Furniture', 12000, 15),
(107, 'Monitor', 'Electronics', 18000, 25),
(108, 'Mouse', 'Accessories', 800, 120),
(109, 'Printer', 'Electronics', 15000, 10),
(110, 'Bookshelf', 'Furniture', 5500, 0),
(111, 'Webcam', 'Accessories', 3500, 40),
(112, 'Tablet', 'Electronics', 30000, 18);

INSERT INTO sales VALUES
(1001, 1, 101, '2024-01-05', 1, 65000, 'Completed'),
(1002, 2, 102, '2024-01-10', 2, 50000, 'Completed'),
(1003, 3, 103, '2024-01-15', 3, 7500, 'Completed'),
(1004, 4, 105, '2024-02-02', 1, 8500, 'Pending'),
(1005, 5, 107, '2024-02-10', 2, 36000, 'Completed'),
(1006, 6, 104, '2024-02-15', 4, 6000, 'Completed'),
(1007, 7, 106, '2024-03-01', 1, 12000, 'Cancelled'),
(1008, 8, 108, '2024-03-05', 5, 4000, 'Completed'),
(1009, 9, 109, '2024-03-12', 1, 15000, 'Pending'),
(1010, 10, 110, '2024-03-20', 2, 11000, 'Completed'),
(1011, 1, 102, '2024-04-02', 1, 25000, 'Completed'),
(1012, 2, 103, '2024-04-08', 2, 5000, 'Completed'),
(1013, 3, 107, '2024-04-15', 1, 18000, 'Completed'),
(1014, 4, 101, '2024-05-01', 1, 65000, 'Pending'),
(1015, 5, 108, '2024-05-10', 10, 8000, 'Completed'),
(1016, 6, 112, '2024-05-18', 1, 30000, 'Completed'),
(1017, 7, 111, '2024-06-02', 2, 7000, 'Completed'),
(1018, 8, 105, '2024-06-10', 1, 8500, 'Completed'),
(1019, 9, 104, '2024-06-15', 3, 4500, 'Cancelled'),
(1020, 10, 109, '2024-06-20', 2, 30000, 'Completed'),
(1021, 1, 107, '2024-07-01', 2, 36000, 'Completed'),
(1022, 2, 106, '2024-07-05', 1, 12000, 'Pending'),
(1023, 3, 101, '2024-07-12', 1, 65000, 'Completed'),
(1024, 4, 108, '2024-07-18', 4, 3200, 'Completed'),
(1025, 5, 112, '2024-08-01', 2, 60000, 'Completed'),
(1026, 6, 103, '2024-08-10', 2, 5000, 'Pending'),
(1027, 7, 102, '2024-08-15', 1, 25000, 'Completed'),
(1028, 8, 111, '2024-08-20', 3, 10500, 'Completed'),
(1029, 9, 105, '2024-09-05', 2, 17000, 'Completed'),
(1030, 10, 101, '2024-09-15', 1, 65000, 'Completed');
