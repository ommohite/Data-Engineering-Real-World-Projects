# Author: Om Mohite
# Test Case 19: Python export of the corresponding Jupyter notebook.
# Run from this folder; configure DB_PASSWORD/DB_USER/DB_HOST/DB_PORT as needed.

import os
from pathlib import Path
from getpass import getpass

try:
    from IPython.display import display
except ImportError:
    display = print

import os
import getpass
from sqlalchemy import URL, create_engine, text

db_password = os.getenv("DB_PASSWORD") or getpass.getpass("MySQL password: ")

server_url = URL.create(
    drivername="mysql+pymysql",
    username=os.getenv("DB_USER", "root"),
    password=db_password,
    host=os.getenv("DB_HOST", "localhost"),
    port=int(os.getenv("DB_PORT", "3306")),
)

server_engine = create_engine(server_url, pool_pre_ping=True)

with server_engine.connect() as conn:
    databases = conn.execute(text("SHOW DATABASES")).scalars().all()

print("Available databases:", databases)

# %%

from sqlalchemy import URL, create_engine, text
import pandas as pd

connection_url = URL.create(
    drivername="mysql+pymysql",
    username=os.getenv("DB_USER", "root"),
    password=db_password,
    host=os.getenv("DB_HOST", "localhost"),
    port=int(os.getenv("DB_PORT", "3306")),
    database="aggregation_test",
)

engine = create_engine(connection_url, pool_pre_ping=True)

with engine.connect() as conn:
    tables = conn.execute(text("SHOW TABLES")).all()

print("Tables:", tables)

# %%

with engine.connect() as conn:
    columns = pd.read_sql(
        text("""
            SELECT COLUMN_NAME, DATA_TYPE
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
              AND TABLE_NAME = 'sales'
            ORDER BY ORDINAL_POSITION
        """),
        conn,
    )

    sample_rows = pd.read_sql(
        text("SELECT * FROM sales LIMIT 5"),
        conn,
    )

display(columns)
display(sample_rows)

# %%

anomaly_query = text("""
    WITH daily_sales AS (
        SELECT
            sale_date,
            region,
            SUM(total_amount) AS daily_revenue
        FROM sales
        GROUP BY sale_date, region
    ),
    regional_stats AS (
        SELECT
            region,
            AVG(daily_revenue) AS avg_revenue,
            STDDEV_SAMP(daily_revenue) AS stddev_revenue
        FROM daily_sales
        GROUP BY region
    ),
    scored_sales AS (
        SELECT
            d.sale_date,
            d.region,
            d.daily_revenue,
            s.avg_revenue,
            s.stddev_revenue,
            (d.daily_revenue - s.avg_revenue)
                / NULLIF(s.stddev_revenue, 0) AS z_score
        FROM daily_sales AS d
        JOIN regional_stats AS s
          ON d.region = s.region
    )
    SELECT
        sale_date,
        region,
        daily_revenue,
        ROUND(avg_revenue, 2) AS avg_revenue,
        ROUND(z_score, 2) AS z_score
    FROM scored_sales
    WHERE ABS(z_score) >= 3
    ORDER BY ABS(z_score) DESC
""")

with engine.connect() as conn:
    anomalies = pd.read_sql(anomaly_query, conn)

print("Anomalous region-days found:", len(anomalies))
display(anomalies.head(20))

# %%

rolling_query = text("""
    WITH daily_sales AS (
        SELECT
            sale_date,
            region,
            SUM(total_amount) AS daily_revenue
        FROM sales
        GROUP BY sale_date, region
    ),
    rolling_baseline AS (
        SELECT
            sale_date,
            region,
            daily_revenue,
            COUNT(*) OVER (
                PARTITION BY region
                ORDER BY sale_date
                ROWS BETWEEN 7 PRECEDING AND 1 PRECEDING
            ) AS history_days,
            AVG(daily_revenue) OVER (
                PARTITION BY region
                ORDER BY sale_date
                ROWS BETWEEN 7 PRECEDING AND 1 PRECEDING
            ) AS avg_previous_7_days,
            STDDEV_SAMP(daily_revenue) OVER (
                PARTITION BY region
                ORDER BY sale_date
                ROWS BETWEEN 7 PRECEDING AND 1 PRECEDING
            ) AS stddev_previous_7_days
        FROM daily_sales
    ),
    scored AS (
        SELECT
            *,
            (daily_revenue - avg_previous_7_days)
                / NULLIF(stddev_previous_7_days, 0) AS rolling_z_score
        FROM rolling_baseline
        WHERE history_days = 7
    )
    SELECT
        sale_date,
        region,
        daily_revenue,
        ROUND(avg_previous_7_days, 2) AS avg_previous_7_days,
        ROUND(rolling_z_score, 2) AS rolling_z_score,
        CASE
            WHEN ABS(rolling_z_score) >= 3 THEN 'ANOMALY'
            ELSE 'NORMAL'
        END AS anomaly_status
    FROM scored
    WHERE stddev_previous_7_days > 0
    ORDER BY ABS(rolling_z_score) DESC
    LIMIT 20
""")

