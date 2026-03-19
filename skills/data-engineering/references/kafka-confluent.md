# Kafka / Confluent notes

## Semantics

- Assume at-least-once and make consumers idempotent.
- Define your retry + DLQ strategy; avoid infinite poison-pill loops.

## Schema governance

- Prefer Schema Registry (Avro/Protobuf/JSON Schema) with explicit compatibility policy.
- Treat breaking schema changes like migrations (versioning/dual publish + coordinated rollout).

## Topic design

- Partitioning is an API contract (key semantics, ordering, scalability).
- Choose retention/compaction intentionally.
