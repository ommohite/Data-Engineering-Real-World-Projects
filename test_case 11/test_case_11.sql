CREATE DATABASE IF NOT EXISTS test_case_11;
USE test_case_11;

CREATE TABLE IF NOT EXISTS web_data (
    userId BIGINT NOT NULL,
    id BIGINT PRIMARY KEY,
    title TEXT NOT NULL,
    body LONGTEXT NOT NULL
);

SELECT COUNT(*) AS post_count
FROM web_data;

SELECT userId, id, title, body
FROM web_data
ORDER BY id
LIMIT 5;
