"""Extract sales records from the sales analytics MySQL database."""

import os

import pandas as pd
from sqlalchemy import URL, create_engine


def create_source_engine():
    """Build a MySQL engine from environment variables without embedding secrets."""
    password = os.getenv("DB_PASSWORD") or os.getenv("MYSQL_PASSWORD")
    if not password:
        raise RuntimeError("Set DB_PASSWORD in the environment or .env file.")
    url = URL.create(
        "mysql+pymysql",
        username=os.getenv("DB_USER", "root"),
        password=password,
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "3306")),
        database=os.getenv("DB_NAME", "sales_analytics"),
    )
    return create_engine(url, pool_pre_ping=True)


def data_extraction(engine=None) -> pd.DataFrame:
    """Read all rows from sales_source; caller owns disposal if it supplies engine."""
    own_engine = engine is None
    engine = engine or create_source_engine()
    try:
        sales = pd.read_sql("SELECT * FROM sales_source", engine)
        if sales.empty:
            raise ValueError("sales_source returned no records.")
        return sales
    except Exception as exc:
        raise RuntimeError(f"Could not extract sales_source: {exc}") from exc
    finally:
        if own_engine:
            engine.dispose()
