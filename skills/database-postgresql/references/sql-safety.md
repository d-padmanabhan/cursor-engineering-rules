# SQL command categories and safety guardrails

SQL is broader than `SELECT`. The command category tells you the **risk**, **permissions**, and **rollback strategy**.

## Categories

### DQL - Data Query Language (read-only)

- `SELECT`
- Common clauses: `FROM`, `WHERE`, `GROUP BY`, `HAVING`, `ORDER BY`, `LIMIT`, `OFFSET`

### DML - Data Manipulation Language (changes row contents)

- `INSERT`, `UPDATE`, `DELETE`, `MERGE` (if supported)

> [!CAUTION]
> Most “oops” incidents come from DML without validating the target rowset first.

### DDL - Data Definition Language (changes schema/objects)

- `CREATE`, `ALTER`, `DROP`, `TRUNCATE`, `RENAME`

> [!WARNING]
> DDL can take locks and break applications quickly. Treat schema changes as code: reviewed, tested, staged.

### DCL - Data Control Language (permissions)

- `GRANT`, `REVOKE`

### TCL - Transaction Control Language (atomicity and recovery)

- `BEGIN` / `START TRANSACTION`, `COMMIT`, `ROLLBACK`, `SAVEPOINT`

---

## Destructive-operation guardrails

### Safe UPDATE/DELETE workflow

1. Write the equivalent `SELECT` first to prove the rowset
2. Record expected row count and sample primary keys
3. Wrap the change in a transaction
4. Verify post-conditions, then `COMMIT`

> [!IMPORTANT]
> Never run `UPDATE` or `DELETE` without a `WHERE`.

### Prefer small, reviewable changes

- Use immutable IDs, not names
- Prefer `RETURNING` where supported to review what changed
- Use `LIMIT` only when it’s deterministic (e.g., ordered by PK) - otherwise you can get unpredictable results

### TRUNCATE vs DELETE

- `TRUNCATE` removes all rows fast but can be hard to recover from
- `DELETE` can be scoped and can be rolled back (in a transaction)

---

## Transaction tips

- Use `SAVEPOINT` for complex multi-step changes
- Avoid long-running transactions in production (locks, bloat, replication lag)
- Use statement/lock timeouts when supported for production migrations
