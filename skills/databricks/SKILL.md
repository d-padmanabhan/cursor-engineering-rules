---
name: databricks
description: Databricks playbook. Workflows for workspace bootstrap, Unity Catalog migration, Delta Live Tables (DLT) pipeline design, cluster policy rollout, Photon and cost tuning, governance audit, and recovery via Delta time travel. Use when designing, operating, or auditing Databricks.
---

# Databricks - Playbook

**Companion rule:** `481-databricks.mdc`. This skill turns those patterns into end-to-end workflows.

---

## When to invoke

Use when the user is:

- Bootstrapping a new Databricks workspace or account
- Migrating to Unity Catalog (from Hive metastore or no-governance state)
- Designing or reviewing a Delta Live Tables (DLT) pipeline
- Setting cluster policies or rolling out Serverless / SQL Warehouses
- Tuning cost (cluster sizing, Photon, spot, job compute vs all-purpose)
- Governing data (Unity Catalog, tags, access control, lineage)
- Recovering from a bad change (Delta time travel / `RESTORE`)
- Hardening access (SCIM, SSO, service principals, OAuth tokens)

---

## Golden Rules

1. **Unity Catalog is the default.** Hive metastore is for legacy migration only.
2. **Service principals and OAuth**, not personal access tokens, for automation.
3. **Cluster policies enforce** shape, runtime, tags, access mode - users pick from policies, not raw types.
4. **Job compute for jobs.** All-purpose clusters are for exploration.
5. **Delta is the default table format**; Delta Lake for Spark, Delta tables under Unity Catalog.
6. **Lineage and tags are not optional** - govern at ingest, not post hoc.
7. **Every notebook / repo change runs in CI** before it runs against prod data.

---

## Workflow 1 - Workspace Bootstrap

Stand up a new workspace with governance, security, and cost controls from day one.

### Steps

1. **Account-level setup**:
   - Account console used for identity, Unity Catalog metastore, and workspace provisioning
   - SSO via Okta / Entra ID / Google with SCIM provisioning
   - Admin role in a small, audited group
2. **Unity Catalog metastore** per region, tied to cloud storage location (one per region, one per env optionally)
3. **Workspace deployment** via Terraform (`databricks` provider):
   - Network: private subnets, VPC endpoints / Private Link
   - Customer-managed keys for notebooks and workspace storage
   - Workspace bound to specific metastore
4. **Groups and access** (via SCIM from IdP):
   - `admins-<workspace>` - workspace admins
   - `data-engineers-<env>`, `data-analysts-<env>`, `data-scientists-<env>`, `platform-<env>`
   - Keep global admin list tiny
5. **Cluster policies** (see Workflow 4) for all user-facing compute
6. **Catalog structure**:
   - Catalogs per environment (`dev`, `stage`, `prod`) or per domain (`sales`, `marketing`)
   - Schemas within: `raw`, `staging`, `curated`, `sandbox`
   - Default grants minimal; team-specific access roles
7. **External locations + storage credentials** (Unity Catalog) for cloud object storage; no direct S3/ADLS/GCS creds in notebooks
8. **Budget and alerts**:
   - System tables for billing (`system.billing.usage`)
   - Dashboards for cost by workspace / cluster / user / job
   - Alerts on spend anomalies

**Deliverable:** Terraform modules (account, workspace, UC, groups, policies), bootstrap runbook, cost dashboard.

See [references/workspace-bootstrap.md](references/workspace-bootstrap.md).

---

## Workflow 2 - Unity Catalog Migration

Migrate from Hive metastore (or no governance) to Unity Catalog.

### Steps

1. **Inventory**:
   - All databases / tables in Hive
   - Locations (mount points, `dbfs:/mnt/...`, direct S3 paths)
   - Access patterns (who reads / writes)
   - Data pipelines depending on Hive paths
2. **Metastore setup** (if not already done).
3. **External locations** in Unity Catalog for the cloud storage backing the Hive tables.
4. **Catalog and schema creation** that mirrors the source structure (or a better one).
5. **Migration options**:
   - **Upgrade in place**: `SYNC` command for schemas, or `CREATE TABLE ... LIKE ... LOCATION ...` to point UC tables at existing storage
   - **Copy**: `CREATE TABLE ... AS SELECT ...` into new UC tables (physical re-write; expensive but clean)
   - **Dual-write during transition**: write to both Hive and UC, read from UC, retire Hive
