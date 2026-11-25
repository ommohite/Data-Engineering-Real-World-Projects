# Author: Om Mohite
# Test Case 9: Python export of the corresponding Jupyter notebook.
# Run from this folder; configure DB_PASSWORD/DB_USER/DB_HOST/DB_PORT as needed.

import os
from pathlib import Path
from getpass import getpass

try:
    from IPython.display import display
except ImportError:
    display = print

from sqlalchemy import URL, create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

db_password = os.getenv("DB_PASSWORD")
if not db_password:
    raise ValueError("Set DB_PASSWORD in your .env file.")

server_url = URL.create(
    drivername="mysql+pymysql",
    username=os.getenv("DB_USER", "root"),
    password=db_password,
    host=os.getenv("DB_HOST", "localhost"),
    port=int(os.getenv("DB_PORT", "3306")),
)

server_engine = create_engine(server_url, pool_pre_ping=True)

with server_engine.begin() as conn:
    conn.execute(text("CREATE DATABASE IF NOT EXISTS test_case_9"))

server_engine.dispose()
print("Database test_case_9 is ready.")

# %%

# Author: Om Mohite

import os
import pandas as pd
from sqlalchemy import URL, create_engine, text
from dotenv import load_dotenv

load_dotenv()

db_password = os.getenv("DB_PASSWORD")
if not db_password:
    raise ValueError("Set DB_PASSWORD in your .env file before running this cell.")

connection_url = URL.create(
    drivername="mysql+pymysql",
    username=os.getenv("DB_USER", "root"),
    password=db_password,
    host=os.getenv("DB_HOST", "localhost"),
    port=int(os.getenv("DB_PORT", "3306")),
    database="test_case_9",
)

engine = create_engine(connection_url, pool_pre_ping=True)

with engine.connect() as conn:
    print("Connected to test_case_9")
    print("Tables:", conn.execute(text("SHOW TABLES")).fetchall())

# %%

# Author: Om Mohite

from sqlalchemy import text

customers = [
    ("Rahul Sharma", "Pune", "rahul@gmail.com"),
    ("Amit Patil", "Mumbai", "amit@gmail.com"),
    ("Sneha Joshi", "Pune", "sneha@gmail.com"),
    ("Priya Mehta", "Delhi", "priya@gmail.com"),
    ("Rohan Desai", "Mumbai", "rohan@gmail.com"),
    ("Neha Kulkarni", "Bangalore", "neha@gmail.com"),
    ("Karan Shah", "Pune", "karan@gmail.com"),
    ("Pooja Verma", "Delhi", "pooja@gmail.com"),
    ("Vikas Rao", "Hyderabad", "vikas@gmail.com"),
    ("Anjali Singh", "Mumbai", "anjali@gmail.com"),
]

products = [
    ("Laptop", "Electronics", 65000),
    ("Mouse", "Accessories", 800),
    ("Keyboard", "Accessories", 1500),
    ("Monitor", "Electronics", 12000),
    ("Headphones", "Accessories", 2500),
    ("Mobile", "Electronics", 35000),
    ("Tablet", "Electronics", 22000),
    ("Chair", "Furniture", 7500),
    ("Desk", "Furniture", 12000),
    ("USB Cable", "Accessories", 300),
]

sales = [
    (1, 1, "2026-01-05", 1, 65000),
    (2, 2, "2026-01-08", 2, 1600),
    (3, 3, "2026-01-12", 1, 1500),
    (4, 4, "2026-02-02", 2, 24000),
    (5, 5, "2026-02-10", 1, 2500),
    (6, 6, "2026-02-15", 1, 35000),
    (7, 7, "2026-03-01", 2, 44000),
    (8, 8, "2026-03-05", 1, 7500),
    (9, 9, "2026-03-12", 1, 12000),
    (10, 10, "2026-03-18", 5, 1500),
    (1, 2, "2026-04-02", 3, 2400),
    (2, 4, "2026-04-05", 1, 12000),
    (3, 6, "2026-04-10", 2, 70000),
    (4, 1, "2026-04-15", 1, 65000),
    (5, 3, "2026-05-01", 2, 3000),
    (6, 5, "2026-05-08", 2, 5000),
    (7, 8, "2026-05-15", 2, 15000),
    (8, 9, "2026-05-20", 1, 12000),
    (9, 7, "2026-06-01", 1, 22000),
    (10, 10, "2026-06-10", 10, 3000),
    (1, 4, "2026-06-15", 2, 24000),
    (2, 6, "2026-07-01", 1, 35000),
    (3, 1, "2026-07-05", 1, 65000),
    (4, 2, "2026-07-12", 4, 3200),
    (5, 7, "2026-08-01", 1, 22000),
    (6, 3, "2026-08-10", 3, 4500),
    (7, 5, "2026-08-15", 1, 2500),
    (8, 6, "2026-09-01", 1, 35000),
    (9, 1, "2026-09-10", 2, 130000),
    (10, 4, "2026-09-15", 1, 12000),
]

