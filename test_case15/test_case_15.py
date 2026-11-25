# Author: Om Mohite
# Test Case 15: Python export of the corresponding Jupyter notebook.
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
    conn.execute(text("CREATE DATABASE IF NOT EXISTS test_case_15_staging"))
    conn.execute(text("CREATE DATABASE IF NOT EXISTS test_case_15_production"))

server_engine.dispose()

staging_url = URL.create(
    drivername="mysql+pymysql",
    username=os.getenv("DB_USER", "root"),
    password=db_password,
    host=os.getenv("DB_HOST", "localhost"),
    port=int(os.getenv("DB_PORT", "3306")),
    database="test_case_15_staging",
)

production_url = URL.create(
    drivername="mysql+pymysql",
    username=os.getenv("DB_USER", "root"),
    password=db_password,
    host=os.getenv("DB_HOST", "localhost"),
    port=int(os.getenv("DB_PORT", "3306")),
    database="test_case_15_production",
)

staging_engine = create_engine(staging_url, pool_pre_ping=True)
production_engine = create_engine(production_url, pool_pre_ping=True)

print("Staging and production databases are ready.")

# %%

# Author: Om Mohite

import re
from pathlib import Path

sql_candidates = [
    Path.cwd() / "test_case_15.sql",
    Path(__file__).resolve().parent,
]

sql_file = next((path for path in sql_candidates if path.is_file()), None)
if sql_file is None:
    raise FileNotFoundError("Could not find test_case_15.sql")

sql_script = sql_file.read_text(encoding="utf-8")
staging_statements = []

for statement in sql_script.split(";"):
    statement = statement.strip()
    if re.match(r"^(CREATE TABLE|INSERT INTO customer\b)", statement, re.IGNORECASE):
        staging_statements.append(statement)

with staging_engine.begin() as conn:
    conn.exec_driver_sql("DROP TABLE IF EXISTS customer")
    for statement in staging_statements:
        conn.exec_driver_sql(statement)

with production_engine.begin() as conn:
    conn.exec_driver_sql("""
        CREATE TABLE IF NOT EXISTS customer (
            cust_id INT PRIMARY KEY,
            customer_name VARCHAR(100),
            customer_email VARCHAR(100),
            update_on DATETIME
        )
    """)
    conn.exec_driver_sql("""
        CREATE TABLE IF NOT EXISTS watermark (
            pipeline VARCHAR(100) PRIMARY KEY,
            update_timestamp DATETIME
        )
    """)
    conn.exec_driver_sql("DELETE FROM customer")
    conn.exec_driver_sql("DELETE FROM watermark")

with staging_engine.connect() as conn:
    staging_count = conn.execute(
        text("SELECT COUNT(*) FROM customer")
    ).scalar_one()

print("SQL file used:", sql_file.name)
print("Staging customers loaded:", staging_count)
print("Production customer and watermark tables are ready.")

# %%

    # Author: Om Mohite

upsert_all_sql = text("""
    INSERT INTO test_case_15_production.customer
        (cust_id, customer_name, customer_email, update_on)
    SELECT
        cust_id, customer_name, customer_email, update_on
    FROM test_case_15_staging.customer
    ON DUPLICATE KEY UPDATE
        customer_name = VALUES(customer_name),
        customer_email = VALUES(customer_email),
        update_on = VALUES(update_on)
""")

upsert_incremental_sql = text("""
    INSERT INTO test_case_15_production.customer
        (cust_id, customer_name, customer_email, update_on)
    SELECT
        cust_id, customer_name, customer_email, update_on
    FROM test_case_15_staging.customer
    WHERE update_on > :last_update
    ON DUPLICATE KEY UPDATE
        customer_name = VALUES(customer_name),
        customer_email = VALUES(customer_email),
        update_on = VALUES(update_on)
""")

with production_engine.begin() as conn:
    last_update = conn.execute(
        text("""
            SELECT update_timestamp
            FROM watermark
            WHERE pipeline = 'customer'
        """)
    ).scalar_one_or_none()

    if last_update is None:
        conn.execute(upsert_all_sql)
        print("Initial load completed.")
    else:
        conn.execute(
            upsert_incremental_sql,
            {"last_update": last_update},
        )
        print("Incremental load completed.")

    max_update = conn.execute(
        text("SELECT MAX(update_on) FROM test_case_15_staging.customer")
    ).scalar_one()

    conn.execute(
        text("""
            INSERT INTO watermark (pipeline, update_timestamp)
            VALUES ('customer', :update_timestamp)
            ON DUPLICATE KEY UPDATE
                update_timestamp = VALUES(update_timestamp)
        """),
        {"update_timestamp": max_update},
    )

    production_count = conn.execute(
        text("SELECT COUNT(*) FROM test_case_15_production.customer")
    ).scalar_one()

    saved_watermark = conn.execute(
        text("""
            SELECT update_timestamp
            FROM watermark
            WHERE pipeline = 'customer'
        """)
    ).scalar_one()

print("Production customers:", production_count)
print("Watermark:", saved_watermark)

# %%

# Author: Om Mohite

with production_engine.connect() as production_conn:
    production_df = pd.read_sql(
        text("""
            SELECT cust_id, customer_name, customer_email, update_on
            FROM customer
            ORDER BY cust_id
        """),
        production_conn,
    )

    watermark_df = pd.read_sql(
        text("""
            SELECT pipeline, update_timestamp
            FROM watermark
            WHERE pipeline = 'customer'
        """),
        production_conn,
    )

with staging_engine.connect() as staging_conn:
    staging_df = pd.read_sql(
        text("""
            SELECT cust_id, customer_name, customer_email
            FROM customer
            ORDER BY cust_id
        """),
        staging_conn,
    )

