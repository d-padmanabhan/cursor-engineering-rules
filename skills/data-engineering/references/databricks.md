# Databricks (Delta / Unity Catalog / DLT) notes

## Delta correctness

- Make upserts explicit (for example: `MERGE`) when duplicates/late data exist.
- Define event-time and watermark policy for streaming pipelines.

## Delta maintenance

- `OPTIMIZE`/`ZORDER` should be evidence-driven (small files or chronic scan latency).
- Treat `VACUUM` as destructive; validate retention and time travel requirements first.

## Unity Catalog governance

- Prefer UC object grants over workspace-local permissions.
- Use groups/service principals and least privilege.
