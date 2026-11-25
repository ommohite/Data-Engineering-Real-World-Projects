# Author: Om Mohite
# Test Case 18: Python export of the corresponding Jupyter notebook.
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
    conn.execute(text("CREATE DATABASE IF NOT EXISTS aggregation_test"))

server_engine.dispose()

database_url = URL.create(
    drivername="mysql+pymysql",
    username=os.getenv("DB_USER", "root"),
    password=db_password,
    host=os.getenv("DB_HOST", "localhost"),
    port=int(os.getenv("DB_PORT", "3306")),
    database="aggregation_test",
)

engine = create_engine(database_url, pool_pre_ping=True)

print("Database aggregation_test is ready.")

# %%

# Author: Om Mohite

import re
from pathlib import Path

sql_file = Path.cwd() / "test_case_18.sql"
if not sql_file.exists():
    raise FileNotFoundError(f"SQL file not found: {sql_file}")

sql_script = sql_file.read_text(encoding="utf-8")
load_statements = []

for statement in sql_script.split(";"):
    statement = statement.strip()

    if re.match(
        r"^(CREATE TABLE|INSERT INTO sales\b)",
        statement,
        re.IGNORECASE,
    ):
        load_statements.append(statement)

with engine.begin() as conn:
    conn.exec_driver_sql("DROP TABLE IF EXISTS sales")

    for statement in load_statements:
        conn.exec_driver_sql(statement)

with engine.connect() as conn:
    row_count = conn.execute(
        text("SELECT COUNT(*) FROM sales")
    ).scalar_one()

    date_range = conn.execute(
        text("SELECT MIN(sale_date), MAX(sale_date) FROM sales")
    ).one()

print("SQL file used:", sql_file.name)
print("Sales rows:", row_count)
print("Date range:", date_range[0], "to", date_range[1])

# %%

# Author: Om Mohite

region_summary_query = text("""
    SELECT
        region,
        SUM(total_amount) AS total_revenue,
        SUM(quantity) AS total_quantity,
        ROUND(AVG(total_amount), 2) AS average_sale,
        COUNT(*) AS total_transactions,
        MAX(total_amount) AS highest_sale,
        MIN(total_amount) AS lowest_sale
    FROM sales
    GROUP BY region
    ORDER BY total_revenue DESC
""")

with engine.connect() as conn:
    region_summary = pd.read_sql(region_summary_query, conn)

display(region_summary)

# %%

# Author: Om Mohite

yearly_region_query = text("""
    SELECT
        region,
        YEAR(sale_date) AS sale_year,
        SUM(total_amount) AS total_revenue
    FROM sales
    GROUP BY region, YEAR(sale_date)
    ORDER BY region, sale_year
""")

with engine.connect() as conn:
    yearly_region_revenue = pd.read_sql(yearly_region_query, conn)

display(yearly_region_revenue)

# %%

# Author: Om Mohite

monthly_region_query = text("""
    SELECT
        region,
        YEAR(sale_date) AS sale_year,
        MONTH(sale_date) AS sale_month,
        SUM(total_amount) AS total_revenue
    FROM sales
    GROUP BY region, YEAR(sale_date), MONTH(sale_date)
    ORDER BY region, sale_year, sale_month
""")

with engine.connect() as conn:
    monthly_region_revenue = pd.read_sql(monthly_region_query, conn)

display(monthly_region_revenue.head(20))

# %%

# Author: Om Mohite

product_performance_query = text("""
    SELECT
        product_id,
        SUM(quantity) AS total_quantity,
        SUM(total_amount) AS total_revenue
    FROM sales
    GROUP BY product_id
    ORDER BY total_revenue DESC
    LIMIT 10
""")

with engine.connect() as conn:
    top_products = pd.read_sql(product_performance_query, conn)

display(top_products)

# %%

# Author: Om Mohite

regional_pivot_query = text("""
    SELECT
        SUM(CASE WHEN region = 'North' THEN total_amount ELSE 0 END) AS north_revenue,
        SUM(CASE WHEN region = 'South' THEN total_amount ELSE 0 END) AS south_revenue,
        SUM(CASE WHEN region = 'East' THEN total_amount ELSE 0 END) AS east_revenue,
        SUM(CASE WHEN region = 'West' THEN total_amount ELSE 0 END) AS west_revenue,
        SUM(CASE WHEN region = 'Central' THEN total_amount ELSE 0 END) AS central_revenue
    FROM sales
""")

with engine.connect() as conn:
    regional_pivot = pd.read_sql(regional_pivot_query, conn)

display(regional_pivot)

# %%

# Author: Om Mohite

