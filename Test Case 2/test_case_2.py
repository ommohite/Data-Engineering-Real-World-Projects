# Author: Om Mohite
# Test Case 2: Python export of the corresponding Jupyter notebook.
# Run from this folder; configure DB_PASSWORD/DB_USER/DB_HOST/DB_PORT as needed.

import os
from pathlib import Path
from getpass import getpass

try:
    from IPython.display import display
except ImportError:
    display = print

import pandas as pd
from sqlalchemy import create_engine, URL, text
from getpass import getpass

# %%

password = getpass("MySQL password: ")

def get_connection(database):

    connection_url = URL.create(
        drivername="mysql+pymysql",
        username="root",
        password=password,
        host="localhost",
        port=3306,
        database=database
    )

    engine = create_engine(connection_url, pool_pre_ping=True)

    return engine

# %%

def data_extraction():

    try:

        engine = get_connection("test_case_2")

        with engine.connect() as conn:

            customer = pd.read_sql(
                text("SELECT * FROM customers"), conn
            )

            orders = pd.read_sql(
                text("SELECT * FROM orders"), conn
            )

            order_item = pd.read_sql(
                text("SELECT * FROM order_items"), conn
            )

            product = pd.read_sql(
                text("SELECT * FROM products"), conn
            )

        print("Data Extraction Completed Successfully")

        print("Customers:", len(customer))
        print("Orders:", len(orders))
        print("Order Items:", len(order_item))
        print("Products:", len(product))

        return customer, orders, order_item, product

    except Exception as e:

        print(f"Extraction Error: {e}")
        raise

    finally:

        if 'engine' in locals():
            engine.dispose()

# %%

def transformation(customer, order, order_item, product):

    # Remove duplicates
    customer = customer.drop_duplicates().copy()
    order = order.drop_duplicates().copy()
    order_item = order_item.drop_duplicates().copy()
    product = product.drop_duplicates().copy()

    # Customer Transformation
    customer = customer.dropna(subset=["customer_id", "customer_name", "email"])

    customer["city"] = customer["city"].fillna("Unknown")

    # Product Transformation
    product = product.dropna(subset=["product_id", "price"])

    product["product_name"] = product["product_name"].fillna("Unknown")
    product["category"] = product["category"].fillna("Unknown")

    product["price"] = pd.to_numeric(
        product["price"], errors="coerce"
    )

    product = product.dropna(subset=["price"])

    product = product[product["price"] > 0].copy()

    # Order Transformation
    order = order.dropna(subset=["order_id", "customer_id"]).copy()

    order = order[
        order["customer_id"].isin(customer["customer_id"])
    ].copy()

    order["order_date"] = pd.to_datetime(
        order["order_date"], errors="coerce"
    )

    order["order_date"] = order["order_date"].ffill()

    order = order.dropna(subset=["order_date"]).copy()

    order["order_date"] = order["order_date"].dt.date

    # Order Item Transformation
    order_item = order_item.dropna(
        subset=["order_item_id", "order_id", "product_id", "quantity"]
    ).copy()

    order_item = order_item[
        order_item["order_id"].isin(order["order_id"])
    ].copy()

    order_item = order_item[
        order_item["product_id"].isin(product["product_id"])
    ].copy()

    order_item.loc[
        order_item["quantity"] <= 0, "quantity"
    ] = 1

    print("Data Transformation Completed Successfully")

    print("Customers:", len(customer))
    print("Orders:", len(order))
    print("Order Items:", len(order_item))
    print("Products:", len(product))

    return customer, order, order_item, product

# %%

def loading_data(customer, order, order_item, product):

    try:

        engine2 = get_connection("test_case_2_dw")

        with engine2.begin() as conn:

            # Clear previous data
            conn.execute(text("DELETE FROM fact_total_sale"))

            conn.execute(text("DELETE FROM stagging_order_items"))
            conn.execute(text("DELETE FROM stagging_orders"))
            conn.execute(text("DELETE FROM stagging_products"))
            conn.execute(text("DELETE FROM stagging_customers"))

            conn.execute(text("DELETE FROM order_dim"))
            conn.execute(text("DELETE FROM product_dim"))
            conn.execute(text("DELETE FROM customer_dim"))

            # 1. Load Customers
            customer.to_sql(
                name="stagging_customers",
                con=conn,
                if_exists="append",
                index=False
            )

            # 2. Load Products
            product.to_sql(
                name="stagging_products",
                con=conn,
                if_exists="append",
                index=False
            )

            # 3. Load Orders
            order.to_sql(
                name="stagging_orders",
                con=conn,
                if_exists="append",
                index=False
            )

            # 4. Load Order Items
            order_item.to_sql(
                name="stagging_order_items",
                con=conn,
                if_exists="append",
                index=False
            )

            # Customer Dimension
            conn.execute(text("""
                INSERT INTO customer_dim
                (customer_id, customer_name, city, email)

                SELECT
                    customer_id,
                    customer_name,
                    city,
                    email

                FROM stagging_customers
            """))

            # Order Dimension
            conn.execute(text("""
                INSERT INTO order_dim
                (order_id, order_date)

                SELECT
                    order_id,
                    order_date

                FROM stagging_orders
            """))

            # Product Dimension
            conn.execute(text("""
                INSERT INTO product_dim
                (product_id, product_name, category)

                SELECT
                    product_id,
                    product_name,
                    category

                FROM stagging_products
            """))

            # Fact Table
            conn.execute(text("""
                INSERT INTO fact_total_sale
                (
                    order_key,
                    product_key,
                    customer_key,
                    price,
                    quantity,
                    total_sale
                )

                SELECT
                    o.order_key,
                    p.product_key,
                    c.customer_key,
                    pr.price,
                    soi.quantity,
                    pr.price * soi.quantity AS total_sale

                FROM stagging_order_items soi

                JOIN stagging_orders so
                    ON so.order_id = soi.order_id

                JOIN order_dim o
                    ON o.order_id = so.order_id

                JOIN customer_dim c
                    ON c.customer_id = so.customer_id

                JOIN product_dim p
                    ON p.product_id = soi.product_id

                JOIN stagging_products pr
                    ON pr.product_id = soi.product_id
            """))

        print("Data Loading Completed Successfully")

    except Exception as e:

        print(f"Loading Error: {e}")
        raise

    finally:

        if 'engine2' in locals():
            engine2.dispose()