6. **Lineage and ownership**:
   - Set UC owner to a group, not a person
   - Add tags for sensitivity, owner, data steward
7. **Access control**:
   - Grants at catalog / schema / table level
   - No `ANONYMOUS FUNCTION` / `ALL PRIVILEGES` sprawl
   - Column-level masking / row filters where needed
8. **Cut over** pipelines and BI:
   - Update SQL Warehouses to use UC as default catalog
   - Update notebooks / jobs to reference `catalog.schema.table` three-part names
   - Disable Hive metastore access path after validation
9. **Decommission** Hive once all reads have moved.

**Deliverable:** Migration plan per database, cutover runbook, rollback plan, governance model (owners, stewards, tags, classifications).

---

## Workflow 3 - Delta Live Tables (DLT) Pipeline Design

DLT for declarative, managed, observable pipelines.

### When DLT

- Streaming / micro-batch SCD pipelines
- Data quality enforcement (expectations) required
- Lineage and observability wanted out of the box
- Team prefers declarative SQL / Python over hand-orchestrated jobs

### When NOT DLT

- One-off batch jobs
- Extensive custom Spark (DLT constrains some APIs)
- Cost sensitivity with low duty cycle (DLT compute has overhead)

### Design

1. **Ingest to raw** (bronze) from cloud storage via Auto Loader or Kafka
2. **Stage** (silver) with schema enforcement, de-dup, CDC via `APPLY CHANGES INTO`
3. **Curated** (gold) for business aggregates / dimensional model
4. **Expectations** on each layer:
   - `@expect_or_drop` for quality-gate columns
   - `@expect_or_fail` for must-pass invariants
   - Track failure counts in DLT event log
5. **Serverless DLT** where available for lower cost and managed sizing
6. **Continuous vs triggered**: continuous for streaming SLAs; triggered for batch windows
7. **Target target_lag** with Dynamic Tables equivalents or DLT settings
8. **Naming and lineage**: three-part UC names end-to-end; tags on every table

### Guardrails

- DLT pipeline in Git; deployed via DABs (Databricks Asset Bundles) or Terraform
- CI: unit tests for transformations, integration test against a dev catalog
- Alerting: DLT event log -> metrics -> alerts on expectation failures and pipeline failures
- Cost budget per pipeline

---

## Workflow 4 - Cluster Policies

Enforce cost, security, and compatibility at cluster-creation time.

### Policies to define

| Policy | Audience | Shape |
|---|---|---|
| `interactive-small` | Data analysts | Single-node or 1-4 workers; auto-terminate 30-60 min; access mode = `User Isolation` |
| `interactive-medium` | Data engineers / scientists | 1-8 workers; auto-terminate 60 min; `User Isolation` |
| `job-compute` | Jobs / DLT | Fixed instance types; no interactive attach; auto-scale caps |
| `ml-gpu` | Data scientists | GPU-enabled types; restricted to ML group; auto-terminate 30 min |
| `shared-serverless-sql` | SQL users | Serverless SQL Warehouse sizes S/M/L, governed by policy |

### Policy content

- **Enforced tags**: `cost_center`, `owner`, `env`, `pipeline` (billable by tag)
- **Runtime pinning** to LTS + latest patch
- **Init scripts** disallowed or restricted to vetted list
- **Access mode** = `User Isolation` (Unity Catalog compatible), not `No Isolation`
- **DBFS / mount usage** disallowed in UC-only workspaces
- **Instance profiles / IAM roles** via managed service credentials

### Terraform

```hcl
resource "databricks_cluster_policy" "interactive_small" {
  name       = "interactive-small"
  definition = jsonencode({
    "spark_version"       = { "type": "fixed", "value": "14.3.x-scala2.12" },
    "autotermination_minutes" = { "type": "range", "minValue": 15, "maxValue": 60 },
    "data_security_mode"  = { "type": "fixed", "value": "USER_ISOLATION" },
    "custom_tags.cost_center" = { "type": "unlimited" },
    # ...
  })
}
```

Then grant `CAN_USE` to the right group.

---

