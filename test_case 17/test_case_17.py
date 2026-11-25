# Author: Om Mohite
# Test Case 17: Python export of the corresponding Jupyter notebook.
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
    conn.execute(text("CREATE DATABASE IF NOT EXISTS multitenant_db"))

server_engine.dispose()

database_url = URL.create(
    drivername="mysql+pymysql",
    username=os.getenv("DB_USER", "root"),
    password=db_password,
    host=os.getenv("DB_HOST", "localhost"),
    port=int(os.getenv("DB_PORT", "3306")),
    database="multitenant_db",
)

engine = create_engine(database_url, pool_pre_ping=True)

print("Database multitenant_db is ready.")

# %%

# Author: Om Mohite

import re
from pathlib import Path

sql_file = Path.cwd() / "test_case_17.sql"
if not sql_file.exists():
    raise FileNotFoundError(f"SQL file not found: {sql_file}")

sql_script = sql_file.read_text(encoding="utf-8")
load_statements = []

for statement in sql_script.split(";"):
    statement = statement.strip()

    if re.match(
        r"^(CREATE TABLE|INSERT INTO (tenants|customers|products|orders)\b|CREATE INDEX)",
        statement,
        re.IGNORECASE,
    ):
        load_statements.append(statement)

with engine.begin() as conn:
    conn.exec_driver_sql("DROP TABLE IF EXISTS orders")
    conn.exec_driver_sql("DROP TABLE IF EXISTS products")
    conn.exec_driver_sql("DROP TABLE IF EXISTS customers")
    conn.exec_driver_sql("DROP TABLE IF EXISTS tenants")

    for statement in load_statements:
        conn.exec_driver_sql(statement)

with engine.connect() as conn:
    for table_name in ["tenants", "customers", "products", "orders"]:
        row_count = conn.execute(
            text(f"SELECT COUNT(*) FROM {table_name}")
        ).scalar_one()
        print(f"{table_name}: {row_count} rows")

print("SQL file used:", sql_file.name)

# %%

# Author: Om Mohite

with engine.connect() as conn:
    tenants_df = pd.read_sql(
        text("SELECT * FROM tenants ORDER BY tenant_id"),
        conn,
    )

    customers_df = pd.read_sql(
        text("SELECT * FROM customers ORDER BY tenant_id, customer_id"),
        conn,
    )

    products_df = pd.read_sql(
        text("SELECT * FROM products ORDER BY tenant_id, product_id"),
        conn,
    )

    orders_df = pd.read_sql(
        text("SELECT * FROM orders ORDER BY tenant_id, order_id"),
        conn,
    )

print("Tenants:", len(tenants_df))
print("Customers:", len(customers_df))
print("Products:", len(products_df))
print("Orders:", len(orders_df))

tenant_id = 1

tenant_customers = customers_df[customers_df["tenant_id"] == tenant_id]
tenant_products = products_df[products_df["tenant_id"] == tenant_id]
tenant_orders = orders_df[orders_df["tenant_id"] == tenant_id]

print(f"Tenant {tenant_id} customers:", len(tenant_customers))
print(f"Tenant {tenant_id} products:", len(tenant_products))
print(f"Tenant {tenant_id} orders:", len(tenant_orders))

display(tenant_customers)
display(tenant_products)
display(tenant_orders)

# %%

# Author: Om Mohite

tenant_orders_query = text("""
    SELECT
        o.tenant_id,
        o.order_id,
        o.order_date,
        o.total_amount,
        c.customer_id,
        c.customer_name,
        c.email
    FROM orders AS o
    JOIN customers AS c
        ON o.customer_id = c.customer_id
       AND o.tenant_id = c.tenant_id
    WHERE o.tenant_id = :tenant_id
    ORDER BY o.order_date, o.order_id
""")

with engine.connect() as conn:
    tenant_order_details = pd.read_sql(
        tenant_orders_query,
        conn,
        params={"tenant_id": tenant_id},
    )

display(tenant_order_details)

assert tenant_order_details["tenant_id"].eq(tenant_id).all()
print(f"Tenant-safe join rows for tenant {tenant_id}:", len(tenant_order_details))

# %%

# Author: Om Mohite

tenant_revenue_query = text("""
    SELECT
        t.tenant_id,
        t.tenant_name,
        COALESCE(SUM(o.total_amount), 0) AS total_revenue
    FROM tenants AS t
    LEFT JOIN orders AS o
        ON t.tenant_id = o.tenant_id
    GROUP BY t.tenant_id, t.tenant_name
    ORDER BY total_revenue DESC
""")

customer_spending_query = text("""
    SELECT
        c.tenant_id,
        c.customer_id,
        c.customer_name,
        COALESCE(SUM(o.total_amount), 0) AS total_spent
    FROM customers AS c
    LEFT JOIN orders AS o
        ON c.customer_id = o.customer_id
       AND c.tenant_id = o.tenant_id
    WHERE c.tenant_id = :tenant_id
    GROUP BY c.tenant_id, c.customer_id, c.customer_name
    ORDER BY total_spent DESC
""")

with engine.connect() as conn:
    tenant_revenue = pd.read_sql(tenant_revenue_query, conn)
    customer_spending = pd.read_sql(
        customer_spending_query,
        conn,
        params={"tenant_id": tenant_id},
    )

display(tenant_revenue)
display(customer_spending)

# %%

# Author: Om Mohite

explain_queries = {
    "orders_by_tenant_and_date": """
        EXPLAIN
        SELECT *
        FROM orders
        WHERE tenant_id = 1
          AND order_date >= '2026-11-01'
    """,
    "customers_by_tenant_and_name": """
        EXPLAIN
        SELECT *
        FROM customers
        WHERE tenant_id = 1
          AND customer_name = 'Rahul Sharma'
    """,
    "products_by_tenant_and_name": """
        EXPLAIN
        SELECT *
        FROM products
        WHERE tenant_id = 2
          AND product_name = 'Smartphone'
    """,
}

with engine.connect() as conn:
    for query_name, query in explain_queries.items():
        print(query_name)
        plan = pd.read_sql(text(query), conn)
        display(plan)

# %%

# Author: Om Mohite

from sqlalchemy import inspect

expected_revenue = {
    1: 79800.00,
    2: 49200.00,
    3: 102200.00,
    4: 154500.00,
}

actual_revenue = dict(
    zip(tenant_revenue["tenant_id"], tenant_revenue["total_revenue"])
)

index_names = {
    index["name"]
    for table_name in ["orders", "customers", "products"]
    for index in inspect(engine).get_indexes(table_name)
}

required_indexes = {
    "idx_orders_tenant_date",
    "idx_customers_tenant_name",
    "idx_products_tenant_name",
}

print("Tenant revenue:", actual_revenue)
print("Tenant 1 joined order rows:", len(tenant_order_details))
print("Cross-tenant insert blocked:", cross_tenant_insert_blocked)
print("Required indexes present:", required_indexes.issubset(index_names))

assert len(tenants_df) == 4
assert len(customers_df) == 8
assert len(products_df) == 20
assert len(orders_df) == 12
assert actual_revenue == expected_revenue
assert tenant_order_details["tenant_id"].eq(1).all()
assert cross_tenant_insert_blocked
assert required_indexes.issubset(index_names)

print("TEST CASE 17 MULTI-TENANT VALIDATION PASSED")
