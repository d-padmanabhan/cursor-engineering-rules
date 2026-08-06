# Local-File Memory Pattern

Use local files when the knowledge volume is modest, concurrency is low, and repository or operator access controls match the data classification. Files are not a substitute for a database when multiple writers, fine-grained authorization, high query volume, or regulated deletion require transactional enforcement.

## Choose the Persistence Boundary

Do not use one directory for every memory class.

### Ephemeral Session Context

```text
<repo-root>/tmp/agent-context/
├── active-context.md
├── progress.md
└── handoff.md
```

- Gitignored and replaceable
- Appropriate for current work and handoffs
- Safe to clean after the task
- Not the only copy of durable project knowledge

### Versioned Repository Knowledge

```text
<repo-root>/knowledge/
├── schema/
├── evidence/
├── claims/
├── conflicts/
└── manifests/
```

Use when:

- The content is approved for every repository reader
- Git history is an acceptable retention and deletion model
- Review through pull requests is valuable
- The repository is the intended system of record

Do not commit secrets, customer data, personal notes, or content whose deletion obligations conflict with immutable Git history.

### Private Durable Local Knowledge

Use an operator-owned directory or local database outside disposable repository paths:

```text
<durable-memory-root>/
├── canonical/
│   ├── evidence/
│   └── claims/
├── index/
├── audit/
└── backups/
```

Document:

- Absolute ownership and permissions
- Encryption and key location
- Backup destination and recovery test
- Retention and secure deletion behavior
- Whether synchronization to another machine is allowed

A local directory is not team memory unless a supported synchronization, authorization, concurrency, and recovery design exists.

## Canonical and Derived State

Treat these as canonical:

- Evidence records and their approved storage references
- Claim records and review state
- Stable identifiers and relationships
- Retention, deletion, and authorization metadata

Treat these as derived and replaceable:

- Full-text indexes
- Embeddings and vector indexes
- Chunk files
- Query caches
- Generated context bundles

Derived records must include the canonical ID, canonical version, and index version. A rebuild should produce a usable index without inventing missing canonical data.

## Safe File Updates

For each canonical write:

1. Validate the record against a versioned schema.
2. Verify tenant, classification, actor, and authorization metadata.
3. Acquire a lock or enforce a single-writer boundary.
4. Write the complete new content to a temporary file in the same filesystem.
5. Flush the file and atomically replace the canonical path.
6. Append an audit event without sensitive body content.
7. Queue index updates with the canonical ID and version.
8. Verify the index reports the new version before declaring the update complete.

Do not overwrite a file incrementally or update canonical and index files as if two filesystem renames formed a transaction. The canonical write succeeds first; the index is reconciled asynchronously and monitored for lag.

For multiple concurrent writers or multi-record invariants, use a transactional database instead of adding increasingly complex lock files.

## Stable Identifiers

Do not derive canonical IDs only from file paths. Renames and conflict review must not break citations.

Use:

- An opaque stable ID generated once
- A content hash for idempotent evidence ingestion
- A version field for optimistic concurrency
- Human-readable slugs only as navigation aids

Maintain an ID-to-path manifest when files are used:

```yaml
schema_version: 1
records:
  ev_01JABC123:
    path: evidence/2026/identity-architecture.yaml
    version: 1
    sha256: "<record-sha256>"
  cl_01JXYZ789:
    path: claims/identity-service-protocol.yaml
    version: 2
    sha256: "<record-sha256>"
```

Validate the manifest for duplicate IDs, missing files, hash mismatches, and references to unknown IDs.

## Conflict Review

Keep conflicts as workflow metadata, not only as folders:

1. Create or update each canonical claim independently.
2. Add reciprocal `conflicts_with` relationships.
3. Set review state to `disputed` where policy requires it.
4. Create a review item that references the stable claim IDs.
5. Preserve both claims until an authorized decision.
6. If one claim supersedes another, record scope and validity before changing status.

A `conflicts/` directory may hold review artifacts, but moving canonical files there must not be the only conflict signal.

## Backups and Recovery

- Versioned repository knowledge uses the repository remote and its retention policy only when that policy satisfies recovery requirements.
- Private local knowledge needs encrypted backups outside the primary device.
- Back up canonical state and required audit metadata before derived indexes.
- Test restoration into an isolated location.
- Verify restored claims still resolve their evidence references.
- Rebuild indexes from restored canonical state and compare record counts and versions.

Backups must follow the same tenant, classification, retention, and deletion controls as the primary store.

## Migration Triggers

Move from files to a database or managed knowledge service when any of these becomes material:

- Multiple concurrent writers
- Per-record or per-tenant authorization
- Transactions across records
- Large-scale retention or deletion requests
- Search indexes that cannot be rebuilt within recovery objectives
- High update rates or low-latency freshness requirements
- Audit requirements beyond filesystem and Git history
- Replication across teams, regions, or environments

Preserve stable IDs and exportable canonical records so changing the storage engine does not change the knowledge contract.
