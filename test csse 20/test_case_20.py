# Author: Om Mohite
# Test Case 20: Python export of the corresponding Jupyter notebook.
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
import pandas as pd
from sqlalchemy import URL, create_engine, text

db_password = os.getenv("DB_PASSWORD") or getpass.getpass("MySQL password: ")

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
    interaction_sample = pd.read_sql(
        text("""
            SELECT customer_id, product_id, quantity, sale_date
            FROM sales
            LIMIT 10
        """),
        conn,
    )

display(interaction_sample)

# %%

interaction_query = text("""
    SELECT
        customer_id,
        product_id,
        SUM(quantity) AS interaction_strength,
        MAX(sale_date) AS last_interaction
    FROM sales
    GROUP BY customer_id, product_id
    ORDER BY customer_id, product_id
""")

with engine.connect() as conn:
    user_item_interactions = pd.read_sql(interaction_query, conn)

print("Unique customer-product interactions:", len(user_item_interactions))
display(user_item_interactions.head(10))

# %%

target_customer_id = 1

user_based_query = text("""
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
        WHERE customer_id = :target_customer_id
    ),
    target_count AS (
        SELECT COUNT(*) AS item_count
        FROM target_items
    ),
    peer_counts AS (
        SELECT
            customer_id,
            COUNT(*) AS item_count
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
        WHERE peer.customer_id <> :target_customer_id
        GROUP BY peer.customer_id
    ),
    user_similarity AS (
        SELECT
            common.similar_customer_id,
            common.common_count
                / NULLIF(
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
        ROUND(
            SUM(
                similarity.jaccard_similarity
                * candidate.interaction_strength
            ),
            3
        ) AS recommendation_score,
        COUNT(DISTINCT candidate.customer_id) AS supporting_customers
    FROM user_similarity AS similarity
    JOIN user_items AS candidate
      ON candidate.customer_id = similarity.similar_customer_id
    LEFT JOIN target_items AS already_owned
      ON already_owned.product_id = candidate.product_id
    WHERE already_owned.product_id IS NULL
    GROUP BY candidate.product_id
    ORDER BY recommendation_score DESC, supporting_customers DESC
    LIMIT 10
""")

with engine.connect() as conn:
    user_recommendations = pd.read_sql(
        user_based_query,
        conn,
        params={"target_customer_id": target_customer_id},
    )

print("Recommendations for customer:", target_customer_id)
display(user_recommendations)

# %%

item_based_query = text("""
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
        WHERE customer_id = :target_customer_id
    ),
    peer_customers AS (
        SELECT DISTINCT
            peer.customer_id,
            peer.product_id AS matched_target_product
        FROM user_items AS peer
        JOIN target_items AS target
          ON target.product_id = peer.product_id
        WHERE peer.customer_id <> :target_customer_id
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
    LIMIT 10
""")

with engine.connect() as conn:
    item_recommendations = pd.read_sql(
        item_based_query,
        conn,
        params={"target_customer_id": target_customer_id},
    )

print("Item-based recommendations for customer:", target_customer_id)
display(item_recommendations)

# %%

popularity_query = text("""
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
        WHERE customer_id = :target_customer_id
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
    LIMIT 10
""")

with engine.connect() as conn:
    popularity_recommendations = pd.read_sql(
        popularity_query,
        conn,
        params={"target_customer_id": target_customer_id},
    )

display(popularity_recommendations)

# %%

with engine.connect() as conn:
    purchased_products = set(
        conn.execute(
            text("""
                SELECT DISTINCT product_id
                FROM sales
                WHERE customer_id = :target_customer_id
            """),
            {"target_customer_id": target_customer_id},
        ).scalars().all()
    )

recommendation_sets = {
    "user-based": user_recommendations,
    "item-based": item_recommendations,
    "popularity-based": popularity_recommendations,
}

for method, recommendations in recommendation_sets.items():
    recommended_products = recommendations["product_id"].tolist()

    assert len(recommended_products) == len(set(recommended_products)), (
        f"{method}: duplicate product recommendations found"
    )
    assert not (set(recommended_products) & purchased_products), (
        f"{method}: already purchased products were recommended"
    )

print("Target customer:", target_customer_id)
for method, recommendations in recommendation_sets.items():
    print(f"{method} recommendations:", len(recommendations))

print("TEST CASE 20 RECOMMENDATION VALIDATION PASSED")

# %%

recommendation_frames = [
    (
        "user-based",
        user_recommendations,
        "recommendation_score",
    ),
    (
        "item-based",
        item_recommendations,
        "supporting_customers",
    ),
    (
        "popularity-based",
        popularity_recommendations,
        "customer_count",
    ),
]

recommendation_rows = []

for method, frame, score_column in recommendation_frames:
    for rank, (_, row) in enumerate(frame.iterrows(), start=1):
        recommendation_rows.append(
            {
                "customer_id": int(target_customer_id),
                "product_id": int(row["product_id"]),
                "recommendation_method": method,
                "recommendation_score": float(row[score_column]),
                "recommendation_rank": rank,
            }
        )

create_results_table = text("""
    CREATE TABLE IF NOT EXISTS recommendation_results (
        customer_id BIGINT NOT NULL,
        product_id BIGINT NOT NULL,
        recommendation_method VARCHAR(50) NOT NULL,
        recommendation_score DECIMAL(14, 4) NOT NULL,
        recommendation_rank INT NOT NULL,
        generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (customer_id, product_id, recommendation_method)
    )
""")

with engine.begin() as conn:
    conn.execute(create_results_table)

    conn.execute(
        text("DELETE FROM recommendation_results WHERE customer_id = :customer_id"),
        {"customer_id": target_customer_id},
    )

    if recommendation_rows:
        conn.execute(
            text("""
                INSERT INTO recommendation_results (
                    customer_id,
                    product_id,
                    recommendation_method,
                    recommendation_score,
                    recommendation_rank
                )
                VALUES (
                    :customer_id,
                    :product_id,
                    :recommendation_method,
                    :recommendation_score,
                    :recommendation_rank
                )
            """),
            recommendation_rows,
        )

print("Recommendation rows stored:", len(recommendation_rows))

# %%

with engine.connect() as conn:
    stored_recommendations = pd.read_sql(
        text("""
            SELECT
                customer_id,
                product_id,
                recommendation_method,
                recommendation_score,
                recommendation_rank,
                generated_at
            FROM recommendation_results
            WHERE customer_id = :customer_id
            ORDER BY recommendation_method, recommendation_rank
        """),
        conn,
        params={"customer_id": target_customer_id},
    )

assert len(stored_recommendations) == len(recommendation_rows), (
    f"Expected {len(recommendation_rows)} stored rows, "
    f"found {len(stored_recommendations)}"
)

display(stored_recommendations)

print("Stored recommendation rows verified:", len(stored_recommendations))
print("TEST CASE 20 RECOMMENDATION SYSTEM VALIDATION PASSED")
