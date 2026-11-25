-- Test Case 20: Building a Recommendation System Using SQL
-- MySQL 8.0+
-- Prerequisite: aggregation_test.sales with customer_id, product_id, quantity.

USE aggregation_test;

SET @target_customer_id = 1;

-- User-based collaborative filtering with Jaccard similarity.
-- Excludes products already purchased by the target customer.
WITH user_items AS (
    SELECT
        customer_id,
        product_id,
        SUM(quantity) AS interaction_strength
    FROM sales
    GROUP BY customer_id, product_id
),
target_items AS (
    SELECT product_id
    FROM user_items
    WHERE customer_id = @target_customer_id
),
target_count AS (
    SELECT COUNT(*) AS item_count
    FROM target_items
),
peer_counts AS (
    SELECT customer_id, COUNT(*) AS item_count
    FROM user_items
    GROUP BY customer_id
),
common_items AS (
    SELECT
        peer.customer_id AS similar_customer_id,
        COUNT(*) AS common_count
    FROM user_items AS peer
    JOIN target_items AS target
      ON peer.product_id = target.product_id
    WHERE peer.customer_id <> @target_customer_id
    GROUP BY peer.customer_id
),
user_similarity AS (
    SELECT
        common.similar_customer_id,
        common.common_count / NULLIF(
            target_count.item_count
            + peer_counts.item_count
            - common.common_count,
            0
        ) AS jaccard_similarity
    FROM common_items AS common
    JOIN peer_counts
      ON peer_counts.customer_id = common.similar_customer_id
    CROSS JOIN target_count
)
SELECT
    candidate.product_id,
    ROUND(SUM(similarity.jaccard_similarity * candidate.interaction_strength), 3)
        AS recommendation_score,
    COUNT(DISTINCT candidate.customer_id) AS supporting_customers
FROM user_similarity AS similarity
JOIN user_items AS candidate
  ON candidate.customer_id = similarity.similar_customer_id
LEFT JOIN target_items AS already_owned
  ON already_owned.product_id = candidate.product_id
WHERE already_owned.product_id IS NULL
GROUP BY candidate.product_id
ORDER BY recommendation_score DESC, supporting_customers DESC
LIMIT 10;

-- Item-based co-occurrence using customer purchase history.
-- The source sales table has no order_id, so this is not basket-level analysis.
WITH user_items AS (
    SELECT
        customer_id,
        product_id,
        SUM(quantity) AS interaction_strength
    FROM sales
    GROUP BY customer_id, product_id
),
target_items AS (
    SELECT product_id
    FROM user_items
    WHERE customer_id = @target_customer_id
),
peer_customers AS (
    SELECT DISTINCT
        peer.customer_id,
        peer.product_id AS matched_target_product
    FROM user_items AS peer
    JOIN target_items AS target
      ON target.product_id = peer.product_id
    WHERE peer.customer_id <> @target_customer_id
)
SELECT
    candidate.product_id,
    COUNT(DISTINCT peer.customer_id) AS supporting_customers,
    COUNT(DISTINCT peer.matched_target_product) AS matched_target_products,
    SUM(candidate.interaction_strength) AS total_interaction_strength
FROM peer_customers AS peer
JOIN user_items AS candidate
  ON candidate.customer_id = peer.customer_id
LEFT JOIN target_items AS already_owned
  ON already_owned.product_id = candidate.product_id
WHERE already_owned.product_id IS NULL
GROUP BY candidate.product_id
ORDER BY
    supporting_customers DESC,
    matched_target_products DESC,
    total_interaction_strength DESC
LIMIT 10;

-- Popularity-based fallback for products not already purchased by the target.
WITH product_popularity AS (
    SELECT
        product_id,
        COUNT(DISTINCT customer_id) AS customer_count,
        SUM(quantity) AS total_quantity
    FROM sales
    GROUP BY product_id
),
target_items AS (
    SELECT DISTINCT product_id
    FROM sales
    WHERE customer_id = @target_customer_id
),
ranked_products AS (
    SELECT
        popularity.product_id,
        popularity.customer_count,
        popularity.total_quantity,
        ROW_NUMBER() OVER (
            ORDER BY
                popularity.customer_count DESC,
                popularity.total_quantity DESC,
                popularity.product_id
        ) AS recommendation_rank
    FROM product_popularity AS popularity
    LEFT JOIN target_items AS owned
      ON owned.product_id = popularity.product_id
    WHERE owned.product_id IS NULL
)
SELECT
    recommendation_rank,
    product_id,
    customer_count,
    total_quantity
FROM ranked_products
ORDER BY recommendation_rank
LIMIT 10;
