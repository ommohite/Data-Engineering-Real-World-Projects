# Author: Om Mohite
# Test Case 16: SQL data quality checks and issue logging.

import os
import re
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import URL, create_engine, text


BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = Path(__file__).resolve().parents[2]
SQL_FILE = BASE_DIR / "test_case_16.sql"
DATABASE_NAME = "test_case_16"


QUALITY_RULES = {
    "missing_customer_id": {
        "query": "SELECT COUNT(*) FROM sales WHERE customer_id IS NULL",
        "severity": "HIGH",
    },
    "missing_order_date": {
        "query": "SELECT COUNT(*) FROM sales WHERE order_date IS NULL",
        "severity": "HIGH",
    },
    "duplicate_sale_id": {
        "query": """
            SELECT COUNT(*)
            FROM (
                SELECT sale_id
                FROM sales
                GROUP BY sale_id
                HAVING COUNT(*) > 1
            ) AS duplicate_groups
        """,
        "severity": "HIGH",
    },
    "invalid_quantity": {
        "query": "SELECT COUNT(*) FROM sales WHERE quantity IS NULL OR quantity <= 0",
        "severity": "HIGH",
    },
    "negative_price": {
        "query": "SELECT COUNT(*) FROM sales WHERE unit_price < 0",
        "severity": "MEDIUM",
    },
    "inconsistent_total_amount": {
        "query": """
            SELECT COUNT(*)
            FROM sales
            WHERE total_amount IS NULL
               OR quantity IS NULL
               OR unit_price IS NULL
               OR ABS(total_amount - (quantity * unit_price)) > 0.01
        """,
        "severity": "HIGH",
    },
}


def create_database_engine():
    load_dotenv(PROJECT_ROOT / ".env")

    db_password = os.getenv("DB_PASSWORD")
    if not db_password:
        raise ValueError("Set DB_PASSWORD in the project .env file.")

    server_url = URL.create(
        drivername="mysql+pymysql",
        username=os.getenv("DB_USER", "root"),
        password=db_password,
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "3306")),
    )
    server_engine = create_engine(server_url, pool_pre_ping=True)

    try:
        with server_engine.begin() as conn:
            conn.execute(text(f"CREATE DATABASE IF NOT EXISTS `{DATABASE_NAME}`"))
    finally:
        server_engine.dispose()

    database_url = URL.create(
        drivername="mysql+pymysql",
        username=os.getenv("DB_USER", "root"),
        password=db_password,
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "3306")),
        database=DATABASE_NAME,
    )
    return create_engine(database_url, pool_pre_ping=True)


def load_seed_data(engine):
    if not SQL_FILE.exists():
        raise FileNotFoundError(f"SQL seed file not found: {SQL_FILE}")

    sql_script = SQL_FILE.read_text(encoding="utf-8")
    load_statements = []

    for statement in sql_script.split(";"):
        statement = statement.strip()
        if re.match(r"^(CREATE TABLE|INSERT INTO sales\b)", statement, re.IGNORECASE):
            load_statements.append(statement)

    if not load_statements:
        raise ValueError(f"No sales table or seed statements found in {SQL_FILE.name}")

    # This test fixture is reset on each run so the sample results stay repeatable.
    with engine.begin() as conn:
        conn.exec_driver_sql("DROP TABLE IF EXISTS data_quality_issues")
        conn.exec_driver_sql("DROP TABLE IF EXISTS sales")
        for statement in load_statements:
            conn.exec_driver_sql(statement)


def collect_quality_issues(engine):
    issues = []

    with engine.connect() as conn:
        for rule_name, rule_details in QUALITY_RULES.items():
            failed_records = conn.execute(
                text(rule_details["query"])
            ).scalar_one()

            if failed_records > 0:
                issues.append(
                    {
                        "pipeline_name": "sales_pipeline",
                        "table_name": "sales",
                        "rule_name": rule_name,
                        "severity": rule_details["severity"],
                        "failed_records": int(failed_records),
                    }
                )

    return issues


def save_quality_issues(engine, issues):
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM data_quality_issues"))

        if issues:
            conn.execute(
                text("""
                    INSERT INTO data_quality_issues
                        (pipeline_name, table_name, rule_name, severity, failed_records)
                    VALUES
                        (:pipeline_name, :table_name, :rule_name, :severity, :failed_records)
                """),
                issues,
            )


def main():
    engine = create_database_engine()

    try:
        load_seed_data(engine)

        with engine.connect() as conn:
            sales_df = pd.read_sql(
                text("SELECT * FROM sales ORDER BY sale_id"),
                conn,
            )

        print("SQL file used:", SQL_FILE.name)
        print("Sales rows:", len(sales_df))
        print("Missing values by column:")
        print(sales_df.isna().sum().to_string())

        issues = collect_quality_issues(engine)
        save_quality_issues(engine, issues)

        with engine.connect() as conn:
            saved_issues = pd.read_sql(
                text("""
                    SELECT
                        pipeline_name,
                        table_name,
                        rule_name,
                        severity,
                        failed_records,
                        status
                    FROM data_quality_issues
                    ORDER BY issue_id
                """),
                conn,
            )

        print("Quality rules with failures:", len(issues))
        print("Issue records saved:", len(saved_issues))
        print(saved_issues.to_string(index=False))
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
