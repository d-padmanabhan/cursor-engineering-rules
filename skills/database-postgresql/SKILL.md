---
name: database-postgresql
description: PostgreSQL database design patterns, naming conventions, schema design, migrations, performance optimization, and security best practices. Use when designing database schemas, writing migrations, optimizing queries, or working with PostgreSQL-specific features like JSONB, full-text search, or RLS.
---

# PostgreSQL Database Engineering

## Core Principles

- **"Consistency is king"** - Follow naming conventions consistently across all tables and columns
- **"Explicit over implicit"** - Use explicit constraints, types, and defaults
- **"Performance by design"** - Index foreign keys and frequently queried columns
- **"Security by default"** - Use parameterized queries, RLS, least privilege
- **"Migrations are code"** - Version control migrations, make them reversible
- **"Documentation matters"** - Comments explain why, not just what
- **"Test your migrations"** - Test migrations in staging before production
- **"Backup before changes"** - Always backup before destructive operations

## Quick Reference

### Naming Conventions

- **Tables:** Plural snake_case (`users`, `order_items`)
- **Columns:** Singular snake_case (`first_name`, `email`)
- **Primary Keys:** Always named `id` (BIGSERIAL)
- **Foreign Keys:** `table_name_id` pattern (`user_id`, `product_id`)
- **Indexes:** `idx_table_column` pattern (`idx_users_email`)
- **Constraints:** Named with descriptive pattern (`users_email_unique`)

### Essential Patterns

**Timestamps:**

```sql
created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
```

**Soft Deletes:**

```sql
deleted_at TIMESTAMP WITH TIME ZONE NULL
CREATE INDEX idx_users_deleted_at ON users(deleted_at) WHERE deleted_at IS NULL;
```

**Enums:**

```sql
CREATE TYPE user_status AS ENUM ('active', 'inactive', 'suspended');
status user_status DEFAULT 'active' NOT NULL
```

**Foreign Keys:**

```sql
user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE RESTRICT
```

## Common Patterns

### Basic Table Structure

```sql
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    
    CONSTRAINT users_email_unique UNIQUE (email)
);

CREATE INDEX idx_users_email ON users(email);
```

### Migration Pattern

```sql
-- migrations/20250115120000_create_users_table.sql
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- Always provide down migration
-- migrations/20250115120000_create_users_table.down.sql
DROP TABLE IF EXISTS users;
```

## Security Essentials

**Always use parameterized queries:**

```python
# GOOD
cursor.execute("SELECT * FROM users WHERE email = %s", (email,))

# BAD - SQL injection risk
cursor.execute(f"SELECT * FROM users WHERE email = '{email}'")
```

**Row-Level Security for multi-tenant:**

```sql
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
CREATE POLICY orders_user_policy ON orders
    FOR ALL USING (user_id = current_setting('app.user_id')::bigint);
```

## Performance Basics

**Index foreign keys:**

```sql
CREATE INDEX idx_orders_user_id ON orders(user_id);
```

**Partial indexes for filtered queries:**

```sql
CREATE INDEX idx_users_active ON users(email) WHERE deleted_at IS NULL;
```

**Composite indexes for common patterns:**

```sql
CREATE INDEX idx_orders_user_created ON orders(user_id, created_at DESC);
```

## When to Use This Skill

- Designing database schemas
- Writing SQL migrations
- Optimizing database queries
- Implementing database security (RLS, parameterized queries)
- Working with PostgreSQL-specific features (JSONB, full-text search, arrays)
- Performance tuning (indexes, query plans, partitioning)
- Database testing and migrations

## References

For detailed guidance, see:

- [references/schema-design.md](references/schema-design.md) - Naming conventions, table design patterns
- [references/migrations.md](references/migrations.md) - Migration best practices, reversible migrations
- [references/performance.md](references/performance.md) - Indexing strategies, query optimization
- [references/security.md](references/security.md) - RLS, parameterized queries, connection pooling
- [references/sql-safety.md](references/sql-safety.md) - SQL categories (DQL/DML/DDL/DCL/TCL) and destructive-operation guardrails
- [references/advanced-patterns.md](references/advanced-patterns.md) - JSONB, full-text search, CTEs, partitioning