yearly_growth_query = text("""
    WITH yearly_revenue AS (
        SELECT
            YEAR(sale_date) AS sale_year,
            SUM(total_amount) AS total_revenue
        FROM sales
        GROUP BY YEAR(sale_date)
    ),
    revenue_with_previous_year AS (
        SELECT
            sale_year,
            total_revenue,
            LAG(total_revenue) OVER (ORDER BY sale_year) AS previous_year_revenue
        FROM yearly_revenue
    )
    SELECT
        sale_year,
        total_revenue,
        previous_year_revenue,
        ROUND(
            (total_revenue - previous_year_revenue)
            * 100.0 / NULLIF(previous_year_revenue, 0),
            2
        ) AS growth_percentage
    FROM revenue_with_previous_year
    ORDER BY sale_year
""")

with engine.connect() as conn:
    yearly_growth = pd.read_sql(yearly_growth_query, conn)

display(yearly_growth)

# %%

# Author: Om Mohite

index_definitions = {
    "idx_sales_region": "CREATE INDEX idx_sales_region ON sales(region)",
    "idx_sales_date": "CREATE INDEX idx_sales_date ON sales(sale_date)",
    "idx_sales_product": "CREATE INDEX idx_sales_product ON sales(product_id)",
    "idx_sales_customer": "CREATE INDEX idx_sales_customer ON sales(customer_id)",
    "idx_sales_region_date": (
        "CREATE INDEX idx_sales_region_date ON sales(region, sale_date)"
    ),
}

with engine.begin() as conn:
    existing_indexes = {
        row[2]
        for row in conn.exec_driver_sql("SHOW INDEX FROM sales").fetchall()
    }

    for index_name, create_sql in index_definitions.items():
        if index_name not in existing_indexes:
            conn.exec_driver_sql(create_sql)
            print("Created:", index_name)
        else:
            print("Already exists:", index_name)

print("Index setup complete.")

# %%

# Author: Om Mohite

explain_aggregation_query = text("""
    EXPLAIN
    SELECT
        region,
        SUM(total_amount) AS total_revenue
    FROM sales
    WHERE sale_date >= '2025-01-01'
      AND sale_date < '2026-01-01'
    GROUP BY region
""")

with engine.connect() as conn:
    aggregation_plan = pd.read_sql(explain_aggregation_query, conn)

display(aggregation_plan)

# %%

# Author: Om Mohite

with engine.begin() as conn:
    conn.exec_driver_sql("DROP TABLE IF EXISTS sales_partitioned")

    conn.exec_driver_sql("""
        CREATE TABLE sales_partitioned (
            sale_id INT NOT NULL,
            sale_date DATE NOT NULL,
            region VARCHAR(50) NOT NULL,
            product_id INT NOT NULL,
            customer_id INT NOT NULL,
            quantity INT NOT NULL,
            unit_price DECIMAL(10,2) NOT NULL,
            total_amount DECIMAL(12,2) NOT NULL,
            PRIMARY KEY (sale_id, sale_date)
        )
        PARTITION BY RANGE COLUMNS (sale_date) (
            PARTITION p2023 VALUES LESS THAN ('2024-01-01'),
            PARTITION p2024 VALUES LESS THAN ('2025-01-01'),
            PARTITION p2025 VALUES LESS THAN ('2026-01-01'),
            PARTITION p2026 VALUES LESS THAN ('2027-01-01'),
            PARTITION p_future VALUES LESS THAN (MAXVALUE)
        )
    """)

    conn.exec_driver_sql("""
        INSERT INTO sales_partitioned
        SELECT *
        FROM sales
    """)

    partitioned_count = conn.execute(
        text("SELECT COUNT(*) FROM sales_partitioned")
    ).scalar_one()

print("Rows copied to partitioned table:", partitioned_count)

# %%

# Author: Om Mohite

partition_info_query = text("""
    SELECT
        PARTITION_NAME,
        TABLE_ROWS
    FROM INFORMATION_SCHEMA.PARTITIONS
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_NAME = 'sales_partitioned'
    ORDER BY PARTITION_ORDINAL_POSITION
""")

with engine.connect() as conn:
    partition_info = pd.read_sql(partition_info_query, conn)

display(partition_info)

# %%

# Author: Om Mohite

partitioned_revenue_query = text("""
    SELECT
        region,
        SUM(total_amount) AS total_revenue
    FROM sales_partitioned
    WHERE sale_date >= '2025-01-01'
      AND sale_date < '2026-01-01'
    GROUP BY region
    ORDER BY total_revenue DESC
""")

with engine.connect() as conn:
    partitioned_revenue = pd.read_sql(partitioned_revenue_query, conn)

display(partitioned_revenue)

# %%

