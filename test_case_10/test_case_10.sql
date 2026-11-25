CREATE DATABASE IF NOT EXISTS test_case_10;
USE test_case_10;

CREATE TABLE IF NOT EXISTS stream_events (
    event_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    device_id VARCHAR(50) NOT NULL,
    metric_name VARCHAR(50) NOT NULL,
    metric_value DECIMAL(10,2) NOT NULL,
    event_time DATETIME NOT NULL,
    received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_stream_events_device_metric_time
        (device_id, metric_name, event_time),
    INDEX idx_stream_events_metric_value
        (metric_name, metric_value)
);

-- Aggregate incoming events by device and metric.
SELECT
    device_id,
    metric_name,
    COUNT(*) AS event_count,
    ROUND(AVG(metric_value), 2) AS average_value,
    ROUND(MAX(metric_value), 2) AS maximum_value
FROM stream_events
GROUP BY device_id, metric_name
ORDER BY device_id, metric_name;

-- Show recent events that exceed the temperature alert threshold.
SET @alert_threshold = 80;

SELECT
    event_id,
    device_id,
    metric_name,
    metric_value,
    event_time
FROM stream_events
WHERE metric_name = 'temperature'
  AND metric_value > @alert_threshold
ORDER BY event_time DESC;
