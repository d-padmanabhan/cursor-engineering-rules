# Security Best Practices

## Parameterized Queries

**Always use parameterized queries:**

```python
# GOOD: Parameterized query
cursor.execute(
    "SELECT * FROM users WHERE email = %s",
    (email,)
)

# BAD: String concatenation (SQL injection risk)
cursor.execute(f"SELECT * FROM users WHERE email = '{email}'")
```

**Python Examples:**

```python
# psycopg2
import psycopg2

conn = psycopg2.connect("dbname=mydb user=user")
cursor = conn.cursor()

# Parameterized query
cursor.execute(
    "SELECT * FROM users WHERE email = %s AND status = %s",
    (email, status)
)

# SQLAlchemy
from sqlalchemy import create_engine, text

engine = create_engine("postgresql://user:pass@localhost/mydb")
with engine.connect() as conn:
    result = conn.execute(
        text("SELECT * FROM users WHERE email = :email"),
        {"email": email}
    )
```

## Row-Level Security

**Use RLS for multi-tenant applications:**

```sql
-- Enable RLS
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see their own orders
CREATE POLICY orders_user_policy ON orders
    FOR ALL
    USING (user_id = current_setting('app.user_id')::bigint);

-- Policy: Users can insert their own orders
CREATE POLICY orders_user_insert ON orders
    FOR INSERT
    WITH CHECK (user_id = current_setting('app.user_id')::bigint);

-- Set user context in application
SET app.user_id = '123';
```

**RLS with Roles:**

```sql
-- Create roles
CREATE ROLE tenant_user;
CREATE ROLE tenant_admin;

-- Policy for tenant users
CREATE POLICY tenant_user_policy ON orders
    FOR ALL
    USING (
        tenant_id = current_setting('app.tenant_id')::bigint
        AND user_id = current_setting('app.user_id')::bigint
    );

-- Policy for tenant admins
CREATE POLICY tenant_admin_policy ON orders
    FOR ALL
    USING (tenant_id = current_setting('app.tenant_id')::bigint);
```

## Connection Pooling

**Use connection pooling:**

```python
# Using psycopg2 pool
from psycopg2 import pool

connection_pool = pool.SimpleConnectionPool(
    1, 20,
    host="localhost",
    database="mydb",
    user="user",
    password="password"
)

# Get connection from pool
conn = connection_pool.getconn()
try:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
finally:
    connection_pool.putconn(conn)
```

**Using SQLAlchemy:**

```python
from sqlalchemy import create_engine

engine = create_engine(
    "postgresql://user:password@localhost/mydb",
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True
)
```

## Prepared Statements

**Use prepared statements for repeated queries:**

```sql
-- Use prepared statements for repeated queries
PREPARE get_user_by_email(VARCHAR) AS
    SELECT * FROM users WHERE email = $1;

EXECUTE get_user_by_email('user@acme.com');
```

**Python with Prepared Statements:**

```python
# psycopg2 prepared statements
cursor.execute(
    "PREPARE get_user AS SELECT * FROM users WHERE email = $1"
)
cursor.execute("EXECUTE get_user (%s)", (email,))
```

## Access Control

### User Permissions

**Grant minimal permissions:**

```sql
-- Create application user
CREATE USER app_user WITH PASSWORD 'secure_password';

-- Grant only necessary permissions
GRANT CONNECT ON DATABASE mydb TO app_user;
GRANT USAGE ON SCHEMA public TO app_user;
GRANT SELECT, INSERT, UPDATE ON users TO app_user;
GRANT SELECT ON orders TO app_user;

-- Revoke unnecessary permissions
REVOKE ALL ON DATABASE mydb FROM PUBLIC;
```

### Schema Security

```sql
-- Create separate schema for application
CREATE SCHEMA app_schema;
GRANT USAGE ON SCHEMA app_schema TO app_user;

-- Move tables to schema
ALTER TABLE users SET SCHEMA app_schema;

-- Grant permissions on schema
GRANT ALL ON ALL TABLES IN SCHEMA app_schema TO app_user;
```

## Encryption

### SSL Connections

```python
# Require SSL connections
import psycopg2

conn = psycopg2.connect(
    "dbname=mydb user=user",
    sslmode='require'
)
```

### Encrypted Columns

**Use application-level encryption for sensitive data:**

```python
from cryptography.fernet import Fernet

key = Fernet.generate_key()
cipher = Fernet(key)

# Encrypt before storing
encrypted_email = cipher.encrypt(email.encode())

# Decrypt after retrieving
decrypted_email = cipher.decrypt(encrypted_email).decode()
```

## Secret Management

**Never hardcode credentials:**

```python
# BAD: Hardcoded credentials
conn = psycopg2.connect(
    "dbname=mydb user=admin password=secret123"
)

# GOOD: From environment variables
import os
conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)

# GOOD: From secret manager (AWS Secrets Manager)
import boto3
import json

secrets_client = boto3.client('secretsmanager')
secret = secrets_client.get_secret_value(SecretId='prod/database/credentials')
credentials = json.loads(secret['SecretString'])

conn = psycopg2.connect(
    host=credentials['host'],
    database=credentials['database'],
    user=credentials['username'],
    password=credentials['password']
)
```

## Security Checklist

When reviewing database security:

- [ ] Parameterized queries used (no SQL injection)
- [ ] RLS enabled for multi-tenant tables
- [ ] Connection pooling configured
- [ ] SSL/TLS required for connections
- [ ] Minimal user permissions granted
- [ ] Secrets stored in secret manager (not code)
- [ ] Sensitive data encrypted at rest
- [ ] Regular security audits performed
- [ ] Backup encryption enabled
- [ ] Access logs monitored
