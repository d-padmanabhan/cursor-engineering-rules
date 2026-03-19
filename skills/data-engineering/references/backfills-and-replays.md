# Backfills and replays

## Backfill runbook template

### 1) Scope

- time range (start/end, timezone)
- partitions/topics/tables affected
- downstream datasets impacted

### 2) Preconditions

- input data availability confirmed
- contract version confirmed
- access/permissions validated

### 3) Idempotency plan

- how duplicates are prevented (upsert/dedupe key)
- how partial publishes are prevented (staging + atomic publish)
- how watermark/offset state is handled

### 4) Validation plan (pre/post)

- row counts in/out with expected deltas
- key uniqueness checks (where required)
- reconciliation vs source (sample or aggregate)
- freshness / lag checks

### 5) Rollback plan

- time travel / clone / versioned outputs / restore strategy
- how consumers are pointed back

> [!WARNING]
> Backfills are production changes. They require explicit validation and rollback, not “just rerun the job”.
