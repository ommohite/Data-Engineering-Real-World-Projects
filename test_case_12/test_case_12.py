# Author: Om Mohite
# Test Case 12: Python export of the corresponding Jupyter notebook.
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
import pandas as pd
from sqlalchemy import URL, create_engine, text
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
    conn.execute(text("CREATE DATABASE IF NOT EXISTS test_case_12"))

server_engine.dispose()

connection_url = URL.create(
    drivername="mysql+pymysql",
    username=os.getenv("DB_USER", "root"),
    password=db_password,
    host=os.getenv("DB_HOST", "localhost"),
    port=int(os.getenv("DB_PORT", "3306")),
    database="test_case_12",
)

engine = create_engine(connection_url, pool_pre_ping=True)

print("Database test_case_12 is ready.")

# %%

# Author: Om Mohite

customers = [
    (101, "Rahul Sharma", "Pune", "2024-01-10"),
    (102, "Amit Verma", "Mumbai", "2024-02-15"),
    (103, "Priya Patel", "Pune", "2024-03-20"),
    (104, "Sneha Joshi", "Nashik", "2024-04-05"),
    (105, "Rohan Mehta", "Mumbai", "2024-05-12"),
    (106, "Neha Singh", "Pune", "2024-06-18"),
    (107, "Karan Shah", "Delhi", "2024-07-22"),
    (108, "Pooja Desai", "Nashik", "2024-08-30"),
    (109, "Arjun Rao", "Mumbai", "2024-09-14"),
    (110, "Ananya Kulkarni", "Pune", "2024-10-01"),
]

orders = [
    (1, 101, "2026-11-18", 5000),
    (2, 101, "2026-11-10", 4500),
    (3, 101, "2026-10-25", 6000),
    (4, 101, "2026-10-05", 5500),
    (5, 101, "2026-09-15", 7000),
    (6, 102, "2026-11-15", 2000),
    (7, 102, "2026-10-20", 2500),
    (8, 102, "2026-09-10", 1800),
    (9, 102, "2026-08-05", 2200),
    (10, 103, "2026-11-17", 500),
    (11, 103, "2026-07-12", 700),
    (12, 104, "2026-03-01", 3000),
    (13, 104, "2026-02-10", 2500),
    (14, 105, "2026-06-10", 12000),
    (15, 105, "2026-05-15", 15000),
    (16, 105, "2026-04-20", 10000),
    (17, 105, "2026-03-25", 13000),
    (18, 106, "2026-11-19", 800),
    (19, 107, "2026-09-01", 1500),
    (20, 107, "2026-05-01", 2000),
    (21, 108, "2025-06-10", 900),
    (22, 108, "2025-04-15", 1200),
    (23, 109, "2026-11-16", 400),
    (24, 109, "2026-11-12", 350),
    (25, 109, "2026-11-05", 450),
    (26, 109, "2026-10-28", 300),
    (27, 109, "2026-10-15", 500),
    (28, 110, "2026-11-01", 2500),
]

with engine.begin() as conn:
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS customers (
            customer_id INT PRIMARY KEY,
            customer_name VARCHAR(100),
            city VARCHAR(50),
            signup_date DATE
        )
    """))

    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id INT PRIMARY KEY,
            customer_id INT,
            order_date DATE,
            total_amount DECIMAL(10, 2),
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        )
    """))

    conn.execute(text("DELETE FROM orders"))
    conn.execute(text("DELETE FROM customers"))

    conn.execute(
        text("""
            INSERT INTO customers
                (customer_id, customer_name, city, signup_date)
            VALUES
                (:customer_id, :customer_name, :city, :signup_date)
        """),
        [
            {
                "customer_id": customer_id,
                "customer_name": customer_name,
                "city": city,
                "signup_date": signup_date,
            }
            for customer_id, customer_name, city, signup_date in customers
        ],
    )

    conn.execute(
        text("""
            INSERT INTO orders
                (order_id, customer_id, order_date, total_amount)
            VALUES
                (:order_id, :customer_id, :order_date, :total_amount)
        """),
        [
            {
                "order_id": order_id,
                "customer_id": customer_id,
                "order_date": order_date,
                "total_amount": total_amount,
            }
            for order_id, customer_id, order_date, total_amount in orders
        ],
    )

with engine.connect() as conn:
    customer_count = conn.execute(
        text("SELECT COUNT(*) FROM customers")
    ).scalar_one()
    order_count = conn.execute(
        text("SELECT COUNT(*) FROM orders")
    ).scalar_one()

print("Customers loaded:", customer_count)
print("Orders loaded:", order_count)

# %%

# Author: Om Mohite

import re
from pathlib import Path

sql_file = Path.cwd() / "test_case_12.sql"
if not sql_file.exists():
    raise FileNotFoundError(f"SQL file not found: {sql_file}")

sql_script = sql_file.read_text(encoding="utf-8")

