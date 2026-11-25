CREATE DATABASE IF NOT EXISTS multitenant_db;
USE multitenant_db;

CREATE TABLE tenants (
    tenant_id INT PRIMARY KEY AUTO_INCREMENT,
    tenant_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO tenants (tenant_name) VALUES
('ABC Electronics'),
('XYZ Retail'),
('Global Stores'),
('Tech Solutions');

CREATE TABLE customers (
    customer_id INT AUTO_INCREMENT,
    tenant_id INT NOT NULL,
    customer_name VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (customer_id),
    CONSTRAINT uq_customer_tenant UNIQUE (tenant_id, customer_id),
    CONSTRAINT fk_customers_tenant FOREIGN KEY (tenant_id)
        REFERENCES tenants(tenant_id)
);

INSERT INTO customers (tenant_id, customer_name, email) VALUES
(1, 'Rahul Sharma', 'rahul@abc.com'),
(1, 'Amit Verma', 'amit@abc.com'),
(1, 'Priya Singh', 'priya@abc.com'),
(2, 'John Smith', 'john@xyz.com'),
(2, 'Emily Brown', 'emily@xyz.com'),
(3, 'Michael Lee', 'michael@global.com'),
(3, 'Sarah Wilson', 'sarah@global.com'),
(4, 'David Miller', 'david@techsolutions.com');

CREATE TABLE products (
    product_id INT AUTO_INCREMENT,
    tenant_id INT NOT NULL,
    product_name VARCHAR(100) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (product_id),
    CONSTRAINT uq_product_tenant UNIQUE (tenant_id, product_id),
    CONSTRAINT fk_products_tenant FOREIGN KEY (tenant_id)
        REFERENCES tenants(tenant_id)
);

INSERT INTO products (tenant_id, product_name, price) VALUES
(1, 'Laptop', 75000.00),
(1, 'Mouse', 1200.00),
(1, 'Keyboard', 2500.00),
(1, 'Monitor', 18000.00),
(1, 'Headphones', 5000.00),
(2, 'Smartphone', 45000.00),
(2, 'Tablet', 30000.00),
(2, 'Power Bank', 2500.00),
(2, 'Smart Watch', 12000.00),
(2, 'Earbuds', 4000.00),
(3, 'Gaming Laptop', 95000.00),
(3, 'Gaming Mouse', 3000.00),
(3, 'Gaming Keyboard', 5000.00),
(3, 'Gaming Monitor', 25000.00),
(3, 'Gaming Headset', 8000.00),
(4, 'Server', 150000.00),
(4, 'Router', 10000.00),
(4, 'SSD', 8000.00),
(4, 'RAM', 6000.00),
(4, 'Network Switch', 20000.00);

CREATE TABLE orders (
    order_id INT AUTO_INCREMENT,
    tenant_id INT NOT NULL,
    customer_id INT NOT NULL,
    order_date DATE NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    PRIMARY KEY (order_id),
    CONSTRAINT fk_orders_tenant FOREIGN KEY (tenant_id)
        REFERENCES tenants(tenant_id),
    CONSTRAINT fk_orders_customer_tenant FOREIGN KEY (tenant_id, customer_id)
        REFERENCES customers(tenant_id, customer_id)
);

INSERT INTO orders (tenant_id, customer_id, order_date, total_amount) VALUES
(1, 1, '2026-11-10', 1500.00),
(1, 2, '2026-11-11', 2500.00),
(1, 3, '2026-11-12', 800.00),
(1, 1, '2026-11-15', 75000.00),
(2, 4, '2026-11-10', 3000.00),
(2, 5, '2026-11-12', 1200.00),
(2, 4, '2026-11-15', 45000.00),
(3, 6, '2026-11-11', 5000.00),
(3, 7, '2026-11-13', 2200.00),
(3, 6, '2026-11-16', 95000.00),
(4, 8, '2026-11-14', 4500.00),
(4, 8, '2026-11-17', 150000.00);

CREATE INDEX idx_orders_tenant_date ON orders (tenant_id, order_date);
CREATE INDEX idx_customers_tenant_name ON customers (tenant_id, customer_name);
CREATE INDEX idx_products_tenant_name ON products (tenant_id, product_name);

SELECT t.tenant_id, t.tenant_name, SUM(o.total_amount) AS total_revenue
FROM tenants AS t
LEFT JOIN orders AS o ON t.tenant_id = o.tenant_id
GROUP BY t.tenant_id, t.tenant_name
ORDER BY total_revenue DESC;
