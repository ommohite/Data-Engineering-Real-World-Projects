# Author: Om Mohite
# Test Case 10: Python export of the corresponding Jupyter notebook.
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
    conn.execute(text("CREATE DATABASE IF NOT EXISTS test_case_10"))

server_engine.dispose()

connection_url = URL.create(
    drivername="mysql+pymysql",
    username=os.getenv("DB_USER", "root"),
    password=db_password,
    host=os.getenv("DB_HOST", "localhost"),
    port=int(os.getenv("DB_PORT", "3306")),
    database="test_case_10",
)

engine = create_engine(connection_url, pool_pre_ping=True)

with engine.begin() as conn:
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS stream_events (
            event_id BIGINT PRIMARY KEY AUTO_INCREMENT,
            device_id VARCHAR(50) NOT NULL,
            metric_name VARCHAR(50) NOT NULL,
            metric_value DECIMAL(10,2) NOT NULL,
            event_time DATETIME NOT NULL,
            received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """))

with engine.connect() as conn:
    print("Connected to test_case_10")
    print("Tables:", conn.execute(text("SHOW TABLES")).fetchall())

# %%

# Author: Om Mohite

import random
import time
from datetime import datetime
from sqlalchemy import text

random.seed(42)

def generate_events(total_events=12):
    for _ in range(total_events):
        yield {
            "device_id": f"sensor_{random.randint(1, 3)}",
            "metric_name": "temperature",
            "metric_value": round(random.uniform(65, 85), 2),
            "event_time": datetime.now(),
        }

insert_sql = text("""
    INSERT INTO stream_events
        (device_id, metric_name, metric_value, event_time)
    VALUES
        (:device_id, :metric_name, :metric_value, :event_time)
""")

for event in generate_events():
    with engine.begin() as conn:
        conn.execute(insert_sql, event)

    print(
        event["device_id"],
        event["metric_name"],
        event["metric_value"],
        event["event_time"].strftime("%H:%M:%S"),
    )
    time.sleep(0.3)

with engine.connect() as conn:
    total_rows = conn.execute(
        text("SELECT COUNT(*) FROM stream_events")
    ).scalar_one()

print("Total events stored:", total_rows)

# %%

# Author: Om Mohite

import pandas as pd
from sqlalchemy import text

aggregation_query = text("""
    SELECT
        device_id,
        metric_name,
        COUNT(*) AS event_count,
        ROUND(AVG(metric_value), 2) AS average_value,
        ROUND(MAX(metric_value), 2) AS maximum_value
    FROM stream_events
    GROUP BY device_id, metric_name
    ORDER BY device_id, metric_name
""")

with engine.connect() as conn:
    device_summary = pd.read_sql(aggregation_query, conn)

display(device_summary)

# %%

# Author: Om Mohite

alert_threshold = 80

alert_query = text("""
    SELECT
        event_id,
        device_id,
        metric_name,
        metric_value,
        event_time
    FROM stream_events
    WHERE metric_name = 'temperature'
      AND metric_value > :threshold
    ORDER BY event_time DESC
""")

with engine.connect() as conn:
    alerts = pd.read_sql(
        alert_query,
        conn,
        params={"threshold": alert_threshold},
    )

if alerts.empty:
    print(f"No temperature alerts. Threshold: {alert_threshold}")
else:
    print(f"ALERT: Temperature exceeded {alert_threshold}")
    display(alerts)

# %%

# Author: Om Mohite

with engine.connect() as conn:
    total_events = conn.execute(
        text("SELECT COUNT(*) FROM stream_events")
    ).scalar_one()

    aggregated_devices = conn.execute(text("""
        SELECT COUNT(*)
        FROM (
            SELECT device_id
            FROM stream_events
            GROUP BY device_id
        ) AS device_groups
    """)).scalar_one()

    alert_count = conn.execute(
        text("""
            SELECT COUNT(*)
            FROM stream_events
            WHERE metric_name = 'temperature'
              AND metric_value > :threshold
        """),
        {"threshold": alert_threshold},
    ).scalar_one()

print("Events stored:", total_events)
print("Devices aggregated:", aggregated_devices)
print("Alerts detected:", alert_count)

assert total_events >= 12
assert aggregated_devices >= 1
assert alert_count == len(alerts)

print("TEST CASE 10 REAL-TIME ANALYTICS VALIDATION PASSED")
