# Data contracts and evolution

## Contract template (minimum)

- **Dataset/topic name**
- **Owner** (team) + oncall
- **SLA/SLO** (freshness/availability)
- **Schema** (types, nullability, defaults)
- **Keys**
  - natural/business keys (if any)
  - surrogate keys (if any)
  - dedupe key (if duplicates possible)
- **Time semantics**
  - event time column (definition)
  - processing time meaning (if used)
  - late arrival policy (max lateness)
- **Ordering semantics** (if applicable)
- **Evolution policy**
  - additive changes allowed?
  - breaking changes process (versioning/dual publish)?

> [!IMPORTANT]
> A “schema-only” contract is insufficient. Semantics (units, currency, time zones, enum meaning) must be explicit.

## Evolution rules of thumb

- Prefer **additive** changes (new nullable column) over destructive changes.
- Breaking changes should be handled with:
  - **versioned outputs** or **dual publish**
  - coordinated consumer rollout
  - explicit rollback plan
