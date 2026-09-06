BEGIN;

DELETE FROM tenant_orders
WHERE status = 'cancelled';

CREATE INDEX idx_tenant_orders_created_at
    ON tenant_orders (created_at);

COMMIT;