with engine.connect() as conn:
    rolling_results = pd.read_sql(rolling_query, conn)

display(rolling_results)

# %%

anomaly_summary_query = text("""
    WITH daily_sales AS (
        SELECT
            sale_date,
            region,
            SUM(total_amount) AS daily_revenue
        FROM sales
        GROUP BY sale_date, region
    ),
    rolling_baseline AS (
        SELECT
            sale_date,
            region,
            daily_revenue,
            COUNT(*) OVER (
                PARTITION BY region
                ORDER BY sale_date
                ROWS BETWEEN 7 PRECEDING AND 1 PRECEDING
            ) AS history_days,
            AVG(daily_revenue) OVER (
                PARTITION BY region
                ORDER BY sale_date
                ROWS BETWEEN 7 PRECEDING AND 1 PRECEDING
            ) AS avg_previous_7_days,
            STDDEV_SAMP(daily_revenue) OVER (
                PARTITION BY region
                ORDER BY sale_date
                ROWS BETWEEN 7 PRECEDING AND 1 PRECEDING
            ) AS stddev_previous_7_days
        FROM daily_sales
    ),
    scored AS (
        SELECT
            region,
            daily_revenue,
            (daily_revenue - avg_previous_7_days)
                / NULLIF(stddev_previous_7_days, 0) AS rolling_z_score
        FROM rolling_baseline
        WHERE history_days = 7
          AND stddev_previous_7_days > 0
    )
    SELECT
        region,
        COUNT(*) AS evaluated_days,
        SUM(CASE WHEN ABS(rolling_z_score) >= 3 THEN 1 ELSE 0 END)
            AS anomaly_days,
        ROUND(MAX(ABS(rolling_z_score)), 2) AS largest_abs_z_score
    FROM scored
    GROUP BY region
    ORDER BY anomaly_days DESC, region
""")

with engine.connect() as conn:
    anomaly_summary = pd.read_sql(anomaly_summary_query, conn)

display(anomaly_summary)

# %%

iqr_query = text("""
    WITH daily_sales AS (
        SELECT
            sale_date,
            region,
            SUM(total_amount) AS daily_revenue
        FROM sales
        GROUP BY sale_date, region
    ),
    ranked_sales AS (
        SELECT
            sale_date,
            region,
            daily_revenue,
            NTILE(4) OVER (
                PARTITION BY region
                ORDER BY daily_revenue
            ) AS quartile_group
        FROM daily_sales
    ),
    quartile_bounds AS (
        SELECT
            region,
            MAX(CASE WHEN quartile_group = 1 THEN daily_revenue END) AS q1,
            MIN(CASE WHEN quartile_group = 4 THEN daily_revenue END) AS q3
        FROM ranked_sales
        GROUP BY region
    ),
    fences AS (
        SELECT
            region,
            q1,
            q3,
            q3 - q1 AS iqr,
            q1 - 1.5 * (q3 - q1) AS lower_fence,
            q3 + 1.5 * (q3 - q1) AS upper_fence
        FROM quartile_bounds
    )
    SELECT
        d.sale_date,
        d.region,
        d.daily_revenue,
        ROUND(f.q1, 2) AS q1,
        ROUND(f.q3, 2) AS q3,
        ROUND(f.lower_fence, 2) AS lower_fence,
        ROUND(f.upper_fence, 2) AS upper_fence,
        CASE
            WHEN d.daily_revenue < f.lower_fence THEN 'LOW OUTLIER'
            WHEN d.daily_revenue > f.upper_fence THEN 'HIGH OUTLIER'
        END AS anomaly_type
    FROM daily_sales AS d
    JOIN fences AS f
      ON d.region = f.region
    WHERE d.daily_revenue < f.lower_fence
       OR d.daily_revenue > f.upper_fence
    ORDER BY d.region, d.sale_date
""")

with engine.connect() as conn:
    iqr_anomalies = pd.read_sql(iqr_query, conn)