with engine.begin() as conn:
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS customers (
            customer_id INT PRIMARY KEY AUTO_INCREMENT,
            customer_name VARCHAR(100),
            city VARCHAR(100),
            email VARCHAR(150)
        )
    """))

    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS products (
            product_id INT PRIMARY KEY AUTO_INCREMENT,
            product_name VARCHAR(100),
            category VARCHAR(100),
            price DECIMAL(10,2)
        )
    """))

    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS sales (
            sale_id INT PRIMARY KEY AUTO_INCREMENT,
            customer_id INT,
            product_id INT,
            sale_date DATE,
            quantity INT,
            total_amount DECIMAL(10,2),
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
            FOREIGN KEY (product_id) REFERENCES products(product_id)
        )
    """))

    conn.execute(text("DELETE FROM sales"))
    conn.execute(text("DELETE FROM customers"))
    conn.execute(text("DELETE FROM products"))

    conn.execute(
        text("""
            INSERT INTO customers (customer_name, city, email)
            VALUES (:name, :city, :email)
        """),
        [{"name": name, "city": city, "email": email}
         for name, city, email in customers],
    )

    conn.execute(
        text("""
            INSERT INTO products (product_name, category, price)
            VALUES (:name, :category, :price)
        """),
        [{"name": name, "category": category, "price": price}
         for name, category, price in products],
    )

    conn.execute(
        text("""
            INSERT INTO sales
            (customer_id, product_id, sale_date, quantity, total_amount)
            VALUES (:customer_id, :product_id, :sale_date, :quantity, :total_amount)
        """),
        [
            {
                "customer_id": customer_id,
                "product_id": product_id,
                "sale_date": sale_date,
                "quantity": quantity,
                "total_amount": total_amount,
            }
            for customer_id, product_id, sale_date, quantity, total_amount in sales
        ],
    )

with engine.connect() as conn:
    for table_name in ["customers", "products", "sales"]:
        count = conn.execute(
            text(f"SELECT COUNT(*) FROM {table_name}")
        ).scalar_one()
        print(f"{table_name}: {count} rows")

# %%

# Author: Om Mohite

with engine.connect() as conn:
    plan = pd.read_sql(
        text("""
            EXPLAIN ANALYZE
            SELECT product_name
            FROM products
            WHERE price > 20000
        """),
        conn,
    )

display(plan)

# %%

# Author: Om Mohite

from sqlalchemy import inspect

join_query = """
    SELECT
        c.customer_id,
        p.product_id,
        s.sale_date,
        s.quantity,
        s.total_amount
    FROM customers AS c
    JOIN sales AS s
        ON c.customer_id = s.customer_id
    JOIN products AS p
        ON p.product_id = s.product_id
"""

existing_indexes = inspect(engine).get_indexes("sales")
indexed_columns = {
    index["column_names"][0]
    for index in existing_indexes
    if index.get("column_names")
}

with engine.begin() as conn:
    if "customer_id" not in indexed_columns:
        conn.exec_driver_sql(
            "CREATE INDEX idx_sales_customer_id ON sales(customer_id)"
        )
        print("Created index on sales.customer_id")
    else:
        print("Index already exists on sales.customer_id")

    if "product_id" not in indexed_columns:
        conn.exec_driver_sql(
            "CREATE INDEX idx_sales_product_id ON sales(product_id)"
        )
        print("Created index on sales.product_id")
    else:
        print("Index already exists on sales.product_id")

with engine.connect() as conn:
    join_plan = pd.read_sql(
        text("EXPLAIN ANALYZE " + join_query),
        conn,
    )

    join_results = pd.read_sql(
        text(join_query),
        conn,
    )

print("JOIN rows:", len(join_results))
display(join_plan)
display(join_results.head())

# %%

# Author: Om Mohite

with engine.connect() as conn:
    index_rows = conn.execute(text("""
        SELECT
            INDEX_NAME,
            COLUMN_NAME,
            SEQ_IN_INDEX
        FROM information_schema.statistics
        WHERE table_schema = DATABASE()
          AND table_name = 'sales'
        ORDER BY INDEX_NAME, SEQ_IN_INDEX
    """)).fetchall()

    counts = {
        table_name: conn.execute(
            text(f"SELECT COUNT(*) FROM {table_name}")
        ).scalar_one()
        for table_name in ["customers", "products", "sales"]
    }

print("Sales table indexes:")
for row in index_rows:
    print(row)

print("Table row counts:", counts)
print("JOIN result rows:", len(join_results))

assert counts == {"customers": 10, "products": 10, "sales": 30}
assert len(join_results) == 30
assert {"customer_id", "product_id", "sale_date", "quantity", "total_amount"}.issubset(
    join_results.columns
)

print("TEST CASE 9 INDEXING AND JOIN VALIDATION PASSED")
