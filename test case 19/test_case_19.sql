-- Test Case 19: SQL anomaly detection queries
-- Uses the aggregation_test.sales table created for Test Case 18.
USE aggregation_test;

-- Regional point anomalies using Z-scores.
WITH daily_sales AS (
    SELECT sale_date, region, SUM(total_amount) AS daily_revenue
    FROM sales
    GROUP BY sale_date, region
), regional_stats AS (
    SELECT region, AVG(daily_revenue) AS avg_revenue,
           STDDEV_SAMP(daily_revenue) AS stddev_revenue
    FROM daily_sales GROUP BY region
), scored AS (
    SELECT d.sale_date, d.region, d.daily_revenue, s.avg_revenue,
           (d.daily_revenue-s.avg_revenue)/NULLIF(s.stddev_revenue,0) AS z_score
    FROM daily_sales d JOIN regional_stats s ON s.region=d.region
)
SELECT sale_date, region, daily_revenue, ROUND(avg_revenue,2) AS avg_revenue,
       ROUND(z_score,2) AS z_score
FROM scored WHERE ABS(z_score)>=3 ORDER BY ABS(z_score) DESC;

-- Time-series anomalies against the previous seven observations per region.
WITH daily_sales AS (
    SELECT sale_date, region, SUM(total_amount) AS daily_revenue
    FROM sales GROUP BY sale_date, region
), baseline AS (
    SELECT sale_date, region, daily_revenue,
           COUNT(*) OVER (PARTITION BY region ORDER BY sale_date
               ROWS BETWEEN 7 PRECEDING AND 1 PRECEDING) AS history_days,
           AVG(daily_revenue) OVER (PARTITION BY region ORDER BY sale_date
               ROWS BETWEEN 7 PRECEDING AND 1 PRECEDING) AS avg_previous_7,
           STDDEV_SAMP(daily_revenue) OVER (PARTITION BY region ORDER BY sale_date
               ROWS BETWEEN 7 PRECEDING AND 1 PRECEDING) AS stddev_previous_7
    FROM daily_sales
), scored AS (
    SELECT *, (daily_revenue-avg_previous_7)/NULLIF(stddev_previous_7,0) AS z_score
    FROM baseline WHERE history_days=7
)
SELECT sale_date, region, daily_revenue, ROUND(avg_previous_7,2) AS baseline_revenue,
       ROUND(z_score,2) AS z_score
FROM scored WHERE stddev_previous_7>0 AND ABS(z_score)>=3
ORDER BY ABS(z_score) DESC;

-- Quartile-based IQR outlier detection using NTILE quartile groups.
WITH daily_sales AS (
    SELECT sale_date, region, SUM(total_amount) AS daily_revenue
    FROM sales GROUP BY sale_date, region
), ranked AS (
    SELECT sale_date, region, daily_revenue,
           NTILE(4) OVER (PARTITION BY region ORDER BY daily_revenue) AS quartile_group
    FROM daily_sales
), bounds AS (
    SELECT region,
           MAX(CASE WHEN quartile_group=1 THEN daily_revenue END) AS q1,
           MIN(CASE WHEN quartile_group=4 THEN daily_revenue END) AS q3
    FROM ranked GROUP BY region
), fences AS (
    SELECT region, q1, q3, q1-1.5*(q3-q1) AS lower_fence,
           q3+1.5*(q3-q1) AS upper_fence
    FROM bounds
)
SELECT d.sale_date, d.region, d.daily_revenue, f.q1, f.q3,
       f.lower_fence, f.upper_fence
FROM daily_sales d JOIN fences f ON f.region=d.region
WHERE d.daily_revenue<f.lower_fence OR d.daily_revenue>f.upper_fence
ORDER BY d.region, d.sale_date;

CREATE TABLE IF NOT EXISTS anomaly_log (
    anomaly_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    sale_date DATE NOT NULL,
    region VARCHAR(50) NOT NULL,
    detection_method VARCHAR(100) NOT NULL,
    daily_revenue DECIMAL(14,2) NOT NULL,
    baseline_revenue DECIMAL(14,2) NOT NULL,
    z_score DECIMAL(10,2) NOT NULL,
    severity VARCHAR(10) NOT NULL,
    logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_anomaly_method_date_region (sale_date,region,detection_method)
);