print("IQR anomalies found:", len(iqr_anomalies))
display(iqr_anomalies.head(20))

# %%

detection_summary = pd.DataFrame(
    [
        {
            "method": "Regional Z-score",
            "anomaly_count": len(anomalies),
        },
        {
            "method": "Rolling 7-observation Z-score",
            "anomaly_count": int(anomaly_summary["anomaly_days"].sum()),
        },
        {
            "method": "IQR",
            "anomaly_count": len(iqr_anomalies),
        },
    ]
)

display(detection_summary)

# %%

# Re-run the rolling query without its LIMIT so the log gets every anomaly.
full_rolling_query = text(rolling_query.text.replace("LIMIT 20", ""))

with engine.connect() as conn:
    all_rolling_results = pd.read_sql(full_rolling_query, conn)

rolling_anomaly_log = all_rolling_results[
    all_rolling_results["anomaly_status"] == "ANOMALY"
].copy()

rolling_anomaly_log["detection_method"] = "Rolling 7-observation Z-score"
rolling_anomaly_log["severity"] = rolling_anomaly_log["rolling_z_score"].abs().apply(
    lambda score: "HIGH" if score >= 5 else "MEDIUM"
)

create_log_table = text("""
    CREATE TABLE IF NOT EXISTS anomaly_log (
        anomaly_id BIGINT AUTO_INCREMENT PRIMARY KEY,
        sale_date DATE NOT NULL,
        region VARCHAR(50) NOT NULL,
        detection_method VARCHAR(100) NOT NULL,
        daily_revenue DECIMAL(14, 2) NOT NULL,
        baseline_revenue DECIMAL(14, 2) NOT NULL,
        z_score DECIMAL(10, 2) NOT NULL,
        severity VARCHAR(10) NOT NULL,
        logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE KEY uq_anomaly_method_date_region
            (sale_date, region, detection_method)
    )
""")

insert_log_row = text("""
    INSERT INTO anomaly_log (
        sale_date,
        region,
        detection_method,
        daily_revenue,
        baseline_revenue,
        z_score,
        severity
    )
    VALUES (
        :sale_date,
        :region,
        :detection_method,
        :daily_revenue,
        :baseline_revenue,
        :z_score,
        :severity
    )
""")

with engine.begin() as conn:
    conn.execute(create_log_table)
    conn.execute(
        text("""
            DELETE FROM anomaly_log
            WHERE detection_method = 'Rolling 7-observation Z-score'
        """)
    )

    if not rolling_anomaly_log.empty:
        log_rows = [
            {
                "sale_date": row["sale_date"],
                "region": row["region"],
                "detection_method": row["detection_method"],
                "daily_revenue": float(row["daily_revenue"]),
                "baseline_revenue": float(row["avg_previous_7_days"]),
                "z_score": float(row["rolling_z_score"]),
                "severity": row["severity"],
            }
            for _, row in rolling_anomaly_log.iterrows()
        ]
        conn.execute(insert_log_row, log_rows)

print("Anomaly records logged:", len(rolling_anomaly_log))

# %%

with engine.connect() as conn:
    logged_summary = pd.read_sql(
        text("""
            SELECT
                detection_method,
                severity,
                COUNT(*) AS anomaly_count,
                MIN(sale_date) AS first_anomaly_date,
                MAX(sale_date) AS last_anomaly_date
            FROM anomaly_log
            GROUP BY detection_method, severity
            ORDER BY detection_method, severity
        """),
        conn,
    )

    logged_preview = pd.read_sql(
        text("""
            SELECT
                sale_date,
                region,
                daily_revenue,
                baseline_revenue,
                z_score,
                severity
            FROM anomaly_log
            ORDER BY ABS(z_score) DESC
            LIMIT 10
        """),
        conn,
    )

display(logged_summary)
display(logged_preview)

# %%

with engine.connect() as conn:
    logged_count = conn.execute(
        text("""
            SELECT COUNT(*)
            FROM anomaly_log
            WHERE detection_method = 'Rolling 7-observation Z-score'
        """)
    ).scalar_one()

expected_count = len(rolling_anomaly_log)

assert logged_count == expected_count, (
    f"Log count mismatch: expected {expected_count}, found {logged_count}"
)

assert set(rolling_anomaly_log["severity"].dropna()).issubset(
    {"HIGH", "MEDIUM"}
)

print("Rolling anomalies detected:", expected_count)
print("Anomaly records verified:", logged_count)
print("TEST CASE 19 ANOMALY DETECTION VALIDATION PASSED")