# Author: Om Mohite

partitioned_explain_query = text("""
    EXPLAIN
    SELECT
        region,
        SUM(total_amount) AS total_revenue
    FROM sales_partitioned
    WHERE sale_date >= '2025-01-01'
      AND sale_date < '2026-01-01'
    GROUP BY region
""")

with engine.connect() as conn:
    partitioned_plan = pd.read_sql(partitioned_explain_query, conn)

display(partitioned_plan)

# %%

# Author: Om Mohite

with engine.begin() as conn:
    for shard_name in ["sales_shard_1", "sales_shard_2", "sales_shard_3"]:
        conn.exec_driver_sql(f"DROP TABLE IF EXISTS {shard_name}")
        conn.exec_driver_sql(
            f"CREATE TABLE {shard_name} LIKE sales"
        )

    conn.exec_driver_sql("""
        INSERT INTO sales_shard_1
        SELECT * FROM sales
        WHERE MOD(sale_id, 3) = 0
    """)

    conn.exec_driver_sql("""
        INSERT INTO sales_shard_2
        SELECT * FROM sales
        WHERE MOD(sale_id, 3) = 1
    """)

    conn.exec_driver_sql("""
        INSERT INTO sales_shard_3
        SELECT * FROM sales
        WHERE MOD(sale_id, 3) = 2
    """)

    shard_counts = {
        shard_name: conn.execute(
            text(f"SELECT COUNT(*) FROM {shard_name}")
        ).scalar_one()
        for shard_name in ["sales_shard_1", "sales_shard_2", "sales_shard_3"]
    }

print("Rows per shard:", shard_counts)
print("Total sharded rows:", sum(shard_counts.values()))

# %%

# Author: Om Mohite

sharded_monthly_query = text("""
    SELECT
        YEAR(sale_date) AS sale_year,
        MONTH(sale_date) AS sale_month,
        SUM(total_amount) AS total_revenue
    FROM (
        SELECT sale_date, total_amount FROM sales_shard_1
        UNION ALL
        SELECT sale_date, total_amount FROM sales_shard_2
        UNION ALL
        SELECT sale_date, total_amount FROM sales_shard_3
    ) AS combined_sales
    GROUP BY YEAR(sale_date), MONTH(sale_date)
    ORDER BY sale_year, sale_month
""")

with engine.connect() as conn:
    sharded_monthly_revenue = pd.read_sql(sharded_monthly_query, conn)

display(sharded_monthly_revenue.head(20))

# %%



top_regions_query = text("""
    SELECT
        region,
        SUM(total_amount) AS total_revenue
    FROM sales
    GROUP BY region
    ORDER BY total_revenue DESC
    LIMIT 5
""")

with engine.connect() as conn:
    top_regions = pd.read_sql(top_regions_query, conn)

display(top_regions)

# %%

# Author: Om Mohite

regional_share_query = text("""
    SELECT
        region,
        SUM(total_amount) AS total_revenue,
        ROUND(
            SUM(total_amount) * 100.0
            / (SELECT SUM(total_amount) FROM sales),
            2
        ) AS revenue_percentage
    FROM sales
    GROUP BY region
    ORDER BY revenue_percentage DESC
""")

with engine.connect() as conn:
    regional_revenue_share = pd.read_sql(regional_share_query, conn)

display(regional_revenue_share)

# %%

# Author: Om Mohite

top_products_by_quantity_query = text("""
    SELECT
        product_id,
        SUM(quantity) AS total_quantity
    FROM sales
    GROUP BY product_id
    ORDER BY total_quantity DESC
    LIMIT 10
""")

with engine.connect() as conn:
    top_products_by_quantity = pd.read_sql(
        top_products_by_quantity_query,
        conn,
    )

display(top_products_by_quantity)

# %%

# Author: Om Mohite

best_month_query = text("""
    WITH monthly_revenue AS (
        SELECT
            YEAR(sale_date) AS sale_year,
            MONTH(sale_date) AS sale_month,
            SUM(total_amount) AS total_revenue
        FROM sales
        GROUP BY YEAR(sale_date), MONTH(sale_date)
    ),
    ranked_months AS (
        SELECT
            sale_year,
            sale_month,
            total_revenue,
            RANK() OVER (
                PARTITION BY sale_year
                ORDER BY total_revenue DESC
            ) AS revenue_rank
        FROM monthly_revenue
    )
    SELECT
        sale_year,
        sale_month,
        total_revenue
    FROM ranked_months
    WHERE revenue_rank = 1
    ORDER BY sale_year
""")

with engine.connect() as conn:
    best_month_by_year = pd.read_sql(best_month_query, conn)

display(best_month_by_year)

