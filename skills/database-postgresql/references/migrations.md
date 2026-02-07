# Migration Best Practices

## Migration Files

**Use timestamped migration files:**

```sql
-- migrations/20250115120000_create_users_table.sql
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- migrations/20250115120001_add_user_status.sql
CREATE TYPE user_status AS ENUM ('active', 'inactive', 'suspended');
ALTER TABLE users ADD COLUMN status user_status DEFAULT 'active' NOT NULL;
```

## Reversible Migrations

**Always provide both up and down migrations:**

```sql
-- Up migration: migrations/20250115120000_create_users_table.sql
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE
);

-- Down migration: migrations/20250115120000_create_users_table.down.sql
DROP TABLE IF EXISTS users;
```

## Data Migrations

**Separate schema and data migrations:**

```sql
-- Schema migration: migrations/20250115120001_add_user_status.sql
ALTER TABLE users ADD COLUMN status user_status;

-- Data migration: migrations/20250115120002_populate_user_status.sql
UPDATE users SET status = 'active' WHERE status IS NULL;
ALTER TABLE users ALTER COLUMN status SET NOT NULL;
```

## Migration Best Practices

### 1. Test Migrations Locally First

```bash
# Run migrations on local database
psql -d myapp_dev -f migrations/20250115120000_create_users_table.sql

# Verify migration
psql -d myapp_dev -c "\d users"

# Test rollback
psql -d myapp_dev -f migrations/20250115120000_create_users_table.down.sql
```

### 2. Use Transactions

```sql
-- Wrap migrations in transactions
BEGIN;

CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE
);

CREATE INDEX idx_users_email ON users(email);

COMMIT;
```

### 3. Add Columns with Defaults

```sql
-- GOOD: Add column with default, then make NOT NULL
ALTER TABLE users ADD COLUMN status user_status DEFAULT 'active';
UPDATE users SET status = 'active' WHERE status IS NULL;
ALTER TABLE users ALTER COLUMN status SET NOT NULL;

-- BAD: Adding NOT NULL column without default (blocks table)
ALTER TABLE users ADD COLUMN status user_status NOT NULL;
```

### 4. Index Creation Strategy

```sql
-- For large tables, create index CONCURRENTLY
CREATE INDEX CONCURRENTLY idx_users_email ON users(email);

-- This doesn't block writes but takes longer
```

### 5. Column Renaming

```sql
-- Rename column (preserves data and constraints)
ALTER TABLE users RENAME COLUMN email_address TO email;
```

### 6. Column Type Changes

```sql
-- Change type safely
-- Step 1: Add new column
ALTER TABLE users ADD COLUMN email_new VARCHAR(255);

-- Step 2: Copy data
UPDATE users SET email_new = email::VARCHAR(255);

-- Step 3: Drop old column
ALTER TABLE users DROP COLUMN email;

-- Step 4: Rename new column
ALTER TABLE users RENAME COLUMN email_new TO email;

-- Step 5: Add constraints
ALTER TABLE users ADD CONSTRAINT users_email_unique UNIQUE (email);
```

## Testing Migrations

### Unit Testing Migrations

```python
# Test migrations with pytest
import pytest
from sqlalchemy import create_engine, text
from alembic import command
from alembic.config import Config

@pytest.fixture
def db_engine():
    """Create test database engine."""
    engine = create_engine("postgresql://test:test@localhost/testdb")
    yield engine
    engine.dispose()

def test_migration_up_and_down(db_engine):
    """Test migration can be applied and reverted."""
    alembic_cfg = Config("alembic.ini")

    # Apply migration
    command.upgrade(alembic_cfg, "head")

    # Verify table exists
    with db_engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM users"))
        assert result.scalar() == 0

    # Revert migration
    command.downgrade(alembic_cfg, "base")

    # Verify table removed
    with db_engine.connect() as conn:
        with pytest.raises(Exception):  # Table should not exist
            conn.execute(text("SELECT COUNT(*) FROM users"))
```

### Integration Testing

```python
# Test database operations
@pytest.fixture
def db_session(db_engine):
    """Create database session."""
    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker(bind=db_engine)
    session = Session()
    yield session
    session.rollback()
    session.close()

def test_create_user(db_session):
    """Test user creation."""
    user = User(email="test@acme.com", first_name="Test", last_name="User")
    db_session.add(user)
    db_session.commit()

    assert user.id is not None
    assert user.created_at is not None
```

## Migration Tools

### Alembic (Python)

```python
# alembic.ini
[alembic]
script_location = alembic
sqlalchemy.url = postgresql://user:pass@localhost/mydb

# migrations/env.py
from models import Base
target_metadata = Base.metadata

# Generate migration
alembic revision --autogenerate -m "create users table"

# Apply migration
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Flyway (Java/Universal)

```sql
-- V1__Create_users_table.sql
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE
);

-- V2__Add_user_status.sql
CREATE TYPE user_status AS ENUM ('active', 'inactive');
ALTER TABLE users ADD COLUMN status user_status DEFAULT 'active';
```

### Rails Migrations (Ruby)

```ruby
# db/migrate/20250115120000_create_users.rb
class CreateUsers < ActiveRecord::Migration[7.0]
  def change
    create_table :users do |t|
      t.string :email, null: false
      t.timestamps
    end

    add_index :users, :email, unique: true
  end
end
```

## Common Migration Patterns

### Adding Foreign Key

```sql
-- Add foreign key column
ALTER TABLE orders ADD COLUMN user_id BIGINT;

-- Populate data
UPDATE orders SET user_id = (SELECT id FROM users LIMIT 1);

-- Add constraint
ALTER TABLE orders 
    ALTER COLUMN user_id SET NOT NULL,
    ADD CONSTRAINT orders_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(id);
```

### Removing Column

```sql
-- Step 1: Remove constraints
ALTER TABLE users DROP CONSTRAINT IF EXISTS users_old_column_fkey;

-- Step 2: Remove index
DROP INDEX IF EXISTS idx_users_old_column;

-- Step 3: Remove column
ALTER TABLE users DROP COLUMN old_column;
```

### Changing Default Value

```sql
-- Change default value
ALTER TABLE users ALTER COLUMN status SET DEFAULT 'inactive';

-- Remove default
ALTER TABLE users ALTER COLUMN status DROP DEFAULT;
```

## Migration Checklist

Before deploying migrations:

- [ ] Migration is reversible (has down migration)
- [ ] Migration tested locally
- [ ] Migration tested in staging
- [ ] Large tables use CONCURRENTLY for indexes
- [ ] Data migrations separate from schema migrations
- [ ] Backup taken before production migration
- [ ] Rollback plan documented
- [ ] Migration doesn't lock tables unnecessarily
- [ ] Migration includes appropriate indexes
- [ ] Migration preserves existing data
