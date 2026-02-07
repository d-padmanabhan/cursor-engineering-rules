# Advanced PostgreSQL Patterns

## JSONB Columns

**Use JSONB for flexible schema:**

```sql
-- Use JSONB for flexible schema
CREATE TABLE products (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    attributes JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- Index JSONB fields
CREATE INDEX idx_products_attributes_gin ON products USING GIN(attributes);
CREATE INDEX idx_products_attributes_category ON products((attributes->>'category'));

-- Query JSONB
SELECT * FROM products
WHERE attributes->>'category' = 'electronics'
  AND (attributes->>'price')::numeric > 100;

-- Update JSONB
UPDATE products
SET attributes = jsonb_set(attributes, '{price}', '150')
WHERE id = 1;
```

## Full-Text Search

**Create full-text search index:**

```sql
-- Create full-text search index
CREATE TABLE articles (
    id BIGSERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    search_vector tsvector
);

-- Generate search vector
CREATE INDEX idx_articles_search ON articles USING GIN(search_vector);

CREATE OR REPLACE FUNCTION update_search_vector() RETURNS TRIGGER AS $$
BEGIN
    NEW.search_vector :=
        setweight(to_tsvector('english', COALESCE(NEW.title, '')), 'A') ||
        setweight(to_tsvector('english', COALESCE(NEW.content, '')), 'B');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER articles_search_vector_update
    BEFORE INSERT OR UPDATE ON articles
    FOR EACH ROW EXECUTE FUNCTION update_search_vector();

-- Search query
SELECT id, title, ts_rank(search_vector, query) as rank
FROM articles, to_tsquery('english', 'search & terms') query
WHERE search_vector @@ query
ORDER BY rank DESC;
```

## Common Table Expressions (CTEs)

**Use CTEs for complex queries:**

```sql
-- Use CTEs for complex queries
WITH recent_orders AS (
    SELECT user_id, SUM(total) as total_spent
    FROM orders
    WHERE created_at > NOW() - INTERVAL '30 days'
    GROUP BY user_id
),
high_value_users AS (
    SELECT user_id
    FROM recent_orders
    WHERE total_spent > 1000
)
SELECT u.*, r.total_spent
FROM users u
JOIN high_value_users h ON u.id = h.user_id
JOIN recent_orders r ON u.id = r.user_id;
```

**Recursive CTEs:**

```sql
-- Recursive CTE for hierarchical data
WITH RECURSIVE category_tree AS (
    -- Base case: root categories
    SELECT id, name, parent_id, 0 as level
    FROM categories
    WHERE parent_id IS NULL
    
    UNION ALL
    
    -- Recursive case: child categories
    SELECT c.id, c.name, c.parent_id, ct.level + 1
    FROM categories c
    JOIN category_tree ct ON c.parent_id = ct.id
)
SELECT * FROM category_tree ORDER BY level, name;
```

## Arrays

**Use arrays for multi-value columns:**

```sql
-- Use arrays for tags, categories, etc.
CREATE TABLE articles (
    id BIGSERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    tags TEXT[] NOT NULL DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- Query arrays
SELECT * FROM articles WHERE 'python' = ANY(tags);

-- Index arrays
CREATE INDEX idx_articles_tags_gin ON articles USING GIN(tags);

-- Update arrays
UPDATE articles SET tags = array_append(tags, 'new-tag') WHERE id = 1;
```

## Window Functions

**Use window functions for analytical queries:**

```sql
-- Window functions for rankings
SELECT
    user_id,
    total,
    ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY total DESC) as rank,
    SUM(total) OVER (PARTITION BY user_id) as user_total,
    AVG(total) OVER (PARTITION BY user_id) as user_avg
FROM orders
ORDER BY user_id, total DESC;
```

## Lateral Joins

**Use lateral joins for correlated subqueries:**

```sql
-- Lateral join for correlated queries
SELECT u.*, recent_orders.*
FROM users u
CROSS JOIN LATERAL (
    SELECT *
    FROM orders
    WHERE user_id = u.id
    ORDER BY created_at DESC
    LIMIT 5
) recent_orders;
```

## Custom Functions

**Create custom functions for reusable logic:**

```sql
-- Custom function for user statistics
CREATE OR REPLACE FUNCTION get_user_stats(p_user_id BIGINT)
RETURNS TABLE (
    total_orders BIGINT,
    total_spent NUMERIC,
    avg_order_value NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        COUNT(*)::BIGINT,
        COALESCE(SUM(total), 0),
        COALESCE(AVG(total), 0)
    FROM orders
    WHERE user_id = p_user_id;
END;
$$ LANGUAGE plpgsql;

-- Use function
SELECT * FROM get_user_stats(123);
```

## Triggers

**Use triggers for automatic updates:**

```sql
-- Trigger for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger for audit logging
CREATE TABLE audit_log (
    id BIGSERIAL PRIMARY KEY,
    table_name VARCHAR(100) NOT NULL,
    record_id BIGINT NOT NULL,
    action VARCHAR(10) NOT NULL,
    changed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    old_data JSONB,
    new_data JSONB
);

CREATE OR REPLACE FUNCTION audit_trigger()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO audit_log (table_name, record_id, action, old_data, new_data)
    VALUES (
        TG_TABLE_NAME,
        COALESCE(NEW.id, OLD.id),
        TG_OP,
        row_to_json(OLD)::JSONB,
        row_to_json(NEW)::JSONB
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER users_audit
    AFTER INSERT OR UPDATE OR DELETE ON users
    FOR EACH ROW
    EXECUTE FUNCTION audit_trigger();
```

## Extensions

**Useful PostgreSQL extensions:**

```sql
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
SELECT uuid_generate_v4();

-- Enable PostGIS for geospatial data
CREATE EXTENSION IF NOT EXISTS postgis;

-- Enable pg_trgm for fuzzy text search
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE INDEX idx_users_email_trgm ON users USING gin(email gin_trgm_ops);

-- Enable pg_stat_statements for query statistics
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
```

## Best Practices Summary

1. **JSONB** - Use for flexible, schema-less data
2. **Full-text search** - Use tsvector for text search
3. **CTEs** - Use for complex, readable queries
4. **Arrays** - Use for multi-value columns
5. **Window functions** - Use for analytical queries
6. **Lateral joins** - Use for correlated subqueries
7. **Custom functions** - Use for reusable logic
8. **Triggers** - Use for automatic updates and auditing
9. **Extensions** - Use for additional functionality
