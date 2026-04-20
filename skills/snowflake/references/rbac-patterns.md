# Snowflake RBAC Patterns

Reference role hierarchy, ownership conventions, and service-account patterns.

---

## Three-Layer Role Model

```
Users
  |
  v
Functional roles      (what a person/service IS; granted to users)
  |                   e.g., ANALYST_SALES, ENGINEER_DATA, ADMIN_FINOPS
  v
Access roles          (what it CAN DO; hold privileges on objects)
  |                   e.g., DB_SALES_READ, DB_SALES_WRITE, WH_LOAD_USE
  v
Snowflake objects     (database, schema, table, warehouse, stage, ...)
```

Rules:

- Users get functional roles only. Never grant access roles directly to users.
- Functional roles inherit access roles via `GRANT ROLE access_role TO ROLE functional_role`.
- `SYSADMIN` sits above functional roles that own objects (`GRANT ROLE owner_role TO SYSADMIN`) so the sysadmin lineage can manage them.

---

## Ownership

| Object | Owner |
|---|---|
| Database | `DB_<name>_OWNER` role, granted to `SYSADMIN` |
| Schema | Same owner role as database, or a schema-specific owner role |
| Table / view / UDF | Inherited from schema (managed access schemas simplify this) |
| Warehouse | `WH_<name>_OWNER` role, granted to `SYSADMIN` |
| Stage (external) | `INT_<name>_OWNER` role |

Never leave objects owned by `ACCOUNTADMIN` in production. Migrate ownership during setup.

---

## Access Roles (examples)

For each resource, define a read / write / admin access role:

```sql
CREATE ROLE DB_SALES_READ;
GRANT USAGE ON DATABASE SALES TO ROLE DB_SALES_READ;
GRANT USAGE ON ALL SCHEMAS IN DATABASE SALES TO ROLE DB_SALES_READ;
GRANT SELECT ON ALL TABLES IN DATABASE SALES TO ROLE DB_SALES_READ;
GRANT SELECT ON FUTURE TABLES IN DATABASE SALES TO ROLE DB_SALES_READ;

CREATE ROLE DB_SALES_WRITE;
GRANT ROLE DB_SALES_READ TO ROLE DB_SALES_WRITE;
GRANT INSERT, UPDATE, DELETE, TRUNCATE ON ALL TABLES IN DATABASE SALES TO ROLE DB_SALES_WRITE;
GRANT INSERT, UPDATE, DELETE, TRUNCATE ON FUTURE TABLES IN DATABASE SALES TO ROLE DB_SALES_WRITE;

CREATE ROLE WH_ANALYTICS_USE;
GRANT USAGE ON WAREHOUSE ANALYTICS_WH TO ROLE WH_ANALYTICS_USE;
```

---

## Functional Roles (examples)

```sql
CREATE ROLE ANALYST_SALES;
GRANT ROLE DB_SALES_READ TO ROLE ANALYST_SALES;
GRANT ROLE WH_ANALYTICS_USE TO ROLE ANALYST_SALES;

CREATE ROLE ENGINEER_DATA;
GRANT ROLE DB_SALES_WRITE TO ROLE ENGINEER_DATA;
GRANT ROLE DB_MARKETING_WRITE TO ROLE ENGINEER_DATA;
GRANT ROLE WH_ETL_USE TO ROLE ENGINEER_DATA;
```

Grant functional roles to users / service users:

```sql
GRANT ROLE ANALYST_SALES TO USER alice@example.com;
```

---

## Managed Access Schemas

For schemas where multiple teams grant access, enable managed access so only the schema owner can grant privileges (not the object owner):

```sql
ALTER SCHEMA SALES.CORE SET MANAGED ACCESS = TRUE;
```

Centralizes control; prevents lateral privilege sprawl.

---

## Separation of Duties

- **`USERADMIN`**: create / manage users, create roles, grant roles to users
- **`SECURITYADMIN`**: grant privileges on objects; inherits `USERADMIN`
- **`SYSADMIN`**: own objects, warehouses; does not grant role-to-user
- **`ACCOUNTADMIN`**: break-glass only; MFA required; audited

Production posture:

- `SECURITYADMIN` should not be doing day-to-day user role grants (use `USERADMIN`)
- `ACCOUNTADMIN` should have 1-3 members max, all humans, all with phishing-resistant MFA, all audited
- No service users with `ACCOUNTADMIN` or `SECURITYADMIN`

---

## Service Users

Application / ETL / BI / reverse-ETL accounts.

```sql
CREATE USER dbt_prod
  DEFAULT_ROLE = ENGINEER_DATA
  DEFAULT_WAREHOUSE = ETL_WH
  MUST_CHANGE_PASSWORD = FALSE
  RSA_PUBLIC_KEY = '...';  -- key-pair auth; no passwords

GRANT ROLE ENGINEER_DATA TO USER dbt_prod;
```

- **Key-pair auth or OAuth**; no password-based service users
- **DEFAULT_ROLE** matches the scope; users cannot escalate via `USE ROLE` beyond granted set
- **Network policy** restricts source IP / PrivateLink
- **Rotate key** on a schedule; store in vault
- **Separate user per integration** - do not share service users across tools

---

## Common Anti-Patterns

- Granting `SELECT ON ALL TABLES IN ACCOUNT` to any role
- Grant to `PUBLIC` role (inherited by every user)
- Direct grants to users
- Objects owned by `ACCOUNTADMIN`
- One role used for both humans and services
- `USERADMIN` held by service users ("but it needs to create users") - use a scoped custom role
- Role names with inconsistent casing or no conventions - impossible to audit

---

## Terraform via `snowflake-terraform-provider`

```hcl
resource "snowflake_role" "analyst_sales" {
  name = "ANALYST_SALES"
}

resource "snowflake_role_grants" "analyst_sales_to_users" {
  role_name = snowflake_role.analyst_sales.name
  users     = ["alice@example.com"]
}

resource "snowflake_grant_privileges_to_role" {
  privileges   = ["USAGE"]
  role_name    = snowflake_role.analyst_sales.name
  on_account_object {
    object_type = "WAREHOUSE"
    object_name = "ANALYTICS_WH"
  }
}
```

Keep roles, grants, and object ownership in the same module for a given business unit. Version-controlled, PR-reviewed, drift-detected.
