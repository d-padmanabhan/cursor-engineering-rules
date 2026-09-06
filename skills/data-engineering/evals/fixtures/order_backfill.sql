INSERT INTO curated_orders (order_id, event_date, amount_cents)
SELECT order_id, event_date, amount_cents
FROM raw_orders
WHERE event_date BETWEEN DATE '2026-01-01' AND DATE '2026-01-31';
