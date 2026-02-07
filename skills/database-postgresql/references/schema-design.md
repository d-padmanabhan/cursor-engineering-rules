# Schema Design Patterns

## Naming Conventions

### Tables

**Tables use plural snake_case:**

```sql
-- GOOD: Plural snake_case
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE user_books (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id),
    book_id BIGINT NOT NULL REFERENCES books(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, book_id)
);

-- BAD: Singular or camelCase
CREATE TABLE User ( ... );
CREATE TABLE userBooks ( ... );
```

### Columns

**Columns use singular snake_case:**

```sql
-- GOOD: Singular snake_case
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email_address VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- BAD: Plural or camelCase
CREATE TABLE users (
    firstName VARCHAR(100),
    EmailAddress VARCHAR(255)
);
```

### Primary Keys

**Primary keys are always named `id`:**

```sql
-- GOOD: Standard id column
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    ...
);

-- BAD: Custom primary key names
CREATE TABLE users (
    user_id BIGSERIAL PRIMARY KEY,
    user_uuid UUID PRIMARY KEY
);
```

### Foreign Keys

**Foreign keys reference the table name in singular form plus `_id`:**

```sql
-- GOOD: user_id references users table
CREATE TABLE orders (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id),
    product_id BIGINT NOT NULL REFERENCES products(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- GOOD: Self-referencing foreign key
CREATE TABLE categories (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    parent_id BIGINT REFERENCES categories(id)
);

-- BAD: Inconsistent naming
CREATE TABLE orders (
    id BIGSERIAL PRIMARY KEY,
    customer_id BIGINT REFERENCES users(id),  -- Should be user_id
    item_id BIGINT REFERENCES products(id)     -- Should be product_id
);
```

### Indexes

**Indexes use descriptive names:**

```sql
-- GOOD: Descriptive index names
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_created_at ON orders(created_at);
CREATE UNIQUE INDEX idx_users_email_unique ON users(email);

-- BAD: Generic or unclear names
CREATE INDEX idx1 ON users(email);
CREATE INDEX idx_users_1 ON users(user_id);
```

### Constraints

**Constraints use descriptive names:**

```sql
-- GOOD: Named constraints
ALTER TABLE users
    ADD CONSTRAINT users_email_unique UNIQUE (email),
    ADD CONSTRAINT users_email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$');

-- BAD: Unnamed constraints (PostgreSQL will generate random names)
ALTER TABLE users ADD UNIQUE (email);
```

## Schema Patterns

### Timestamps

**Always include `created_at` and `updated_at`:**

```sql
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- Trigger to auto-update updated_at
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
```

### Soft Deletes

**Use `deleted_at` for soft deletes:**

```sql
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    deleted_at TIMESTAMP WITH TIME ZONE NULL
);

-- Index for active records
CREATE INDEX idx_users_deleted_at ON users(deleted_at) WHERE deleted_at IS NULL;

-- Query active records
SELECT * FROM users WHERE deleted_at IS NULL;
```

### Enums

**Use PostgreSQL enums for fixed value sets:**

```sql
-- GOOD: Use ENUM type
CREATE TYPE user_status AS ENUM ('active', 'inactive', 'suspended');
CREATE TYPE order_status AS ENUM ('pending', 'processing', 'shipped', 'delivered', 'cancelled');

CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    status user_status DEFAULT 'active' NOT NULL
);

CREATE TABLE orders (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id),
    status order_status DEFAULT 'pending' NOT NULL
);

-- BAD: String with CHECK constraint (less efficient)
CREATE TABLE users (
    status VARCHAR(20) CHECK (status IN ('active', 'inactive', 'suspended'))
);
```

## Advanced Schema Patterns

### Table Inheritance

```sql
-- Use table inheritance for shared columns
CREATE TABLE base_events (
    id BIGSERIAL PRIMARY KEY,
    event_type VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

CREATE TABLE user_events (
    user_id BIGINT NOT NULL REFERENCES users(id),
    event_data JSONB
) INHERITS (base_events);

CREATE TABLE system_events (
    component VARCHAR(100) NOT NULL,
    severity VARCHAR(20) NOT NULL
) INHERITS (base_events);
```

