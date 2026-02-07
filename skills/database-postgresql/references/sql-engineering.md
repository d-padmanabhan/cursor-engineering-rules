# SQL Engineering Patterns

**Audience:** Analysts and engineers writing or reviewing SQL for any RDBMS

**Goal:** Write SQL that is safe-by-default, reviewable, and operationally predictable

> [!IMPORTANT]
> This guide is intentionally database-agnostic. For PostgreSQL-specific patterns, see other references in this directory.

---

## SQL Command Categories (Mental Model)

Use these categories to quickly understand **risk**, **required privileges**, and **rollback strategy**.

### DQL - Data Query Language (Read-Only Queries)

**Primary command:** `SELECT`

**Common clauses:** `FROM`, `WHERE`, `GROUP BY`, `HAVING`, `ORDER BY`, `LIMIT`, `OFFSET`

**Risk level:** Low (read-only)

**Rollback strategy:** N/A (no mutations)

**Examples:**

```sql
-- Basic query
SELECT user_id, username, created_at
FROM users
WHERE status = 'active'
ORDER BY created_at DESC
LIMIT 100;

-- Aggregation
SELECT country, COUNT(*) as user_count
FROM users
GROUP BY country
HAVING COUNT(*) > 10;
```

---

### DML - Data Manipulation Language (Changes Table Contents)

**Commands:** `INSERT`, `UPDATE`, `DELETE`, `MERGE` (where supported)

**Risk level:** High (data loss possible)

**Rollback strategy:** Use transactions with `BEGIN`/`COMMIT`/`ROLLBACK`

> [!CAUTION]
> DML is where "I destroyed production data" incidents happen.
> Always prove the rowset first and use transactions for risky changes.

**Safe patterns:**

```sql
-- 1. Prove the target set first
SELECT user_id, username FROM users WHERE last_login < '2023-01-01';
-- Verify count and sample data

-- 2. Begin transaction
BEGIN;

-- 3. Perform DML
DELETE FROM users WHERE last_login < '2023-01-01';

-- 4. Verify results
SELECT COUNT(*) FROM users; -- Check expected count

-- 5. Commit or rollback
COMMIT; -- or ROLLBACK if something looks wrong
```

---

### DDL - Data Definition Language (Changes Schema/Objects)

**Commands:** `CREATE`, `ALTER`, `DROP`, `TRUNCATE`, `RENAME`

**Risk level:** Critical (can break applications, cause downtime)

**Rollback strategy:** Often cannot be rolled back; require careful planning

> [!WARNING]
> DDL can take locks, block traffic, and be irreversible (especially `DROP` and `TRUNCATE`).
> Treat DDL as code: migration-reviewed, tested, and rolled out safely.

**Safe patterns:**

```sql
-- Add column (nullable first, backfill later)
ALTER TABLE users ADD COLUMN email_verified BOOLEAN DEFAULT NULL;

-- Create index concurrently (PostgreSQL-specific, non-blocking)
CREATE INDEX CONCURRENTLY idx_users_email ON users(email);

-- Drop column (multi-step process)
-- Step 1: Stop writes to column in application
-- Step 2: Verify no active usage
-- Step 3: Drop column
ALTER TABLE users DROP COLUMN deprecated_field;
```

---

### DCL - Data Control Language (Permissions)

**Commands:** `GRANT`, `REVOKE`, role/user management

**Risk level:** Medium (privilege escalation possible)

**Rollback strategy:** Can be reversed with opposite command

**Safe patterns:**

```sql
-- Grant read-only access
GRANT SELECT ON TABLE users TO analytics_role;

-- Grant write access to specific tables
GRANT INSERT, UPDATE ON TABLE orders TO app_role;

-- Revoke permissions
REVOKE ALL ON TABLE sensitive_data FROM public;
```

---

### TCL - Transaction Control Language (Atomicity and Recovery)

**Commands:** `BEGIN`/`START TRANSACTION`, `COMMIT`, `ROLLBACK`, `SAVEPOINT`

**Risk level:** Low (controls other operations)

**Rollback strategy:** Built-in with `ROLLBACK`

**Patterns:**

```sql
-- Basic transaction
BEGIN;
UPDATE accounts SET balance = balance - 100 WHERE account_id = 1;
UPDATE accounts SET balance = balance + 100 WHERE account_id = 2;
COMMIT;

-- With savepoint for partial rollback
BEGIN;
UPDATE table1 SET status = 'processed';
SAVEPOINT sp1;
UPDATE table2 SET status = 'processed';
-- If table2 update fails, rollback to savepoint
ROLLBACK TO SAVEPOINT sp1;
COMMIT;
```

---

## Destructive Operation Guardrails (MUST FOLLOW)

### DELETE / UPDATE Safety

**Rules:**

1. **NEVER run `DELETE` or `UPDATE` without a `WHERE` clause**
2. **Always prove the target set first** with an equivalent `SELECT`
3. **Record expected row count** and sample primary keys
4. **Use transactions** for all destructive changes

**Safe workflow:**

