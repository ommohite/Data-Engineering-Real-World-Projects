# Author: Om Mohite
# Test Case 13: Python export of the corresponding Jupyter notebook.
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
    conn.execute(text("CREATE DATABASE IF NOT EXISTS test_case_13"))

server_engine.dispose()

connection_url = URL.create(
    drivername="mysql+pymysql",
    username=os.getenv("DB_USER", "root"),
    password=db_password,
    host=os.getenv("DB_HOST", "localhost"),
    port=int(os.getenv("DB_PORT", "3306")),
    database="test_case_13",
)

engine = create_engine(connection_url, pool_pre_ping=True)

print("Database test_case_13 is ready.")

# %%

# Author: Om Mohite

import re
from pathlib import Path

sql_candidates = [
    Path.cwd() / "test_case_13.sql",
    Path(__file__).resolve().parent,
]

sql_file = next((path for path in sql_candidates if path.is_file()), None)
if sql_file is None:
    raise FileNotFoundError("Could not find test_case_13.sql")

sql_script = sql_file.read_text(encoding="utf-8")
statements = []

for statement in sql_script.split(";"):
    cleaned_statement = re.sub(
        r"(?m)^\s*--.*(?:\n|$)",
        "",
        statement,
    ).strip()

    if re.match(
        r"^(CREATE TABLE|INSERT INTO employees\b)",
        cleaned_statement,
        re.IGNORECASE,
    ):
        statements.append(cleaned_statement)

with engine.begin() as conn:
    conn.exec_driver_sql("DROP TABLE IF EXISTS employees")

    for statement in statements:
        conn.exec_driver_sql(statement)

with engine.connect() as conn:
    employee_count = conn.execute(
        text("SELECT COUNT(*) FROM employees")
    ).scalar_one()

print("SQL file used:", sql_file.name)
print("Employees loaded:", employee_count)

# %%

# Author: Om Mohite

manager_chain_query = text("""
    WITH RECURSIVE manager_chain AS (
        SELECT
            employee_id,
            employee_name,
            job_title,
            department,
            manager_id,
            salary,
            0 AS hierarchy_level
        FROM employees
        WHERE employee_id = :employee_id

        UNION ALL

        SELECT
            e.employee_id,
            e.employee_name,
            e.job_title,
            e.department,
            e.manager_id,
            e.salary,
            mc.hierarchy_level + 1
        FROM employees AS e
        JOIN manager_chain AS mc
            ON e.employee_id = mc.manager_id
    )
    SELECT *
    FROM manager_chain
    ORDER BY hierarchy_level
""")

with engine.connect() as conn:
    employee_17_chain = pd.read_sql(
        manager_chain_query,
        conn,
        params={"employee_id": 17},
    )

display(employee_17_chain)

# %%

# Author: Om Mohite

hierarchy_query = text("""
    WITH RECURSIVE employee_hierarchy AS (
        SELECT
            employee_id,
            employee_name,
            job_title,
            department,
            manager_id,
            salary,
            0 AS hierarchy_level
        FROM employees
        WHERE manager_id IS NULL

        UNION ALL

        SELECT
            e.employee_id,
            e.employee_name,
            e.job_title,
            e.department,
            e.manager_id,
            e.salary,
            eh.hierarchy_level + 1
        FROM employees AS e
        JOIN employee_hierarchy AS eh
            ON e.manager_id = eh.employee_id
    )
    SELECT *
    FROM employee_hierarchy
    ORDER BY hierarchy_level, employee_id
""")

with engine.connect() as conn:
    employee_hierarchy = pd.read_sql(hierarchy_query, conn)

display(employee_hierarchy)

# %%

# Author: Om Mohite

with engine.connect() as conn:
    employee_2_chain = pd.read_sql(
        manager_chain_query,
        conn,
        params={"employee_id": 2},
    )

expected_employee_17_chain = [17, 15, 4, 1]
expected_employee_2_chain = [2, 1]

assert employee_17_chain["employee_id"].tolist() == expected_employee_17_chain
assert employee_2_chain["employee_id"].tolist() == expected_employee_2_chain
assert len(employee_hierarchy) == 17
assert employee_hierarchy["employee_id"].nunique() == 17
assert employee_hierarchy["hierarchy_level"].max() == 3
assert employee_hierarchy.loc[
    employee_hierarchy["hierarchy_level"] == 0, "employee_name"
].tolist() == ["Robert"]

print("Employee 17 chain:", employee_17_chain["employee_id"].tolist())
print("Employee 2 chain:", employee_2_chain["employee_id"].tolist())
print("Hierarchy rows:", len(employee_hierarchy))
print("Maximum hierarchy level:", employee_hierarchy["hierarchy_level"].max())
print("TEST CASE 13 RECURSIVE CTE VALIDATION PASSED")
