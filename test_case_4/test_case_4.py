# Author: Om Mohite
# Test Case 4: Python export of the corresponding Jupyter notebook.
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
        break

if env_file:
    load_dotenv(env_file)

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
    conn.execute(text("CREATE DATABASE IF NOT EXISTS data_cleansing"))

# Connect to the Test Case 4 database
engine = create_engine(
    server_url.set(database="data_cleansing"),
    pool_pre_ping=True,
)

create_table_sql = """
CREATE TABLE IF NOT EXISTS sales_source (
    sale_id INT PRIMARY KEY,
    customer_name VARCHAR(100),
    product_name VARCHAR(100),
    quantity INT,
    unit_price DECIMAL(10, 2),
    total_amount DECIMAL(10, 2),
    sale_date DATE,
    city VARCHAR(100)
)
"""

with engine.begin() as conn:
    conn.execute(text(create_table_sql))
    tables = conn.execute(text("SHOW TABLES")).all()

print("Connected database: data_cleansing")
print("Tables:", tables)

server_engine.dispose()

# %%

# Author: Om Mohite

import pandas as pd
from sqlalchemy import text

source_rows = [
    (1, "Rahul Sharma", "Laptop", 2, 55000, 110000, "2026-01-10", "Pune"),
    (2, "Priya Patel", "Mouse", 3, 500, 1500, "2026-01-12", "Mumbai"),
    (3, "Amit Verma", "Keyboard", -2, 1200, -2400, "2026-01-15", "Delhi"),
    (4, None, "Monitor", 1, 12000, 12000, "2026-01-18", "Pune"),
    (5, "Sneha Joshi", "Headphones", 2, -1500, -3000, "2026-01-20", "Mumbai"),
    (6, "Karan Mehta", None, 1, 25000, 25000, "2026-01-22", "Delhi"),
    (7, "Neha Singh", "Printer", None, 8000, 8000, "2026-01-25", "Pune"),
    (8, "Rohit Kumar", "Tablet", 2, 15000, 25000, "2026-01-27", "Mumbai"),
    (9, "Anjali Desai", "Smartphone", 1, 30000, 30000, None, "Pune"),
    (10, "Vikas Rao", "Laptop", 1, 55000, 55000, "2026-01-30", None),
    (11, "Pooja Shah", "Mouse", 0, 500, 0, "2026-02-02", "Delhi"),
    (12, "Arjun Nair", "Keyboard", 2, None, 2400, "2026-02-05", "Mumbai"),
    (13, "Meera Kulkarni", "Monitor", 1, 12000, None, "2026-02-08", "Pune"),
    (14, "  Ramesh Patil  ", "Headphones", 2, 1500, 3000, "2026-02-10", " Pune "),
    (15, "Sahil Gupta", "Laptop", 1, 55000, 55000, "2026-02-15", "Mumbai"),
]

columns = [
    "sale_id",
    "customer_name",
    "product_name",
    "quantity",
    "unit_price",
    "total_amount",
    "sale_date",
    "city",
]

source_df = pd.DataFrame(source_rows, columns=columns)

with engine.begin() as conn:
    existing_count = conn.execute(
        text("SELECT COUNT(*) FROM sales_source")
    ).scalar_one()

    if existing_count == 0:
        source_df.to_sql(
            name="sales_source",
            con=conn,
            if_exists="append",
            index=False,
        )
        print("Official source records loaded:", len(source_df))

    elif existing_count == 15:
        existing_ids = conn.execute(
            text("SELECT sale_id FROM sales_source ORDER BY sale_id")
        ).scalars().all()

        if existing_ids != list(range(1, 16)):
            raise ValueError("sales_source has 15 rows, but the IDs do not match the source data.")

        print("Official 15 source records are already loaded.")

    else:
        raise ValueError(
            f"sales_source contains {existing_count} rows. "
            "Expected an empty table or the official 15 rows."
        )

df = pd.read_sql(
    "SELECT * FROM sales_source ORDER BY sale_id",
    con=engine,
)

print("Rows:", len(df))
print("Missing values in source:")
display(df.isna().sum().to_frame("missing_count"))
display(df)

# %%

# Author: Om Mohite

import numpy as np

print("Missing values by column")
display(df.isna().sum().to_frame("missing_count"))

print("Rows with negative quantity, price, or total")
negative_mask = (
    (df["quantity"] < 0)
    | (df["unit_price"] < 0)
    | (df["total_amount"] < 0)
)
display(df.loc[negative_mask])

print("Rows with zero or missing quantity")
display(df.loc[df["quantity"].isna() | (df["quantity"] == 0)])