### Check Constraints

```sql
-- Use check constraints for data validation
CREATE TABLE orders (
    id BIGSERIAL PRIMARY KEY,
    total DECIMAL(10,2) NOT NULL,
    discount_percent INTEGER NOT NULL,
    status order_status NOT NULL,

    CONSTRAINT orders_total_positive CHECK (total >= 0),
    CONSTRAINT orders_discount_range CHECK (discount_percent >= 0 AND discount_percent <= 100),
    CONSTRAINT orders_status_valid CHECK (status IN ('pending', 'processing', 'shipped', 'delivered', 'cancelled'))
);
```

### Generated Columns

```sql
-- Use generated columns for computed values
CREATE TABLE products (
    id BIGSERIAL PRIMARY KEY,
    price DECIMAL(10,2) NOT NULL,
    tax_rate DECIMAL(5,2) NOT NULL,
    price_with_tax DECIMAL(10,2) GENERATED ALWAYS AS (price * (1 + tax_rate)) STORED
);
```

## Comprehensive Example Schema

```sql
-- Enums
CREATE TYPE user_status AS ENUM ('active', 'inactive', 'suspended');
CREATE TYPE order_status AS ENUM ('pending', 'processing', 'shipped', 'delivered', 'cancelled');

-- Users table
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    status user_status DEFAULT 'active' NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    deleted_at TIMESTAMP WITH TIME ZONE NULL,

    CONSTRAINT users_email_unique UNIQUE (email),
    CONSTRAINT users_email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$')
);

-- Products table
CREATE TABLE products (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    attributes JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,

    CONSTRAINT products_price_positive CHECK (price > 0)
);

-- Orders table
CREATE TABLE orders (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    status order_status DEFAULT 'pending' NOT NULL,
    total DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,

    CONSTRAINT orders_total_positive CHECK (total >= 0)
);

-- Order items table
CREATE TABLE order_items (
    id BIGSERIAL PRIMARY KEY,
    order_id BIGINT NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    product_id BIGINT NOT NULL REFERENCES products(id) ON DELETE RESTRICT,
    quantity INTEGER NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,

    CONSTRAINT order_items_quantity_positive CHECK (quantity > 0),
    CONSTRAINT order_items_price_positive CHECK (price > 0),
    CONSTRAINT order_items_order_product_unique UNIQUE (order_id, product_id)
);

-- Indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_deleted_at ON users(deleted_at) WHERE deleted_at IS NULL;
CREATE INDEX idx_users_status ON users(status) WHERE deleted_at IS NULL;

CREATE INDEX idx_products_name ON products(name);
CREATE INDEX idx_products_attributes_gin ON products USING GIN(attributes);

CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_created_at ON orders(created_at DESC);
CREATE INDEX idx_orders_user_created ON orders(user_id, created_at DESC);

CREATE INDEX idx_order_items_order_id ON order_items(order_id);
CREATE INDEX idx_order_items_product_id ON order_items(product_id);

-- Comments
COMMENT ON TABLE users IS 'User accounts in the system';
COMMENT ON COLUMN users.email IS 'Unique email address for login';
COMMENT ON COLUMN users.status IS 'Current status of the user account';
COMMENT ON COLUMN users.deleted_at IS 'Timestamp of soft delete, NULL if active';

COMMENT ON TABLE orders IS 'Customer orders';
COMMENT ON COLUMN orders.total IS 'Total order amount in currency units';
COMMENT ON COLUMN orders.status IS 'Current status of the order';
```

**Key Patterns Demonstrated:**

- ✅ Naming Conventions: Plural tables, singular columns, consistent patterns
- ✅ Constraints: Named constraints, check constraints, foreign keys
- ✅ Indexes: Foreign keys indexed, frequently queried columns indexed
- ✅ Timestamps: created_at, updated_at with triggers
- ✅ Soft Deletes: deleted_at with partial indexes
- ✅ Enums: Type-safe status fields
- ✅ Documentation: Comments explain purpose