## Workflow 5 - Cost and Performance Tuning

### Levers (ordered by impact)

1. **Right compute type**:
   - Serverless SQL for BI
   - Job compute (not all-purpose) for jobs
   - Serverless DLT where eligible
2. **Photon** on for Spark SQL / DataFrame workloads - almost always faster and cheaper
3. **Auto-scaling** - set min low; max capped by policy
4. **Auto-terminate** - short for interactive; stricter on policies
5. **Spot instances** - on for job compute where tolerant of evictions; never for latency-critical
6. **Instance type** - memory-optimized for big joins; compute-optimized for ML inference; right-size vs spillage
7. **Query** - partition pruning, Z-order, `OPTIMIZE`/`VACUUM` cadence, broadcast joins, caching
8. **Storage**:
   - Delta `OPTIMIZE` weekly (files small) or continuously (`auto optimize`)
   - `VACUUM` retention tuned to recovery needs
   - Liquid Clustering where partitioning would fight the query pattern

### Monitoring

- `system.billing.usage` for DBU cost by workspace, cluster, job, user, tag
- `system.query.history` for slow queries
- `system.compute.*` for cluster utilization
- Cost dashboard per team / product

---

## Workflow 6 - Governance Audit

### Steps

1. **Catalog inventory**: catalogs, schemas, tables, volumes, functions. Owner + tags per table.
2. **Access grants**: pull from `information_schema.*` and Unity Catalog grants. Flag:
   - Grants to `account users` (broad)
   - `ALL PRIVILEGES` at catalog / schema level
   - Non-group grants
3. **Sensitive data**:
   - PII tagged and masked
   - Row filters configured where applicable
   - Tokenization for PCI
4. **Network**:
   - Private Link / VPC endpoints
   - No public workspace access from the internet (IP ACLs, Private Access)
5. **Identity**:
   - SCIM from IdP
   - Personal access tokens rotated or replaced with OAuth
   - Service principals scoped; not in admin groups
6. **Secrets**:
   - Secret scopes used, not hard-coded; scoped to groups
   - Cloud-managed secrets (Key Vault / Secrets Manager) via backed scopes
7. **Audit**:
   - System tables `system.access.audit`, `system.access.table_lineage`, `system.access.column_lineage`
   - Streamed to SIEM; retention per policy
   - Alerts on privilege changes, admin role grants, token creation

---

## Workflow 7 - Recovery via Delta Time Travel

Delta tables preserve history; `RESTORE` brings you back.

```sql
-- Inspect
DESCRIBE HISTORY my_table;

-- Query old state
SELECT * FROM my_table VERSION AS OF 42;
SELECT * FROM my_table TIMESTAMP AS OF '2026-04-19T10:00:00';

-- Restore the table
RESTORE TABLE my_table TO VERSION AS OF 42;
-- or
RESTORE TABLE my_table TO TIMESTAMP AS OF '2026-04-19T10:00:00';
```

### Guardrails

- `VACUUM` retention dictates how far back you can go - set per-table based on recovery needs
- For hard-delete / GDPR: use `VACUUM` with lower retention + explicit delete workflow
- Test `RESTORE` in dev; have a runbook

---

## Anti-patterns

1. Personal access tokens in production code
2. All-purpose clusters running scheduled jobs (expensive, contention)
3. No cluster policies (users pick 32-worker XL for ad-hoc queries)
4. Mount points and DBFS as persistent storage in UC workspaces
5. `USE CATALOG hive_metastore` lingering in prod after UC migration
6. Admin rights granted to groups that include all engineers
7. Notebooks as production code paths (without DABs or CI)
8. No Photon on compute that would benefit
9. Auto-terminate disabled "for convenience"
10. No cost dashboard; surprise bill each month

---

## References

- [references/workspace-bootstrap.md](references/workspace-bootstrap.md) - Terraform-driven workspace + UC setup

## Related

- Rule: `481-databricks.mdc`
- Rule: `480-data-engineering.mdc` (cross-platform data contracts, DQ)
- Rule: `475-sql.mdc` (safe SQL patterns)
- Rule: `316-zero-trust.mdc` (data tier under Zero Trust)
- Skill: `data-engineering` (pipeline concepts)
- Skill: `snowflake` (for comparison)