print("Rows with missing customer, product, date, city, price, or total")
display(
    df.loc[
        df[
            [
                "customer_name",
                "product_name",
                "sale_date",
                "city",
                "unit_price",
                "total_amount",
            ]
        ].isna().any(axis=1)
    ]
)

print("Rows where total_amount does not equal quantity * unit_price")
expected_total = df["quantity"] * df["unit_price"]
mismatch_mask = (
    df["total_amount"].notna()
    & expected_total.notna()
    & ((df["total_amount"] - expected_total).abs() > 0.01)
)
display(df.loc[mismatch_mask])

print("Text fields with leading or trailing spaces")
for column in ["customer_name", "product_name", "city"]:
    values = df[column].dropna().astype(str)
    space_count = int((values != values.str.strip()).sum())
    print(f"{column}: {space_count}")

# %%

# Author: Om Mohite

clean_df = df.copy()

# Clean text fields
for column in ["customer_name", "product_name", "city"]:
    clean_df[column] = (
        clean_df[column]
        .astype("string")
        .str.strip()
        .replace("", pd.NA)
        .fillna("Unknown")
    )

# Convert numeric fields
numeric_columns = ["quantity", "unit_price", "total_amount"]

for column in numeric_columns:
    clean_df[column] = pd.to_numeric(clean_df[column], errors="coerce")

# Correct negative numeric values
for column in numeric_columns:
    clean_df[column] = clean_df[column].abs()

# Treat zero or missing quantity as invalid
clean_df.loc[clean_df["quantity"] <= 0, "quantity"] = pd.NA

# Treat zero or missing price as invalid
clean_df.loc[clean_df["unit_price"] <= 0, "unit_price"] = pd.NA

# Recover missing price from total_amount / quantity
price_from_total = clean_df["total_amount"] / clean_df["quantity"]
clean_df["unit_price"] = clean_df["unit_price"].fillna(price_from_total)

# Fill any remaining missing prices with the mean valid price
average_price = clean_df["unit_price"].mean()

if pd.isna(average_price):
    raise ValueError("Cannot fill unit_price: no valid prices are available.")

clean_df["unit_price"] = clean_df["unit_price"].fillna(average_price)

# Recover missing quantity from total_amount / unit_price
quantity_from_total = clean_df["total_amount"] / clean_df["unit_price"]
clean_df["quantity"] = clean_df["quantity"].fillna(quantity_from_total)

# Use the notebook's fallback quantity when it still cannot be recovered
clean_df.loc[clean_df["quantity"] <= 0, "quantity"] = pd.NA
clean_df["quantity"] = clean_df["quantity"].fillna(1)

# Recalculate total_amount to correct missing or inconsistent totals
clean_df["total_amount"] = clean_df["quantity"] * clean_df["unit_price"]

# Keep sale_date as a date; do not invent a missing date
clean_df["sale_date"] = pd.to_datetime(clean_df["sale_date"], errors="coerce")

print("Missing values after cleansing")
display(clean_df.isna().sum().to_frame("missing_count"))

print("Cleaned records")
display(clean_df)

# %%

# Author: Om Mohite

expected_total = clean_df["quantity"] * clean_df["unit_price"]

validation_report = {
    "source_rows": len(df),
    "cleaned_rows": len(clean_df),
    "missing_customer_names": int(clean_df["customer_name"].isna().sum()),
    "missing_product_names": int(clean_df["product_name"].isna().sum()),
    "missing_cities": int(clean_df["city"].isna().sum()),
    "missing_sale_dates": int(clean_df["sale_date"].isna().sum()),
    "invalid_quantities": int(
        (clean_df["quantity"].isna() | (clean_df["quantity"] <= 0)).sum()
    ),
    "invalid_prices": int(
        (clean_df["unit_price"].isna() | (clean_df["unit_price"] <= 0)).sum()
    ),
    "invalid_totals": int(
        (clean_df["total_amount"].isna() | (clean_df["total_amount"] < 0)).sum()
    ),
    "incorrect_total_amounts": int(
        (~(clean_df["total_amount"].round(2) == expected_total.round(2))).sum()
    ),
}

display(pd.Series(validation_report, name="count").to_frame())

checks_passed = (
    validation_report["source_rows"] == 15
    and validation_report["cleaned_rows"] == 15
    and validation_report["missing_customer_names"] == 0
    and validation_report["missing_product_names"] == 0
    and validation_report["missing_cities"] == 0
    and validation_report["invalid_quantities"] == 0
    and validation_report["invalid_prices"] == 0
    and validation_report["invalid_totals"] == 0
    and validation_report["incorrect_total_amounts"] == 0
)

if not checks_passed:
    raise AssertionError("Data cleansing validation failed.")

print("TEST CASE 4 DATA CLEANSING VALIDATION PASSED")
print("Missing sale dates retained for review:", validation_report["missing_sale_dates"])
