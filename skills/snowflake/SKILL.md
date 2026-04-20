---
name: snowflake
description: Snowflake playbook. Workflows for RBAC rollout, warehouse sizing and cost control, secure data sharing, Streams/Tasks/Snowpipe pipelines, permissions audit, and Time Travel / Fail-safe recovery. Use when designing, operating, or auditing Snowflake.
---

# Snowflake - Playbook

**Companion rule:** `482-snowflake.mdc`. This skill turns those patterns into end-to-end workflows.

---

## When to invoke

Use when the user is:

- Designing a new Snowflake account, database, or warehouse
- Rolling out or auditing RBAC (roles, grants, object ownership)
- Tuning cost (warehouse sizing, auto-suspend, query optimization, storage)
- Building pipelines with Snowpipe, Streams, Tasks, or Dynamic Tables
- Setting up secure data sharing (Reader Accounts, Snowflake Marketplace, Private Listings)
- Recovering from a bad change (Time Travel, Fail-safe)
- Governing sensitive data (masking, row access policies, tagging)

---

## Golden Rules

1. **Roles hold privileges; users hold roles.** Never grant directly to users.
2. **Use `USE ROLE` at the top of every script.** Implicit roles cause access-denied mysteries.
3. **Warehouses suspend aggressively** (60s auto-suspend for interactive; higher for streaming).
4. **Right-size warehouses**; scale with multi-cluster, not with XL.
5. **Time Travel is real; Fail-safe is last-resort.** Set retention deliberately per schema.
6. **Every production role chain has an owner and an audit trail.**

---

## Workflow 1 - RBAC Rollout

Design a production-grade role hierarchy and migrate away from `ACCOUNTADMIN`-as-default.

### Steps

1. **Map your access model** to Snowflake's RBAC:
   - **System roles**: `ORGADMIN`, `ACCOUNTADMIN`, `SECURITYADMIN`, `USERADMIN`, `SYSADMIN`, `PUBLIC`
   - **Custom roles**: business- and data-oriented
2. **Use the standard hierarchy**:
   - Functional roles (granted to users): e.g., `ANALYST_SALES`, `ENGINEER_DATA`, `ADMIN_FINOPS`
   - Access roles (hold privileges on objects): e.g., `DB_SALES_READ`, `DB_SALES_WRITE`, `WH_LOAD_USE`
   - Functional roles inherit from access roles, not from each other
3. **Ownership**:
   - Custom databases / schemas / warehouses are OWNED by a custom role (e.g., `DB_SALES_OWNER`), never by `ACCOUNTADMIN`
   - `SYSADMIN` sits above functional roles; custom-role-owned objects grant managed access through their owner role
4. **USE MANAGED ACCESS schemas** for any schema where multiple teams grant access - centralize grant control.
5. **Separation of duties**:
   - `USERADMIN` manages users + role grants; `SECURITYADMIN` manages privilege grants on objects; they do NOT overlap
   - Application service users are locked to a specific role via `DEFAULT_ROLE` and cannot switch
6. **Audit**:
   - Snapshot `GRANTS` to a governance schema nightly (SNOWFLAKE.ACCOUNT_USAGE.GRANTS_TO_ROLES)
   - Alert on new grants to `ACCOUNTADMIN` / `SECURITYADMIN`
7. **Terraform / dbt**:
   - Manage roles and grants via `snowflake-terraform-provider` (Snowflake Labs) or Permifrost (dbt Labs)
   - PR-reviewed changes; drift detection
8. **Migrate existing access** incrementally; lock down `ACCOUNTADMIN`-for-daily-use.

**Deliverable:** Role hierarchy diagram, Terraform modules, audit job, migration runbook.

See [references/rbac-patterns.md](references/rbac-patterns.md).

---

## Workflow 2 - Warehouse Sizing and Cost Control

Keep Snowflake cheap without starving workloads.

### Steps

1. **Classify workloads**:
   - Interactive (BI, ad-hoc) - small/medium WH, multi-cluster auto-scale, short auto-suspend
   - Batch ETL - medium/large WH, single cluster, on-demand
   - Streaming (Snowpipe, Tasks) - small WH, tasks share warehouses
   - ML / heavy - large/xlarge WH, purpose-specific
2. **Start small**, scale on evidence. Double warehouse size only if >50% of query time is spillage or queueing.
3. **Multi-cluster warehouses for concurrency, not for speed**. A bigger warehouse makes one query faster; multi-cluster lets more concurrent queries run at the same speed.
4. **Auto-suspend**:
   - Interactive: 60s
   - Batch / streaming: 60-600s depending on duty cycle
   - Never `AUTO_SUSPEND = 0` in prod
5. **Resource monitors** per warehouse (or per warehouse group):
   - Daily, weekly, monthly credit quotas
   - Actions: notify at 75%, suspend at 100%
   - Owner and escalation path in the notification message
6. **Query tuning**:
   - `EXPLAIN` and `QUERY_HISTORY` the slow queries
   - Prune with clustering keys only when necessary (micro-partition pruning is automatic - test before adding)
   - Materialize results (tables / materialized views) for repeated heavy scans
   - Use Query Acceleration Service for BI workloads with unpredictable heavy queries
7. **Storage**:
   - Time Travel retention appropriate to schema (0 for staging scratch, 1d for most, 7-90d for critical)
   - Transient / temporary tables for scratch
   - Track storage cost by database with ACCOUNT_USAGE.STORAGE_DAILY_HISTORY
8. **Reports**:
   - Weekly top-N queries by credit cost
   - Weekly top-N tables by storage growth
   - Month-over-month trend

**Deliverable:** Warehouse catalog, resource monitors, dashboard, slow-query hit list.

