# Author: Om Mohite
# Test Case 7: Python export of the corresponding Jupyter notebook.
# Run from this folder; configure DB_PASSWORD/DB_USER/DB_HOST/DB_PORT as needed.

import os
from pathlib import Path
from getpass import getpass

try:
    from IPython.display import display
except ImportError:
    display = print

# Author: Om Mohite

import os
from pathlib import Path
from getpass import getpass

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import URL, create_engine, text

# Find and load the existing .env file
env_file = None

for folder in [Path.cwd(), *Path.cwd().parents]:
    candidates = [
        folder / ".env",
        folder / "Data-Engineering-Real-World-Projects" / ".env",
    ]

    for candidate in candidates:
        if candidate.exists():
            env_file = candidate
            break

    if env_file:
        load_dotenv(env_file)
        break

db_password = os.getenv("DB_PASSWORD") or getpass("MySQL password: ")

# Connect to MySQL server
server_url = URL.create(
    drivername="mysql+pymysql",
    username=os.getenv("DB_USER", "root"),
    password=db_password,
    host=os.getenv("DB_HOST", "localhost"),
    port=int(os.getenv("DB_PORT", "3306")),
)

server_engine = create_engine(server_url, pool_pre_ping=True)

with server_engine.begin() as conn:
    conn.execute(text("CREATE DATABASE IF NOT EXISTS test_case_7"))

engine = create_engine(
    server_url.set(database="test_case_7"),
    pool_pre_ping=True,
)

create_table_statements = [
    """
    CREATE TABLE IF NOT EXISTS customers (
        customer_id INT PRIMARY KEY,
        customer_name VARCHAR(100),
        email VARCHAR(100),
        city VARCHAR(50),
        region VARCHAR(50),
        registration_date DATE
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS products (
        product_id INT PRIMARY KEY,
        product_name VARCHAR(100),
        category VARCHAR(50),
        unit_price DECIMAL(10, 2),
        stock_quantity INT
    )
    """,
    """
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
    )
    """,
]

with engine.begin() as conn:
    for statement in create_table_statements:
        conn.execute(text(statement))

    tables = conn.execute(text("SHOW TABLES")).all()

print("Connected database: test_case_7")
print("Tables:", tables)

server_engine.dispose()

# %%

# Author: Om Mohite

import re
from pathlib import Path
from sqlalchemy import text

sql_candidates = [
    Path.cwd() / "test_case_7.sql",
    Path.cwd() / "Data-Engineering-Real-World-Projects" / "Test_Case_7" / "test_case_7.sql",
]

sql_file = next((path for path in sql_candidates if path.exists()), None)

if sql_file is None:
    raise FileNotFoundError("Could not find test_case_7.sql.")

sql_script = sql_file.read_text(encoding="utf-8")

table_names = ["customers", "products", "sales"]
insert_statements = {}

for table_name in table_names:
    statements = [
        statement.strip()
        for statement in sql_script.split(";")
        if re.match(
            rf"\s*INSERT\s+INTO\s+{table_name}\b",
            statement,
            re.IGNORECASE,
        )
    ]

    if not statements:
        raise ValueError(f"No INSERT statement found for {table_name}.")

    insert_statements[table_name] = statements

with engine.begin() as conn:
    # Clear test records in foreign-key-safe order
    conn.execute(text("DELETE FROM sales"))
    conn.execute(text("DELETE FROM customers"))
    conn.execute(text("DELETE FROM products"))

    for table_name in table_names:
        for statement in insert_statements[table_name]:
            conn.exec_driver_sql(statement)

    row_counts = {
        table_name: conn.execute(
            text(f"SELECT COUNT(*) FROM {table_name}")
        ).scalar_one()
        for table_name in table_names
    }

print("Rows loaded:", row_counts)

if row_counts != {"customers": 10, "products": 12, "sales": 30}:
    raise ValueError(f"Unexpected source row counts: {row_counts}")

# %%

# Author: Om Mohite

def data_extraction(engine):
    customers_df = pd.read_sql(
        "SELECT * FROM customers",
        con=engine,
    )

    products_df = pd.read_sql(
        "SELECT * FROM products",
        con=engine,
    )

    sales_df = pd.read_sql(
        "SELECT * FROM sales",
        con=engine,
    )

    return customers_df, products_df, sales_df


customers, products, sales = data_extraction(engine)

print("Customers:", len(customers))
print("Products:", len(products))
print("Sales:", len(sales))

display(customers.head(3))
display(products.head(3))
display(sales.head(3))

# %%

# Author: Om Mohite

join_query = """
    SELECT
        c.customer_id,
        p.product_id,
        s.sale_id,
        c.customer_name,
        c.email,
        c.city,
        c.region,
        c.registration_date,
        p.product_name,
        p.category,
        p.unit_price,
        p.stock_quantity,
        s.sale_date,
        s.quantity,
        s.total_amount,
        s.payment_status
    FROM customers AS c
    RIGHT JOIN sales AS s
        ON c.customer_id = s.customer_id
    RIGHT JOIN products AS p
        ON p.product_id = s.product_id
"""

complete_table = pd.read_sql(join_query, con=engine)

print("Joined rows:", len(complete_table))
display(complete_table.head())

# %%

# Author: Om Mohite

region_sales = (
    complete_table
    .groupby("region")["total_amount"]
    .sum()
    .sort_values(ascending=False)
)

print("Sales by region")
display(region_sales.to_frame("total_sales"))

# %%

# Author: Om Mohite

source_sales_count = len(sales)
joined_row_count = len(complete_table)
unique_joined_sales = complete_table["sale_id"].nunique()

source_total = float(sales["total_amount"].sum())
joined_total = float(complete_table["total_amount"].sum())
regional_total = float(region_sales.sum())

validation_report = {
    "source_sales_rows": source_sales_count,
    "joined_rows": joined_row_count,
    "unique_joined_sales": unique_joined_sales,
    "source_total_amount": source_total,
    "joined_total_amount": joined_total,
    "region_report_total": regional_total,
}

display(pd.Series(validation_report, name="value").to_frame())

assert joined_row_count == source_sales_count
assert unique_joined_sales == source_sales_count
assert abs(source_total - joined_total) < 0.01
assert abs(source_total - regional_total) < 0.01

print("TEST CASE 7 VALIDATION PASSED")