```sql
-- Step 1: Prove the target set
SELECT user_id, username, last_login
FROM users
WHERE last_login < '2023-01-01'
ORDER BY last_login
LIMIT 10; -- Review sample

-- Step 2: Count affected rows
SELECT COUNT(*) FROM users WHERE last_login < '2023-01-01';
-- Record this number: expected 2,847 rows

-- Step 3: Begin transaction
BEGIN;

-- Step 4: Perform DELETE
DELETE FROM users WHERE last_login < '2023-01-01';
-- Check affected rows matches expectation

-- Step 5: Verify results
SELECT COUNT(*) FROM users; -- Should match expected total

-- Step 6: Commit or rollback
COMMIT; -- or ROLLBACK if something looks wrong
```

**Safer patterns:**

```sql
-- Use RETURNING to see what was modified (PostgreSQL, some others)
DELETE FROM users
WHERE last_login < '2023-01-01'
RETURNING user_id, username;

-- Limit scope by immutable IDs, not names
UPDATE users SET status = 'inactive'
WHERE user_id IN (SELECT user_id FROM inactive_user_ids);
```

> [!TIP]
> For large tables, add a predicate that can use an index.
> Avoid whole-table scans for hot production paths.

---

### TRUNCATE vs DELETE

| Aspect | TRUNCATE | DELETE |
|--------|----------|--------|
| **Speed** | Fast (removes all rows at once) | Slower (row-by-row) |
| **WHERE clause** | Not supported (all rows removed) | Supported (selective) |
| **Rollback** | May not be rollback-able in some DBs | Can rollback in transaction |
| **Triggers** | May bypass row-level triggers | Fires row-level triggers |
| **Locks** | Takes exclusive table lock | Row-level locks |
| **Use case** | Empty entire table quickly | Selective row removal |

**Example:**

```sql
-- TRUNCATE: removes all rows, resets sequences (fast)
TRUNCATE TABLE staging_data;

-- DELETE: selective, can rollback
BEGIN;
DELETE FROM staging_data WHERE imported_at < NOW() - INTERVAL '30 days';
COMMIT;
```

---

### DROP Safety

**Rules:**

1. `DROP TABLE` / `DROP COLUMN` is often **irreversible**
2. Can **break applications immediately**
3. Prefer **multi-step deprecation**

**Safe deprecation workflow:**

```sql
-- Step 1: Stop writes to column in application code
-- (Deploy code change first)

-- Step 2: Verify no active usage
SELECT * FROM pg_stat_user_tables WHERE schemaname = 'public' AND tablename = 'users';
-- Check for recent writes

-- Step 3: Rename column to indicate deprecation (optional safety step)
ALTER TABLE users RENAME COLUMN old_field TO deprecated_old_field;
-- Monitor for errors in applications

-- Step 4: After confirmation, drop the column
ALTER TABLE users DROP COLUMN deprecated_old_field;
```

**For tables:**

```sql
-- Step 1: Stop all writes to table
-- Step 2: Backfill/migrate readers to new table
-- Step 3: Remove all usage from application
-- Step 4: Rename table to indicate deprecation
ALTER TABLE old_table RENAME TO deprecated_old_table;
-- Monitor for a period

-- Step 5: Finally drop
DROP TABLE deprecated_old_table;
```

---

## Transactions (TCL) - Safe Workflows

### "Prove Then Mutate" Pattern

```sql
-- 1. BEGIN transaction
BEGIN;

-- 2. SELECT to verify target set
SELECT order_id, status, total
FROM orders
WHERE status = 'pending' AND created_at < NOW() - INTERVAL '7 days';

-- 3. Perform DML
UPDATE orders
SET status = 'cancelled', cancelled_at = NOW()
WHERE status = 'pending' AND created_at < NOW() - INTERVAL '7 days';

-- 4. Verify results with SELECT
SELECT COUNT(*) FROM orders WHERE status = 'cancelled' AND cancelled_at >= NOW() - INTERVAL '1 minute';
-- Should match expected count

-- 5. COMMIT or ROLLBACK
COMMIT; -- or ROLLBACK if verification fails
```

> [!IMPORTANT]
> If the DB supports it, use statement/lock timeouts for production migrations
> to avoid prolonged blocking.

**Setting timeouts (PostgreSQL example):**

```sql
-- Set statement timeout (abort if query takes > 30s)
SET statement_timeout = '30s';

-- Set lock timeout (abort if can't acquire lock within 5s)
SET lock_timeout = '5s';

BEGIN;
-- ... your DDL/DML operations
COMMIT;
```

---

### Savepoints for Complex Operations

Use `SAVEPOINT` when you need partial rollback inside a longer transaction.

```sql
BEGIN;

-- Operation 1
INSERT INTO audit_log (action) VALUES ('start_batch');

SAVEPOINT before_updates;

-- Operation 2 (might fail)
UPDATE orders SET processed = true WHERE batch_id = 123;

-- If Operation 2 had issues, rollback to savepoint
-- ROLLBACK TO SAVEPOINT before_updates;

SAVEPOINT before_cleanup;

-- Operation 3
DELETE FROM temp_data WHERE batch_id = 123;

-- Final commit
COMMIT;
```

