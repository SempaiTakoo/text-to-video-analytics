import pytest

from app.validate_sql import is_read_only_sql


@pytest.mark.parametrize(
    "sql",
    [
        """
SELECT user_id, email, registration_date
FROM users
WHERE registration_date >= '2024-01-01'
AND is_active = true;
    """,
        """
SELECT c.category_name,
       COUNT(p.product_id) as product_count,
       AVG(p.price) as avg_price
FROM categories c
LEFT JOIN products p ON c.category_id = p.category_id
GROUP BY c.category_id, c.category_name
ORDER BY product_count DESC;
""",
        """
WITH ranked_orders AS (
    SELECT customer_id,
           order_id,
           total_amount,
           order_date,
           RANK() OVER (PARTITION BY customer_id ORDER BY total_amount DESC)
           as rank_by_amount
    FROM orders
    WHERE EXTRACT(YEAR FROM order_date) = 2023
)
SELECT c.name, ro.order_id, ro.total_amount, ro.order_date
FROM ranked_orders ro
JOIN customers c ON ro.customer_id = c.customer_id
WHERE ro.rank_by_amount = 1;
""",
    ],
)
def test_true_if_is_read_only(sql: str) -> None:
    assert is_read_only_sql(sql)


@pytest.mark.parametrize(
    "sql",
    [
        """
INSERT INTO logs (event_type, description, created_at)
VALUES ('SYSTEM_CHECK', 'Automated log entry from maintenance script.', NOW());
""",
        """
UPDATE products
SET price = price * 1.05,
    updated_at = CURRENT_TIMESTAMP
WHERE category_id = 5
AND discontinued = false;
""",
        """
DELETE FROM user_sessions
WHERE expires_at < NOW();
""",
        """
CREATE TABLE temp_import_data (
    id SERIAL PRIMARY KEY,
    raw_data JSONB NOT NULL,
    processed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
""",
        """
WITH inactive_users AS (
    SELECT user_id, email
    FROM users
    WHERE last_login < '2023-01-01'
)
-- Первая часть - SELECT (разрешена), но вторая - DELETE (запрещена)
DELETE FROM login_attempts
WHERE user_id IN (SELECT user_id FROM inactive_users);
""",
    ],
)
def test_false_if_is_not_read_only(sql: str) -> None:
    assert not is_read_only_sql(sql)
