# Author: Om Mohite
# Test Case 14: Python export of the corresponding Jupyter notebook.
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
    conn.execute(text("CREATE DATABASE IF NOT EXISTS test_case_14"))

server_engine.dispose()

connection_url = URL.create(
    drivername="mysql+pymysql",
    username=os.getenv("DB_USER", "root"),
    password=db_password,
    host=os.getenv("DB_HOST", "localhost"),
    port=int(os.getenv("DB_PORT", "3306")),
    database="test_case_14",
)

engine = create_engine(connection_url, pool_pre_ping=True)

print("Database test_case_14 is ready.")

# %%

# Author: Om Mohite

import re
from pathlib import Path

sql_candidates = [
    Path.cwd() / "test_case_14.sql",
    Path(__file__).resolve().parent,
]

sql_file = next((path for path in sql_candidates if path.is_file()), None)
if sql_file is None:
    raise FileNotFoundError("Could not find test_case_14.sql")

sql_script = sql_file.read_text(encoding="utf-8")
load_statements = []

for statement in sql_script.split(";"):
    cleaned_statement = statement.strip()

    if re.match(
        r"^(CREATE TABLE|INSERT INTO (customers|products|orders)\b)",
        cleaned_statement,
        re.IGNORECASE,
    ):
        load_statements.append(cleaned_statement)

with engine.begin() as conn:
    conn.exec_driver_sql("DROP TABLE IF EXISTS daily_sales_analytics")
    conn.exec_driver_sql("DROP TABLE IF EXISTS orders")
    conn.exec_driver_sql("DROP TABLE IF EXISTS products")
    conn.exec_driver_sql("DROP TABLE IF EXISTS customers")

    for statement in load_statements:
        conn.exec_driver_sql(statement)

with engine.connect() as conn:
    for table_name in ["customers", "products", "orders"]:
        row_count = conn.execute(
            text(f"SELECT COUNT(*) FROM {table_name}")
        ).scalar_one()
        print(f"{table_name}: {row_count} rows")

print("SQL file used:", sql_file.name)

# %%

# Author: Om Mohite

with engine.connect() as conn:
    customers_df = pd.read_sql(
        text("SELECT * FROM customers ORDER BY customer_id"),
        conn,
    )

    products_df = pd.read_sql(
        text("SELECT * FROM products ORDER BY product_id"),
        conn,
    )

    orders_df = pd.read_sql(
        text("SELECT * FROM orders ORDER BY order_id"),
        conn,
    )

print("Customers:", len(customers_df))
print("Products:", len(products_df))
print("Orders:", len(orders_df))

display(customers_df.head())
display(products_df.head())
display(orders_df.head())

# %%

# Author: Om Mohite

customer_orders = customers_df.merge(
    orders_df,
    on="customer_id",
    how="left",
)

sales_detail = customer_orders.merge(
    products_df,
    on="product_id",
    how="left",
)

sales_detail["order_date"] = pd.to_datetime(
    sales_detail["order_date"],
    errors="coerce",
)

sales_detail["total_amount"] = pd.to_numeric(
    sales_detail["total_amount"],
    errors="coerce",
)

sales_detail = sales_detail.dropna(
    subset=["order_date", "city", "category", "order_id"]
).copy()

sales_detail["sales_date"] = sales_detail["order_date"].dt.normalize()

daily_sales_df = (
    sales_detail
    .groupby(["sales_date", "city", "category"], as_index=False)
    .agg(
        total_orders=("order_id", "nunique"),
        total_quantity=("quantity", "sum"),
        total_revenue=("total_amount", "sum"),
    )
)

daily_sales_df["average_order_value"] = (
    daily_sales_df["total_revenue"] / daily_sales_df["total_orders"]
).round(2)

daily_sales_df = daily_sales_df.sort_values(
    ["sales_date", "city", "category"]
).reset_index(drop=True)

print("Daily analytics rows:", len(daily_sales_df))
display(daily_sales_df.head())

# %%

# Author: Om Mohite

daily_sales_to_load = daily_sales_df.copy()
daily_sales_to_load["batch_timestamp"] = pd.Timestamp.now()

with engine.begin() as conn:
    conn.execute(text("DELETE FROM daily_sales_analytics"))

    daily_sales_to_load.to_sql(
        name="daily_sales_analytics",
        con=conn,
        if_exists="append",
        index=False,
        chunksize=100,
        method="multi",
    )

with engine.connect() as conn:
    loaded_rows = conn.execute(
        text("SELECT COUNT(*) FROM daily_sales_analytics")
    ).scalar_one()

print("Daily analytics rows loaded:", loaded_rows)

# %%

# Author: Om Mohite

with engine.connect() as conn:
    loaded_analytics = pd.read_sql(
        text("""
            SELECT
                sales_date,
                city,
                category,
                total_orders,
                total_quantity,
                total_revenue,
                average_order_value,
                batch_timestamp
            FROM daily_sales_analytics
            ORDER BY sales_date, city, category
        """),
        conn,
    )

print("Analytics groups:", len(loaded_analytics))
print("Orders represented:", loaded_analytics["total_orders"].sum())
print("Quantity represented:", loaded_analytics["total_quantity"].sum())
print("Revenue in analytics:", loaded_analytics["total_revenue"].sum())
print("Revenue in source orders:", orders_df["total_amount"].sum())

assert len(loaded_analytics) == len(daily_sales_df)
assert loaded_analytics["total_orders"].sum() == len(orders_df)
assert loaded_analytics["total_quantity"].sum() == orders_df["quantity"].sum()
assert round(loaded_analytics["total_revenue"].sum(), 2) == round(
    orders_df["total_amount"].sum(), 2
)

display(loaded_analytics.head())
print("TEST CASE 14 DAILY SALES VALIDATION PASSED")

# %%

# Author: Om Mohite

import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

def send_error_email(error_detail):
    load_dotenv(override=True)

    sender_email = os.getenv("SENDER_EMAIL")
    receiver_email = os.getenv("RECEIVER_EMAIL")
    email_password = os.getenv("EMAIL_PASSWORD")

    if not all([sender_email, receiver_email, email_password]):
        print("Email alert skipped: email settings are missing from .env.")
        return False

    message = EmailMessage()
    message["Subject"] = "Test Case 14 ETL Pipeline Failure"
    message["From"] = sender_email
    message["To"] = receiver_email
    message.set_content(f"Daily sales ETL failed:\n\n{error_detail}")

    with smtplib.SMTP("smtp.gmail.com", 587, timeout=30) as server:
        server.starttls()
        server.login(sender_email, email_password)
        server.send_message(message)

    print("Error alert email sent.")
    return True

print("ETL error alert function is ready.")