---

## Security Essentials

### Prevent SQL Injection

**Rule:** Always use **parameterized queries**, never string concatenation

**Bad (vulnerable to SQL injection):**

```python
# DON'T DO THIS
user_input = "admin' OR '1'='1"
query = f"SELECT * FROM users WHERE username = '{user_input}'"
```

**Good (parameterized):**

```python
# DO THIS
query = "SELECT * FROM users WHERE username = %s"
cursor.execute(query, (user_input,))
```

---

### Least Privilege Roles

**Principles:**

- Read-only roles for analytics/reporting
- Write roles scoped to minimal schema/tables needed
- Application roles with specific grants only

**Example:**

```sql
-- Create read-only analyst role
CREATE ROLE analyst_role;
GRANT CONNECT ON DATABASE mydb TO analyst_role;
GRANT USAGE ON SCHEMA public TO analyst_role;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO analyst_role;

-- Create application write role
CREATE ROLE app_role;
GRANT CONNECT ON DATABASE mydb TO app_role;
GRANT USAGE ON SCHEMA public TO app_role;
GRANT SELECT, INSERT, UPDATE ON TABLE orders TO app_role;
GRANT SELECT, INSERT, UPDATE ON TABLE order_items TO app_role;
-- No DELETE or DDL permissions
```

---

### Protect Sensitive Data

**Rules:**

1. **Do not `SELECT *`** from secrets/PII tables into logs or exports
2. **Mask/redact** sensitive fields in tooling where possible
3. **Limit access** to sensitive tables

**Example:**

```sql
-- Bad: exposes sensitive data
SELECT * FROM users; -- includes SSN, credit card, etc.

-- Good: explicit columns, redacted sensitive fields
SELECT
    user_id,
    username,
    email,
    LEFT(ssn, 3) || '-XX-XXXX' AS ssn_masked,
    'XXXX-XXXX-XXXX-' || RIGHT(credit_card, 4) AS cc_masked
FROM users;
```

---

## Review Checklist

Before running any SQL in production:

- [ ] **Query category understood** (DQL/DML/DDL/DCL/TCL)
- [ ] **DML has a `WHERE`** clause and is proven with equivalent `SELECT`
- [ ] **Transaction strategy is clear** (`BEGIN`/`COMMIT`/`ROLLBACK`/`SAVEPOINT`)
- [ ] **Target set verified** with count and sample before destructive operation
- [ ] **Permissions are least privilege** (DCL changes reviewed)
- [ ] **No secrets/PII leaked** via `SELECT *` or logging
- [ ] **Migration/DDL risk documented** (locks, downtime, rollback plan)
- [ ] **Timeouts configured** for long-running operations
- [ ] **Backup exists** before irreversible operations
- [ ] **Rollback plan documented** in case of issues

---

## Common Patterns

### Bulk Updates with Safety

```sql
BEGIN;

-- Step 1: Create temp table with IDs to update
CREATE TEMP TABLE ids_to_update AS
SELECT user_id FROM users WHERE status = 'pending' AND created_at < '2023-01-01';

-- Step 2: Verify count
SELECT COUNT(*) FROM ids_to_update; -- Record this number

-- Step 3: Perform update using temp table
UPDATE users
SET status = 'archived'
WHERE user_id IN (SELECT user_id FROM ids_to_update);

-- Step 4: Verify results
SELECT COUNT(*) FROM users WHERE status = 'archived' AND user_id IN (SELECT user_id FROM ids_to_update);
-- Should match count from Step 2

COMMIT;

-- Step 5: Clean up
DROP TABLE ids_to_update;
```

---

### Safe Schema Migrations

```sql
-- Pattern: Add column with default, then backfill
BEGIN;

-- Step 1: Add nullable column (fast, no table rewrite)
ALTER TABLE users ADD COLUMN email_verified BOOLEAN DEFAULT NULL;

COMMIT;

-- Step 2: Backfill in batches (separate transaction)
DO $$
DECLARE
    batch_size INT := 1000;
    rows_affected INT;
BEGIN
    LOOP
        UPDATE users
        SET email_verified = false
        WHERE email_verified IS NULL
        LIMIT batch_size;

        GET DIAGNOSTICS rows_affected = ROW_COUNT;
        EXIT WHEN rows_affected = 0;

        COMMIT; -- Commit each batch
        PERFORM pg_sleep(0.1); -- Throttle to avoid load spike
    END LOOP;
END $$;

-- Step 3: Add NOT NULL constraint after backfill
ALTER TABLE users ALTER COLUMN email_verified SET NOT NULL;
```

---

## Integration with PostgreSQL Patterns

For PostgreSQL-specific features, see:

- `postgres-schema-design.md` - Schema patterns, data types
- `postgres-migrations.md` - Migration strategies
- `postgres-performance.md` - Query optimization, indexes
- `postgres-security.md` - Row-level security, audit logging

This SQL engineering guide provides database-agnostic foundations. Combine with PostgreSQL-specific references for complete guidance.