# %%

def main_function():

    try:

        # Step 1: Extraction
        customer, order, order_item, product = data_extraction()

        # Step 2: Transformation
        customer, order, order_item, product = transformation(
            customer,
            order,
            order_item,
            product
        )

        # Step 3: Loading
        loading_data(
            customer,
            order,
            order_item,
            product
        )

        print("\nETL Pipeline Executed Successfully")

    except Exception as e:

        print(f"ETL Pipeline Failed: {e}")

# %%

main_function()

# %%

import re
from pathlib import Path

sql_file = Path(__file__).resolve().parent

sql_content = sql_file.read_text(encoding="utf-8")

conn = engine.raw_connection()
cursor = conn.cursor()

try:
    cursor.execute("USE test_case_2")

    statements = sql_content.split(";")

    for query in statements:
        query = query.strip()

        if not query:
            continue

        if re.match(r"CREATE\s+DATABASE", query, re.I):
            continue

        if re.match(r"USE\s+", query, re.I):
            continue

        cursor.execute(query)

    conn.commit()

    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()

    print("DATABASE IMPORT SUCCESSFUL!")
    print("AVAILABLE TABLES:")

    for table in tables:
        print(table[0])

except Exception as e:
    conn.rollback()
    print("IMPORT FAILED:", e)

finally:
    cursor.close()
    conn.close()

# %%

from sqlalchemy import create_engine, URL, text
from getpass import getpass
from pathlib import Path
import re

password = getpass("MySQL password: ")

# Correct database connection
engine = create_engine(
    URL.create(
        "mysql+pymysql",
        username="root",
        password=password,
        host="127.0.0.1",
        port=3306,
        database="test_case_2"
    )
)

# Import SQL file
sql_file = Path(__file__).resolve().parent
sql_content = sql_file.read_text(encoding="utf-8")

with engine.begin() as conn:
    for statement in sql_content.split(";"):
        query = statement.strip()

        if not query:
            continue

        if re.match(r"CREATE\s+DATABASE", query, re.I):
            continue

        if re.match(r"USE\s+", query, re.I):
            continue

        conn.exec_driver_sql(query)

    result = conn.execute(text("SHOW TABLES"))

    print("ETL DATABASE READY!")
    print("TABLES:")

    for row in result:
        print(row[0])

# %%

import pandas as pd

tables = ["customers", "products", "orders", "order_items"]

with engine.connect() as conn:

    extracted_data = {}

    for table in tables:
        df = pd.read_sql(
            f"SELECT * FROM `{table}`",
            conn
        )

        extracted_data[table] = df

        print(f"{table}: {len(df)} records extracted")

print("\nDATA EXTRACTION COMPLETED!")

# %%

# DATA TRANSFORMATION

for table_name, df in extracted_data.items():

    print(f"\nProcessing: {table_name}")

    # Remove duplicate records
    df.drop_duplicates(inplace=True)

    # Handle missing values
    df.dropna(how="all", inplace=True)

    # Reset index
    df.reset_index(drop=True, inplace=True)

    print("Rows:", len(df))
    print("Columns:", list(df.columns))

print("\nDATA TRANSFORMATION COMPLETED SUCCESSFULLY!")

# %%

from sqlalchemy import create_engine
from sqlalchemy.types import Integer, String, Date, Numeric

# Target Database
target_engine = create_engine(
    engine.url.set(database="test_case_2_dw")
)

# Load transformed data
try:
    with target_engine.begin() as conn:

        for table_name, df in extracted_data.items():

            df.to_sql(
                name=table_name,
                con=conn,
                if_exists="replace",
                index=False
            )

            print(f"{table_name}: {len(df)} rows loaded")

    print("\nETL PIPELINE COMPLETED SUCCESSFULLY!")

except Exception as e:
    print("LOADING ERROR:", e)

# %%

