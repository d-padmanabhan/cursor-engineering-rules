def load_order(cursor, tenant_id, order_id):
    cursor.execute(
        f"SELECT id, status FROM tenant_orders "
        f"WHERE tenant_id = {tenant_id} AND id = {order_id}"
    )
    return cursor.fetchone()
