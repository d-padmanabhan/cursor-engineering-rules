# Snowflake notes

## Cost and compute

- Use auto-suspend, right-size warehouses, and resource monitors.
- Scale out only for concurrency; avoid paying for idle compute.

## Governance

- RBAC-first; least privilege roles.
- Use masking policies, row access policies, secure views for sensitive data.

## Performance

- Design queries for pruning; avoid unbounded joins and accidental wide scans.
- Add clustering keys only with evidence (persistent pruning issues).
