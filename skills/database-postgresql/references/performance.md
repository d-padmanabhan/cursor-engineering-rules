# Performance Optimization

## Indexing Strategies

### Index Foreign Keys

**Foreign keys should be indexed:**

```sql
-- Foreign keys should be indexed
CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_product_id ON orders(product_id);
```

### Index Frequently Queried Columns

```sql
-- Frequently queried columns
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_orders_created_at ON orders(created_at);
```

### Composite Indexes

**Use composite indexes for common query patterns:**

```sql
-- Composite indexes for common query patterns
CREATE INDEX idx_orders_user_created ON orders(user_id, created_at DESC);

-- Query benefits from composite index
SELECT * FROM orders 
WHERE user_id = 123 
ORDER BY created_at DESC;
```

### Partial Indexes

**Use partial indexes for filtered queries:**

```sql
-- Index only active users
CREATE INDEX idx_users_active ON users(email) WHERE deleted_at IS NULL;

-- Index only pending orders
CREATE INDEX idx_orders_pending ON orders(created_at) WHERE status = 'pending';
```

## Query Optimization

### Query Performance Analysis

```sql
-- Enable query timing
\timing

-- Explain query plan
EXPLAIN ANALYZE
SELECT * FROM orders
WHERE user_id = 123
  AND created_at > NOW() - INTERVAL '30 days';

-- Check index usage
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan DESC;
```

### Performance Optimization Examples

**Query Optimization:**

```sql
-- BAD: Full table scan
SELECT * FROM orders WHERE user_id = 123 AND status = 'pending';

-- GOOD: Composite index covers both conditions
CREATE INDEX idx_orders_user_status ON orders(user_id, status);
SELECT * FROM orders WHERE user_id = 123 AND status = 'pending';

-- EXCELLENT: Partial index for common query
CREATE INDEX idx_orders_user_pending ON orders(user_id) WHERE status = 'pending';
SELECT * FROM orders WHERE user_id = 123 AND status = 'pending';
```

**Covering Indexes:**

```sql
-- Covering index includes all columns needed for query
CREATE INDEX idx_orders_user_covering ON orders(user_id, created_at, total, status);

-- Query can be satisfied from index alone
SELECT user_id, created_at, total, status
FROM orders
WHERE user_id = 123;
```

## Advanced Performance Patterns

### Partitioning

**Partition large tables by date:**

```sql
-- Partition large tables by date
CREATE TABLE orders (
    id BIGSERIAL,
    user_id BIGINT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    total DECIMAL(10,2) NOT NULL
) PARTITION BY RANGE (created_at);

-- Create partitions
CREATE TABLE orders_2024_q1 PARTITION OF orders
    FOR VALUES FROM ('2024-01-01') TO ('2024-04-01');

CREATE TABLE orders_2024_q2 PARTITION OF orders
    FOR VALUES FROM ('2024-04-01') TO ('2024-07-01');
```

### Materialized Views

**Use materialized views for expensive aggregations:**

```sql
-- Materialized view for expensive aggregations
CREATE MATERIALIZED VIEW user_order_stats AS
SELECT
    user_id,
    COUNT(*) as total_orders,
    SUM(total) as total_spent,
    AVG(total) as avg_order_value
FROM orders
GROUP BY user_id;

-- Refresh periodically
REFRESH MATERIALIZED VIEW CONCURRENTLY user_order_stats;

-- Index materialized view
CREATE UNIQUE INDEX idx_user_order_stats_user_id ON user_order_stats(user_id);
```

## Performance Monitoring

### Query Statistics

```sql
-- Enable query statistics
ALTER SYSTEM SET track_io_timing = on;
ALTER SYSTEM SET track_functions = all;
SELECT pg_reload_conf();

-- View slow queries
SELECT
    query,
    calls,
    total_exec_time,
    mean_exec_time,
    max_exec_time
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;
```

### Table Statistics

```sql
-- Update statistics
ANALYZE users;

-- View table statistics
SELECT
    schemaname,
    tablename,
    n_live_tup,
    n_dead_tup,
    last_vacuum,
    last_autovacuum,
    last_analyze,
    last_autoanalyze
FROM pg_stat_user_tables
WHERE schemaname = 'public';
```

### Vacuum and Analyze

```sql
-- Manual vacuum
VACUUM ANALYZE users;

-- Vacuum with verbose output
VACUUM VERBOSE ANALYZE users;

-- Check vacuum status
SELECT
    schemaname,
    tablename,
    last_vacuum,
    last_autovacuum,
    vacuum_count,
    autovacuum_count
FROM pg_stat_user_tables;
```

## Troubleshooting Performance Issues

### Slow Queries

```sql
-- Check for missing indexes
SELECT
    schemaname,
    tablename,
    seq_scan,
    seq_tup_read,
    idx_scan,
    seq_tup_read / NULLIF(seq_scan, 0) as avg_seq_read
FROM pg_stat_user_tables
WHERE seq_scan > 0
ORDER BY seq_tup_read DESC;

-- Find unused indexes
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan
FROM pg_stat_user_indexes
WHERE idx_scan = 0
ORDER BY schemaname, tablename;
```

### Lock Contention

```sql
-- Check for locks
SELECT
    locktype,
    relation::regclass,
    mode,
    granted,
    pid
FROM pg_locks
WHERE NOT granted;

-- Kill blocking queries
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE pid IN (
    SELECT pid FROM pg_locks WHERE NOT granted
);
```

### Connection Issues

```sql
-- Check active connections
SELECT
    datname,
    usename,
    application_name,
    state,
    query_start,
    state_change
FROM pg_stat_activity
WHERE datname = 'mydb';

-- Check connection limits
SHOW max_connections;
```

## Performance Best Practices

1. **Index foreign keys** - Always index foreign key columns
2. **Use partial indexes** - For filtered queries (WHERE deleted_at IS NULL)
3. **Composite indexes** - For multi-column queries
4. **Covering indexes** - Include frequently selected columns
5. **Partition large tables** - By date or other criteria
6. **Materialized views** - For expensive aggregations
7. **Regular VACUUM** - Keep statistics up to date
8. **Monitor query performance** - Use pg_stat_statements
9. **Analyze query plans** - Use EXPLAIN ANALYZE
10. **Connection pooling** - Use connection pools (pgBouncer, SQLAlchemy)