---

## Workflow 3 - Pipeline via Snowpipe / Streams / Tasks / Dynamic Tables

### When to use which

| Use | Why |
|---|---|
| **Snowpipe** | Continuous ingestion from S3/GCS/ADLS into raw tables |
| **Streams** | CDC (change-tracking) on tables; power incremental pipelines |
| **Tasks** | Scheduled or conditional SQL; often reads from streams |
| **Dynamic Tables** | Declarative, managed materialization (prefer over manual Stream+Task where it fits) |
| **Snowflake Connector for Kafka** | Direct Kafka ingestion when latency < Snowpipe is needed |

### Design pattern

```
Cloud storage  --Snowpipe-->  raw.tableRaw (VARIANT)
                                     |
                                     | Stream cdc_raw
                                     v
staging.tableStaged  <--Task-- INSERT/MERGE from raw via stream consumption
                                     |
                                     | Stream cdc_staging
                                     v
warehouse.fact_table  <--Task-- MERGE into dimensional model
```

Or with Dynamic Tables:

```
raw.tableRaw  --> dt_staging (target lag 5 min)  --> dt_fact (target lag 15 min)
```

### Guardrails

- Idempotent MERGE (use stable business keys)
- DLQ table for malformed rows
- Monitoring: unprocessed stream rows, task failure count, ingestion latency
- Alert thresholds and runbook for each pipeline

---

## Workflow 4 - Secure Data Sharing

Share data without moving it.

### Options

- **Listings (Snowflake Marketplace)**: public or private catalog-based sharing
- **Private Listings**: curated access with request workflow
- **Direct Shares**: account-to-account inside the same cloud region; cross-region uses Replication
- **Reader Accounts**: consumer gets a Snowflake account you pay for (to share with non-Snowflake customers)

### Design checklist

- Secure views / secure UDFs for shared objects (prevent data peek via `EXPLAIN`)
- Explicit column selection; no `SELECT *` on shared views
- Row access policies for tenant-level filtering where applicable
- Masking policies for any PII in shared objects
- Document retention / SLA for the share; versioning strategy for schema changes
- Consumer-side usage reported back via `SHARE_USAGE` (governance)

---

## Workflow 5 - Permissions Audit

Quarterly or after any org change.

### Steps

1. **Dump grants** from `SNOWFLAKE.ACCOUNT_USAGE.GRANTS_TO_USERS`, `GRANTS_TO_ROLES`, `GRANTS_ON_OBJECTS`.
2. **Flag**:
   - Direct grants to users (should be zero)
   - `ACCOUNTADMIN` / `SECURITYADMIN` granted to non-service identities beyond a small list
   - Privileges granted to `PUBLIC`
   - Objects owned by `ACCOUNTADMIN` (drift; should be owned by custom role)
3. **Check users**:
   - Disabled / stale users still holding roles
   - Service users without scoped roles
4. **Check network policies**:
   - Service users restricted to known CIDRs / PrivateLink
   - Admin roles require MFA
5. **Masking / row-access policies**:
   - Cover all PII columns?
   - Applied via tags where feasible
6. **File findings** with owner, severity, fix.

---

## Workflow 6 - Recovery via Time Travel and Fail-safe

**Time Travel** = queryable historical data (0-90 days, per-object `DATA_RETENTION_TIME_IN_DAYS`).  
**Fail-safe** = Snowflake-only recovery, 7 days, for permanent tables only, not self-serve.

### Recovery playbook

1. **Quantify the blast radius**: which objects, what time, which rows?
2. **Query the past** with `AT(OFFSET => ...)`, `AT(TIMESTAMP => ...)`, `BEFORE(STATEMENT => ...)`:

   ```sql
   SELECT * FROM my_table AT(OFFSET => -3600); -- 1 hour ago
   SELECT * FROM my_table BEFORE(STATEMENT => '<query_id>');
   ```

3. **Clone** to isolate:

   ```sql
   CREATE TABLE my_table_recovered CLONE my_table AT(OFFSET => -3600);
   ```

4. **Restore** selectively (SQL MERGE from clone).
5. **Undrop** recently-dropped objects:

   ```sql
   UNDROP TABLE my_table;
   ```

6. **If Time Travel is expired**, engage Snowflake support for Fail-safe recovery. Not self-serve; not a plan.

### Prevention

- Set `DATA_RETENTION_TIME_IN_DAYS` per schema (>= 7 for prod, >= 30 for critical)
- `TRANSIENT` tables where durability matters less than cost
- Don't `DROP DATABASE` in prod from a human session; use roles that cannot

---

## Anti-patterns

1. Users with `ACCOUNTADMIN` for daily work
2. Grants direct to users
3. `AUTO_SUSPEND` disabled or very long on interactive warehouses
4. Clustering keys added "for performance" without an `EXPLAIN` showing benefit
5. `SELECT *` across wide VARIANT tables in production queries
6. Secrets in SQL scripts or task definitions (use External Functions + vault)
7. Tasks using `ACCOUNTADMIN` as `OWNER`
8. Shares exposing base tables instead of secure views
9. No resource monitors on shared warehouses
10. No storage / credit dashboard

---

## References

- [references/rbac-patterns.md](references/rbac-patterns.md) - Role hierarchy, ownership, managed access, service accounts

## Related

- Rule: `482-snowflake.mdc`
- Rule: `480-data-engineering.mdc` (cross-platform data contracts, DQ, governance)
- Rule: `475-sql.mdc` (safe SQL patterns)
- Rule: `316-zero-trust.mdc` (data tier controls)
- Skill: `data-engineering` (pipeline concepts)
- Skill: `database-postgresql` (for comparison)