print("Staging rows:", len(staging_df))
print("Production rows:", len(production_df))
print("Watermark rows:", len(watermark_df))

display(production_df.head())
display(watermark_df)

assert len(staging_df) == 10
assert len(production_df) == len(staging_df)
assert production_df["cust_id"].tolist() == staging_df["cust_id"].tolist()
assert len(watermark_df) == 1
assert watermark_df.loc[0, "pipeline"] == "customer"

print("TEST CASE 15 INITIAL WATERMARK LOAD VALIDATION PASSED")

# %%

# Author: Om Mohite

import time

time.sleep(1.2)

with staging_engine.begin() as conn:
    conn.execute(
        text("""
            UPDATE customer
            SET customer_email = 'rahul.updated@gmail.com'
            WHERE cust_id = 1
        """)
    )

with staging_engine.connect() as conn:
    changed_record = conn.execute(
        text("""
            SELECT cust_id, customer_email, update_on
            FROM customer
            WHERE cust_id = 1
        """)
    ).one()

print("Updated staging record:", changed_record)

# %%

# Author: Om Mohite

with production_engine.begin() as conn:
    last_update = conn.execute(
        text("""
            SELECT update_timestamp
            FROM watermark
            WHERE pipeline = 'customer'
        """)
    ).scalar_one()

    conn.execute(
        text("""
            INSERT INTO test_case_15_production.customer
                (cust_id, customer_name, customer_email, update_on)
            SELECT
                cust_id, customer_name, customer_email, update_on
            FROM test_case_15_staging.customer
            WHERE update_on >= :last_update
            ON DUPLICATE KEY UPDATE
                customer_name = VALUES(customer_name),
                customer_email = VALUES(customer_email),
                update_on = VALUES(update_on)
        """),
        {"last_update": last_update},
    )

    max_update = conn.execute(
        text("SELECT MAX(update_on) FROM test_case_15_staging.customer")
    ).scalar_one()

    conn.execute(
        text("""
            UPDATE watermark
            SET update_timestamp = :max_update
            WHERE pipeline = 'customer'
        """),
        {"max_update": max_update},
    )

print("Watermark upsert rerun completed.")

# %%

# Author: Om Mohite

procedure_sql = """
CREATE PROCEDURE update_prod()
BEGIN
    DECLARE last_watermark DATETIME DEFAULT NULL;

    SELECT MAX(update_timestamp)
    INTO last_watermark
    FROM test_case_15_production.watermark
    WHERE pipeline = 'customer';

    INSERT INTO test_case_15_production.customer
        (cust_id, customer_name, customer_email, update_on)
    SELECT
        cust_id, customer_name, customer_email, update_on
    FROM test_case_15_staging.customer
    WHERE last_watermark IS NULL OR update_on > last_watermark
    ON DUPLICATE KEY UPDATE
        customer_name = VALUES(customer_name),
        customer_email = VALUES(customer_email),
        update_on = VALUES(update_on);

    INSERT INTO test_case_15_production.watermark
        (pipeline, update_timestamp)
    SELECT 'customer', MAX(update_on)
    FROM test_case_15_staging.customer
    ON DUPLICATE KEY UPDATE
        update_timestamp = VALUES(update_timestamp);
END
"""

with production_engine.connect() as conn:
    event_status = conn.execute(
        text("SHOW VARIABLES LIKE 'event_scheduler'")
    ).one()
    print("MySQL event scheduler:", event_status[1])

    if event_status[1].upper() != "ON":
        conn.exec_driver_sql("SET GLOBAL event_scheduler = ON")

with production_engine.begin() as conn:
    conn.exec_driver_sql("DROP EVENT IF EXISTS update_prod_event")
    conn.exec_driver_sql("DROP PROCEDURE IF EXISTS update_prod")
    conn.exec_driver_sql(procedure_sql)
    conn.exec_driver_sql("""
        CREATE EVENT update_prod_event
        ON SCHEDULE EVERY 10 MINUTE
        DO CALL update_prod()
    """)

    events = conn.execute(
        text("""
            SHOW EVENTS FROM test_case_15_production
            WHERE Name = 'update_prod_event'
        """)
    ).fetchall()

print("Scheduled events:", events)

# %%

# Author: Om Mohite

with production_engine.connect() as conn:
    scheduler_status = conn.execute(
        text("SELECT @@GLOBAL.event_scheduler")
    ).scalar_one()

    scheduled_events = pd.read_sql(
        text("""
            SELECT EVENT_NAME, STATUS, INTERVAL_VALUE, INTERVAL_FIELD
            FROM information_schema.EVENTS
            WHERE EVENT_SCHEMA = 'test_case_15_production'
              AND EVENT_NAME = 'update_prod_event'
        """),
        conn,
    )

    procedures = pd.read_sql(
        text("""
            SELECT ROUTINE_NAME
            FROM information_schema.ROUTINES
            WHERE ROUTINE_SCHEMA = 'test_case_15_production'
              AND ROUTINE_NAME = 'update_prod'
              AND ROUTINE_TYPE = 'PROCEDURE'
        """),
        conn,
    )

print("MySQL event scheduler:", scheduler_status)
print("Scheduled event:")
display(scheduled_events)
print("Stored procedure:")
display(procedures)

assert str(scheduler_status).upper() == "ON"
assert len(scheduled_events) == 1
assert scheduled_events.loc[0, "STATUS"] == "ENABLED"
assert len(procedures) == 1

print("TEST CASE 15 SCHEDULE VALIDATION PASSED")
