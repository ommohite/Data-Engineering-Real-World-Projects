# Author: Om Mohite
# Test Case 8: Python export of the corresponding Jupyter notebook.
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
    conn.execute(text("CREATE DATABASE IF NOT EXISTS test_case_8"))

engine = create_engine(
    server_url.set(database="test_case_8"),
    pool_pre_ping=True,
)

create_table_sql = """
CREATE TABLE IF NOT EXISTS sales (
    sale_id INT PRIMARY KEY AUTO_INCREMENT,
    product_name VARCHAR(100),
    category VARCHAR(50),
    sale_date DATE,
    quantity INT,
    unit_price DECIMAL(10, 2),
    total_amount DECIMAL(12, 2)
)
"""

with engine.begin() as conn:
    conn.execute(text(create_table_sql))
    tables = conn.execute(text("SHOW TABLES")).all()

print("Connected database: test_case_8")
print("Tables:", tables)

server_engine.dispose()

# %%

# Author: Om Mohite

import re
from pathlib import Path
from sqlalchemy import text

sql_candidates = [
    Path.cwd() / "test_case_8.sql",
    Path.cwd() / "Data-Engineering-Real-World-Projects" / "Test_Case_8" / "test_case_8.sql",
    Path.cwd() / "Data-Engineering-Real-World-Projects" / "test_case_8" / "test_case_8.sql",
]

sql_file = next((path for path in sql_candidates if path.exists()), None)

if sql_file is None:
    raise FileNotFoundError("Could not find test_case_8.sql.")

sql_script = sql_file.read_text(encoding="utf-8")

insert_statements = [
    statement.strip()
    for statement in sql_script.split(";")
    if re.match(
        r"\s*INSERT\s+INTO\s+sales\b",
        statement,
        re.IGNORECASE,
    )
]

if not insert_statements:
    raise ValueError("No INSERT statement for sales was found.")

with engine.begin() as conn:
    conn.execute(text("DELETE FROM sales"))

    for statement in insert_statements:
        conn.exec_driver_sql(statement)

with engine.connect() as conn:
    row_count = conn.execute(
        text("SELECT COUNT(*) FROM sales")
    ).scalar_one()

    preview = pd.read_sql(
        "SELECT * FROM sales ORDER BY sale_date, sale_id LIMIT 5",
        con=conn,
    )

print("Rows loaded:", row_count)
display(preview)

if row_count != 24:
    raise ValueError(f"Expected 24 rows; found {row_count}.")

# %%

# Notebook setup command omitted from the Python export: %pip install matplotlib

# %%

import sys

print("Notebook Python:", sys.executable)

# Notebook setup command omitted from the Python export: %pip install matplotlib

import matplotlib.pyplot as plt

print("Matplotlib import successful")

# %%

import pandas as pd
from sqlalchemy import text

rows = [
    ("Laptop", "Electronics", "2025-01-05", 2, 55000, 110000),
    ("Mobile", "Electronics", "2025-01-10", 3, 20000, 60000),
    ("Chair", "Furniture", "2025-01-12", 5, 3000, 15000),
    ("Table", "Furniture", "2025-01-18", 2, 7000, 14000),
    ("Shirt", "Clothing", "2025-01-20", 10, 800, 8000),
    ("Jeans", "Clothing", "2025-01-25", 5, 1500, 7500),

    ("Laptop", "Electronics", "2025-02-03", 1, 55000, 55000),
    ("Mobile", "Electronics", "2025-02-08", 4, 20000, 80000),
    ("Chair", "Furniture", "2025-02-11", 3, 3000, 9000),
    ("Table", "Furniture", "2025-02-15", 4, 7000, 28000),
    ("Shirt", "Clothing", "2025-02-19", 8, 800, 6400),
    ("Jeans", "Clothing", "2025-02-23", 6, 1500, 9000),

    ("Laptop", "Electronics", "2025-03-04", 3, 55000, 165000),
    ("Mobile", "Electronics", "2025-03-09", 2, 20000, 40000),
    ("Chair", "Furniture", "2025-03-13", 6, 3000, 18000),
    ("Table", "Furniture", "2025-03-17", 3, 7000, 21000),
    ("Shirt", "Clothing", "2025-03-21", 12, 800, 9600),
    ("Jeans", "Clothing", "2025-03-26", 4, 1500, 6000),

    ("Laptop", "Electronics", "2025-04-02", 2, 55000, 110000),
    ("Mobile", "Electronics", "2025-04-07", 5, 20000, 100000),
    ("Chair", "Furniture", "2025-04-12", 4, 3000, 12000),
    ("Table", "Furniture", "2025-04-16", 5, 7000, 35000),
    ("Shirt", "Clothing", "2025-04-20", 7, 800, 5600),
    ("Jeans", "Clothing", "2025-04-25", 8, 1500, 12000),
]

columns = [
    "product_name",
    "category",
    "sale_date",
    "quantity",
    "unit_price",
    "total_amount",
]

sales_df = pd.DataFrame(rows, columns=columns)
sales_df["sale_date"] = pd.to_datetime(sales_df["sale_date"]).dt.date

with engine.begin() as conn:
    conn.execute(text("DELETE FROM sales"))
    conn.execute(
        text("""
            INSERT INTO sales
            (product_name, category, sale_date, quantity, unit_price, total_amount)
            VALUES
            (:product_name, :category, :sale_date, :quantity, :unit_price, :total_amount)
        """),
        sales_df.to_dict(orient="records"),
    )

print("Rows loaded:", len(sales_df))
display(sales_df.head())

# %%

# Author: Om Mohite

def data_extraction(engine):
    sales_df = pd.read_sql(
        "SELECT * FROM sales",
        con=engine,
    )

    if sales_df.empty:
        raise ValueError("The sales table contains no records.")

    return sales_df


def data_transformation(sales_df):
    transformed_df = sales_df.copy()

    transformed_df = transformed_df[
        transformed_df["sale_id"].notna()
    ].copy()

    transformed_df["sale_date"] = pd.to_datetime(
        transformed_df["sale_date"],
        errors="raise",
    )

    transformed_df["Month"] = transformed_df["sale_date"].dt.month_name()

    return transformed_df.reset_index(drop=True)


sales_df = data_extraction(engine)
new_df = data_transformation(sales_df)

print("Extracted rows:", len(sales_df))
print("Transformed rows:", len(new_df))
display(new_df.head())

# %%

# Author: Om Mohite

monthly_pivot = pd.pivot_table(
    new_df,
    values="total_amount",
    index="product_name",
    columns="Month",
    aggfunc="sum",
    fill_value=0
)

month_order = ["January", "February", "March", "April"]
monthly_pivot = monthly_pivot.reindex(columns=month_order, fill_value=0)

monthly_pivot["Total"] = monthly_pivot.sum(axis=1)

display(monthly_pivot)

# %%

# Author: Om Mohite

expected_total = sales_df["total_amount"].sum()
pivot_total = monthly_pivot["Total"].sum()

print("Source rows:", len(sales_df))
print("Products in pivot:", len(monthly_pivot))
print("Source total:", expected_total)
print("Pivot total:", pivot_total)

assert len(sales_df) == 24
assert len(monthly_pivot) == 6
assert expected_total == pivot_total

print("TEST CASE 8 PIVOT VALIDATION PASSED")