# %%

# Author: Om Mohite

cumulative_revenue_query = text("""
    SELECT
        sale_date,
        SUM(total_amount) AS daily_revenue,
        SUM(SUM(total_amount)) OVER (
            ORDER BY sale_date
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS cumulative_revenue
    FROM sales
    GROUP BY sale_date
    ORDER BY sale_date
""")

with engine.connect() as conn:
    cumulative_revenue = pd.read_sql(cumulative_revenue_query, conn)

display(cumulative_revenue.head(20))

# %%

# Author: Om Mohite

moving_average_query = text("""
    WITH monthly_revenue AS (
        SELECT
            YEAR(sale_date) AS sale_year,
            MONTH(sale_date) AS sale_month,
            SUM(total_amount) AS monthly_revenue
        FROM sales
        GROUP BY YEAR(sale_date), MONTH(sale_date)
    )
    SELECT
        sale_year,
        sale_month,
        monthly_revenue,
        ROUND(
            AVG(monthly_revenue) OVER (
                ORDER BY sale_year, sale_month
                ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
            ),
            2
        ) AS three_month_moving_average
    FROM monthly_revenue
    ORDER BY sale_year, sale_month
""")

with engine.connect() as conn:
    monthly_moving_average = pd.read_sql(moving_average_query, conn)

display(monthly_moving_average.head(20))

# %%

# Author: Om Mohite

high_spending_customers_query = text("""
    WITH customer_revenue AS (
        SELECT
            customer_id,
            SUM(total_amount) AS total_spending
        FROM sales
        GROUP BY customer_id
    )
    SELECT
        customer_id,
        total_spending
    FROM customer_revenue
    WHERE total_spending > (
        SELECT AVG(total_spending)
        FROM customer_revenue
    )
    ORDER BY total_spending DESC
""")

with engine.connect() as conn:
    high_spending_customers = pd.read_sql(
        high_spending_customers_query,
        conn,
    )

display(high_spending_customers)

# %%

# Author: Om Mohite

base_analyze_query = text("""
    EXPLAIN ANALYZE
    SELECT
        region,
        SUM(total_amount) AS total_revenue
    FROM sales
    WHERE sale_date >= '2025-01-01'
      AND sale_date < '2026-01-01'
    GROUP BY region
""")

partitioned_analyze_query = text("""
    EXPLAIN ANALYZE
    SELECT
        region,
        SUM(total_amount) AS total_revenue
    FROM sales_partitioned
    WHERE sale_date >= '2025-01-01'
      AND sale_date < '2026-01-01'
    GROUP BY region
""")

with engine.connect() as conn:
    base_execution_plan = pd.read_sql(base_analyze_query, conn)
    partitioned_execution_plan = pd.read_sql(partitioned_analyze_query, conn)

print("Base table execution plan:")
display(base_execution_plan)

print("Partitioned table execution plan:")
display(partitioned_execution_plan)

# %%

# Author: Om Mohite

with engine.connect() as conn:
    base_count = conn.execute(
        text("SELECT COUNT(*) FROM sales")
    ).scalar_one()

    partitioned_count = conn.execute(
        text("SELECT COUNT(*) FROM sales_partitioned")
    ).scalar_one()

    shard_count = conn.execute(text("""
        SELECT
            (SELECT COUNT(*) FROM sales_shard_1) +
            (SELECT COUNT(*) FROM sales_shard_2) +
            (SELECT COUNT(*) FROM sales_shard_3)
    """)).scalar_one()

    base_revenue = conn.execute(
        text("SELECT SUM(total_amount) FROM sales")
    ).scalar_one()

    partitioned_revenue_total = conn.execute(
        text("SELECT SUM(total_amount) FROM sales_partitioned")
    ).scalar_one()

    sharded_revenue_total = conn.execute(text("""
        SELECT SUM(total_amount)
        FROM (
            SELECT total_amount FROM sales_shard_1
            UNION ALL
            SELECT total_amount FROM sales_shard_2
            UNION ALL
            SELECT total_amount FROM sales_shard_3
        ) AS all_shards
    """)).scalar_one()

print("Base table rows:", base_count)
print("Partitioned table rows:", partitioned_count)
print("Sharded rows:", shard_count)
print("Base revenue:", base_revenue)
print("Partitioned revenue:", partitioned_revenue_total)
print("Sharded revenue:", sharded_revenue_total)

assert base_count == 100000
assert partitioned_count == base_count
assert shard_count == base_count
assert base_revenue == partitioned_revenue_total == sharded_revenue_total
assert len(region_summary) == 5

print("TEST CASE 18 AGGREGATION AND SCALING VALIDATION PASSED")
