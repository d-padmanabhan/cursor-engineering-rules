ALTER TABLE tenant_orders ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_orders_access ON tenant_orders
    FOR ALL
    USING (tenant_id = current_setting('app.tenant_id')::bigint);