with engine.connect() as conn:
    conn.execute(text("CREATE DATABASE IF NOT EXISTS test_case_2_dw"))
    conn.commit()

print("Data Warehouse Ready!")

# %%

main_function()

# %%

source_counts = {
    "customers": len(customer),
    "orders": len(orders),
    "order_items": len(order_item),
    "products": len(product)
}

target_queries = {
    "customers": "SELECT COUNT(*) FROM stagging_customers",
    "orders": "SELECT COUNT(*) FROM stagging_orders",
    "order_items": "SELECT COUNT(*) FROM stagging_order_items",
    "products": "SELECT COUNT(*) FROM stagging_products"
}

print("========== SOURCE VS TARGET VALIDATION ==========")

with engine2.connect() as conn:

    for table_name, query in target_queries.items():

        target_count = conn.execute(
            text(query)
        ).scalar_one()

        source_count = source_counts[table_name]

        print(f"\nTable: {table_name}")
        print("Source Records:", source_count)
        print("Target Records:", target_count)

        if source_count == target_count:
            print("VALIDATION PASSED")
        else:
            print("VALIDATION FAILED")

# %%

# Extract source data

customer, orders, order_item, product = data_extraction()

# Transform source data

customer, orders, order_item, product = transformation(
    customer,
    orders,
    order_item,
    product
)

print("Data Ready For Validation")

print("Customers:", len(customer))
print("Orders:", len(orders))
print("Order Items:", len(order_item))
print("Products:", len(product))

# %%

source_counts = {
    "customers": len(customer),
    "orders": len(orders),
    "order_items": len(order_item),
    "products": len(product)
}

target_queries = {
    "customers": "SELECT COUNT(*) FROM stagging_customers",
    "orders": "SELECT COUNT(*) FROM stagging_orders",
    "order_items": "SELECT COUNT(*) FROM stagging_order_items",
    "products": "SELECT COUNT(*) FROM stagging_products"
}

print("========== SOURCE VS TARGET VALIDATION ==========")

with engine2.connect() as conn:

    for table_name, query in target_queries.items():

        target_count = conn.execute(
            text(query)
        ).scalar_one()

        source_count = source_counts[table_name]

        print(f"\nTable: {table_name}")
        print("Source Records:", source_count)
        print("Target Records:", target_count)

        if source_count == target_count:
            print("VALIDATION PASSED")
        else:
            print("VALIDATION FAILED")

# %%

from sqlalchemy import create_engine, text

# Create Target Database
with engine.connect() as conn:
    conn.execute(text("CREATE DATABASE IF NOT EXISTS test_case_2_dw"))
    conn.commit()

# Define Target Engine
engine2 = create_engine(
    engine.url.set(database="test_case_2_dw")
)

print("TARGET ENGINE CONNECTED SUCCESSFULLY!")

# Test Connection
with engine2.connect() as conn:
    print("TARGET DATABASE:", conn.execute(
        text("SELECT DATABASE()")
    ).scalar())

# %%

import pandas as pd
from sqlalchemy import text

print("=" * 55)
print("       TEST CASE 2 - FINAL ETL PIPELINE")
print("=" * 55)

required_tables = ["customers", "products", "orders", "order_items"]
validation_results = []

try:
    # STEP 1: Check extracted data
    for table in required_tables:
        if table not in extracted_data:
            raise ValueError(f"Missing extracted table: {table}")

    print("\nSTEP 1: DATA EXTRACTION - SUCCESS")

    # STEP 2: Data Transformation
    for table in required_tables:
        extracted_data[table] = (
            extracted_data[table]
            .drop_duplicates()
            .dropna(how="all")
            .reset_index(drop=True)
        )

    print("STEP 2: DATA TRANSFORMATION - SUCCESS")

    # STEP 3: Load into Target Database
    with engine2.begin() as conn:
        for table in required_tables:
            df = extracted_data[table]

            df.to_sql(
                name=table,
                con=conn,
                if_exists="replace",
                index=False
            )

            print(f"{table}: {len(df)} records loaded")

    print("\nSTEP 3: DATA LOADING - SUCCESS")

    # STEP 4: Source vs Target Validation
    with engine2.connect() as conn:
        for table in required_tables:

            target_count = conn.execute(
                text(f"SELECT COUNT(*) FROM `{table}`")
            ).scalar()

            expected_count = len(extracted_data[table])

            status = "PASS" if target_count == expected_count else "FAIL"

            validation_results.append(status)

            print(
                f"{table}: Expected={expected_count}, "
                f"Target={target_count}, Status={status}"
            )

    # STEP 5: Final Status
    print("\n" + "=" * 55)

    if all(status == "PASS" for status in validation_results):
        print("TEST CASE 2: COMPLETED SUCCESSFULLY!")
        print("ETL EXTRACTION: SUCCESS")
        print("ETL TRANSFORMATION: SUCCESS")
        print("ETL LOADING: SUCCESS")
        print("SOURCE/TARGET VALIDATION: PASS")
    else:
        print("TEST CASE 2: VALIDATION FAILED")

    print("=" * 55)

except Exception as e:
    print("\nETL PIPELINE FAILED!")
    print("ERROR:", repr(e))
