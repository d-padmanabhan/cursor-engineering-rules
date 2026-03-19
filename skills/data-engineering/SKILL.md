---
name: data-engineering
description: Data engineering workflows for designing and reviewing batch/streaming pipelines across Databricks, Snowflake, Confluent Kafka, and Teradata (contracts, backfills, quality, governance, cost, observability). Use when the user mentions data engineering, ETL/ELT, lakehouse/warehouse, Kafka, Databricks, Snowflake, or Teradata.
---

# Data Engineering

## Scope

Use this skill to:

- Review data pipeline PRs (batch or streaming)
- Design new datasets, ingestion pipelines, and transformations
- Plan backfills/replays safely
- Apply platform-specific guidance for Databricks, Snowflake, Confluent Kafka, and Teradata

## Core principles (defaults)

- **Idempotent**: safe to re-run for a given window/offset
- **Contract-driven**: schema + semantics + SLA are explicit
- **Observable**: each run emits counts, timings, and progress/watermarks
- **Governed**: least privilege, masking/row filtering for sensitive data
- **Cost-aware**: incremental + pruning by default; avoid full scans

## Quick start: PR review workflow (local)

1. Determine base branch (usually `main`).
2. Collect git facts:

```bash
git branch --show-current
git log main..HEAD --oneline
git diff --name-status main...HEAD
git diff --numstat main...HEAD
git diff main...HEAD
```

1. Review using the structure below.

### Review output format

- **Critical**: correctness, data loss/duplication, security/PII leaks, breaking contracts
- **Recommended**: performance/cost risks, operational gaps, maintainability
- **Optional**: style, naming, documentation improvements

## Quick start: design workflow (new pipeline / dataset)

Produce a short design covering:

- **Inputs**: sources, formats, volumes, SLAs
- **Contract**: schema, keys, semantics (event vs processing time), evolution policy
- **Processing**: batch vs streaming, watermarking/offset tracking, dedupe/upsert strategy
- **Outputs**: layers (raw/curated/serving), consumers, downstream blast radius
- **Quality**: freshness/volume/uniqueness checks, quarantine strategy
- **Security**: PII classification, masking/row filters, least privilege
- **Ops**: alerting, retries, DLQ/quarantine, runbook for backfills
- **Cost**: partitioning/pruning, incremental strategy, warehouse sizing (if relevant)

## Platform-specific rule pointers

When relevant, apply these rules (in addition to `475-sql.mdc` and `480-data-engineering.mdc`):

- **Databricks**: `rules/481-databricks.mdc`
- **Snowflake**: `rules/482-snowflake.mdc`
- **Kafka / Confluent**: `rules/483-kafka.mdc`
- **Teradata**: `rules/484-teradata.mdc`

## References

- [references/contracts-and-evolution.md](references/contracts-and-evolution.md)
- [references/backfills-and-replays.md](references/backfills-and-replays.md)
- [references/databricks.md](references/databricks.md)
- [references/snowflake.md](references/snowflake.md)
- [references/kafka-confluent.md](references/kafka-confluent.md)
- [references/teradata.md](references/teradata.md)
