# Author: Om Mohite
# Test Case 11: Python export of the corresponding Jupyter notebook.
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
import requests
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
    conn.execute(text("CREATE DATABASE IF NOT EXISTS test_case_11"))

server_engine.dispose()

connection_url = URL.create(
    drivername="mysql+pymysql",
    username=os.getenv("DB_USER", "root"),
    password=db_password,
    host=os.getenv("DB_HOST", "localhost"),
    port=int(os.getenv("DB_PORT", "3306")),
    database="test_case_11",
)

engine = create_engine(connection_url, pool_pre_ping=True)

print("Database test_case_11 is ready.")

# %%

# Author: Om Mohite

api_url = "https://jsonplaceholder.typicode.com/posts"

response = requests.get(api_url, timeout=30)
response.raise_for_status()

posts_data = response.json()
posts_df = pd.json_normalize(posts_data)

print("HTTP status:", response.status_code)
print("Records fetched:", len(posts_df))
print("Columns:", posts_df.columns.tolist())

display(posts_df.head())

# %%

# Author: Om Mohite

clean_posts_df = posts_df.copy()

print("Missing values before cleaning:")
display(clean_posts_df.isna().sum().to_frame("missing_count"))

clean_posts_df["userId"] = clean_posts_df["userId"].fillna(0).astype(int)
clean_posts_df["id"] = clean_posts_df["id"].fillna(0).astype(int)
clean_posts_df["title"] = clean_posts_df["title"].fillna("Unknown")
clean_posts_df["body"] = clean_posts_df["body"].fillna("Unknown")

print("Missing values after cleaning:")
display(clean_posts_df.isna().sum().to_frame("missing_count"))

display(clean_posts_df.head())

# %%

# Author: Om Mohite

clean_posts_df.to_sql(
    name="web_data",
    con=engine,
    if_exists="replace",
    index=False,
    chunksize=100,
    method="multi",
)

with engine.connect() as conn:
    loaded_count = conn.execute(
        text("SELECT COUNT(*) FROM web_data")
    ).scalar_one()

print("Rows loaded into MySQL:", loaded_count)

# %%

# Author: Om Mohite

with engine.connect() as conn:
    loaded_df = pd.read_sql(
        text("""
            SELECT userId, id, title, body
            FROM web_data
            ORDER BY id
        """),
        conn,
    )

print("Rows in MySQL:", len(loaded_df))
print("Missing values:", loaded_df.isna().sum().sum())
print("Unique post IDs:", loaded_df["id"].nunique())

display(loaded_df.head())

assert len(loaded_df) == 100
assert loaded_df.isna().sum().sum() == 0
assert loaded_df["id"].nunique() == 100

print("TEST CASE 11 API ETL VALIDATION PASSED")