statements = []
for statement in sql_script.split(";"):
    cleaned_lines = [
        line for line in statement.splitlines()
        if not line.strip().startswith("--")
    ]
    cleaned_statement = "\n".join(cleaned_lines).strip()

    if re.match(r"^(CREATE TABLE|INSERT INTO (customers|orders)\b)", cleaned_statement, re.IGNORECASE):
        statements.append(cleaned_statement)

if not statements:
    raise ValueError("No customer/order table statements found in the SQL file.")

with engine.begin() as conn:
    conn.exec_driver_sql("DROP TABLE IF EXISTS orders")
    conn.exec_driver_sql("DROP TABLE IF EXISTS customers")

    for statement in statements:
        conn.exec_driver_sql(statement)

with engine.connect() as conn:
    customer_count = conn.execute(
        text("SELECT COUNT(*) FROM customers")
    ).scalar_one()
    order_count = conn.execute(
        text("SELECT COUNT(*) FROM orders")
    ).scalar_one()

print("SQL file used:", sql_file.name)
print("Customers loaded:", customer_count)
print("Orders loaded:", order_count)

# %%

# Author: Om Mohite

with engine.connect() as conn:
    customers_df = pd.read_sql(
        text("""
            SELECT customer_id, customer_name, city, signup_date
            FROM customers
            ORDER BY customer_id
        """),
        conn,
    )

    orders_df = pd.read_sql(
        text("""
            SELECT order_id, customer_id, order_date, total_amount
            FROM orders
            ORDER BY order_id
        """),
        conn,
    )

print("Customers:", len(customers_df))
print("Orders:", len(orders_df))

display(customers_df.head())
display(orders_df.head())

# %%

# Author: Om Mohite

customers_clean = customers_df.copy()
orders_clean = orders_df.copy()

customers_clean["signup_date"] = pd.to_datetime(
    customers_clean["signup_date"],
    errors="coerce",
)

orders_clean["order_date"] = pd.to_datetime(
    orders_clean["order_date"],
    errors="coerce",
)

customers_clean["customer_name"] = (
    customers_clean["customer_name"]
    .astype("string")
    .str.strip()
    .replace("", pd.NA)
    .fillna("Unknown")
)

customers_clean["city"] = (
    customers_clean["city"]
    .astype("string")
    .str.strip()
    .replace("", pd.NA)
)

if customers_clean["city"].notna().any():
    city_mode = customers_clean["city"].mode().iloc[0]
else:
    city_mode = "Unknown"

customers_clean["city"] = customers_clean["city"].fillna(city_mode)

orders_clean["total_amount"] = pd.to_numeric(
    orders_clean["total_amount"],
    errors="coerce",
)
orders_clean["total_amount"] = orders_clean["total_amount"].fillna(
    orders_clean["total_amount"].mean()
)

rfm_metrics = (
    orders_clean
    .groupby("customer_id")
    .agg(
        last_order_date=("order_date", "max"),
        Frequency=("order_id", "nunique"),
        Monetary_Value=("total_amount", "sum"),
    )
    .reset_index()
)

rfm_df = customers_clean[
    ["customer_id", "customer_name", "city"]
].merge(
    rfm_metrics,
    on="customer_id",
    how="left",
)

today = pd.Timestamp.today().normalize()
rfm_df["Recency"] = (today - rfm_df["last_order_date"]).dt.days
rfm_df["Frequency"] = rfm_df["Frequency"].fillna(0).astype(int)
rfm_df["Monetary_Value"] = rfm_df["Monetary_Value"].fillna(0).round(2)

rfm_df = rfm_df[
    [
        "customer_id",
        "customer_name",
        "city",
        "Recency",
        "Frequency",
        "Monetary_Value",
    ]
].sort_values("customer_id")

display(rfm_df)

# %%

# Author: Om Mohite

rfm_df.to_sql(
    name="rfm",
    con=engine,
    if_exists="replace",
    index=False,
    chunksize=100,
    method="multi",
)

with engine.connect() as conn:
    saved_count = conn.execute(
        text("SELECT COUNT(*) FROM rfm")
    ).scalar_one()

print("RFM rows saved:", saved_count)

# %%

# Author: Om Mohite

with engine.connect() as conn:
    rfm_saved = pd.read_sql(
        text("""
            SELECT
                customer_id,
                Recency,
                Frequency,
                Monetary_Value
            FROM rfm
            ORDER BY customer_id
        """),
        conn,
    )

print("RFM customers:", len(rfm_saved))
print("Total orders represented:", rfm_saved["Frequency"].sum())
print("RFM monetary total:", round(rfm_saved["Monetary_Value"].sum(), 2))
print("Source orders:", len(orders_clean))
print("Source monetary total:", round(orders_clean["total_amount"].sum(), 2))

assert len(rfm_saved) == 10
assert rfm_saved["Frequency"].sum() == len(orders_clean)
assert round(rfm_saved["Monetary_Value"].sum(), 2) == round(
    orders_clean["total_amount"].sum(), 2
)
assert rfm_saved["Recency"].notna().all()
assert rfm_saved["Recency"].ge(0).all()

print("TEST CASE 12 RFM VALIDATION PASSED")
