CREATE TABLE customer (
    cust_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_name VARCHAR(100),
    customer_email VARCHAR(100),
    update_on DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

INSERT INTO customer (customer_name, customer_email)
VALUES
('Rahul Sharma', 'rahul@gmail.com'),
('Priya Patel', 'priya@gmail.com'),
('Amit Verma', 'amit@gmail.com'),
('Sneha Joshi', 'sneha@gmail.com'),
('Rohan Mehta', 'rohan@gmail.com'),
('Neha Kulkarni', 'neha@gmail.com'),
('Vikas Singh', 'vikas@gmail.com'),
('Anjali Deshmukh', 'anjali@gmail.com'),
('Karan Shah', 'karan@gmail.com'),
('Pooja Gupta', 'pooja@gmail.com');
