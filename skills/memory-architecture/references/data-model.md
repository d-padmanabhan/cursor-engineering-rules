# Memory Data Model

Use separate records for source evidence and normalized claims. Evidence records preserve what was received. Claim records represent what the system currently believes may be useful, with explicit review and lifecycle state.

## Design Requirements

- Stable identifiers survive moves, reindexing, and supersession.
- Every claim references one or more evidence records.
- Tenant, authorization scope, and classification are explicit fields, not naming conventions.
- Confidence includes a rationale and must not replace provenance.
- Validity, review, retention, and deletion are separate concepts.
- Derived chunks and embeddings point back to canonical records and can be rebuilt.

## Evidence Record

```yaml
schema_version: 1
evidence_id: ev_01JABC123
tenant_id: tenant_acme
source:
  type: document
  uri: repo://docs/architecture/identity.md
  authority: internal_primary
  acquired_at: 2026-08-01T12:00:00Z
content:
  sha256: "<content-sha256>"
  media_type: text/markdown
  storage_ref: object://memory-evidence/ev_01JABC123
classification: internal
contains_personal_data: false
ingestion:
  actor_id: workload_memory_ingester
  method: repository_sync
  status: accepted
  warnings: []
retention:
  policy_id: engineering_docs_v1
  review_at: 2027-08-01T00:00:00Z
  delete_at: null
created_at: 2026-08-01T12:00:01Z
```

`authority` describes the source relationship to the claim. It does not make the content trusted instructions. Ingestion still treats the content as untrusted data.

## Claim Record

```yaml
schema_version: 1
claim_id: cl_01JXYZ789
tenant_id: tenant_acme
subject: identity-service
predicate: uses_protocol
object: OpenID Connect
statement: The identity service uses OpenID Connect for user authentication.
evidence_refs:
  - evidence_id: ev_01JABC123
    locator: heading:Authentication
    support: direct
status: approved
confidence:
  level: high
  rationale: Direct statement in the approved architecture document.
review:
  created_by: agent_researcher
  approved_by: user_123
  approved_at: 2026-08-01T12:15:00Z
validity:
  valid_from: 2026-08-01T00:00:00Z
  valid_until: null
  review_at: 2026-11-01T00:00:00Z
classification: internal
authorization_scope:
  readers:
    - group:identity-engineering
relationships:
  supersedes: []
  superseded_by: null
  conflicts_with: []
created_at: 2026-08-01T12:10:00Z
updated_at: 2026-08-01T12:15:00Z
version: 2
```

## Required States

Keep workflow state explicit:

- `proposed`: generated or imported but not reviewed
- `approved`: authorized for normal retrieval
- `disputed`: credible conflicting evidence exists
- `superseded`: replaced by another claim but retained for lineage
- `rejected`: reviewed and not accepted
- `deleted`: tombstone retained only when policy requires proof of deletion

Do not use a single `confidence` field as workflow state. A high-confidence inference remains `proposed` until the required approval occurs.

## Conflict and Supersession

Conflict and supersession represent different facts:

- A **conflict** means two claims cannot both be used safely in the same scope or time interval. Keep both stable IDs and route the pair for resolution.
- **Supersession** means an approved newer claim replaces an older claim for a defined scope or validity period. Preserve the old record and connect both directions.

Moving files into a conflict directory must not change their canonical IDs or break citations. Prefer status and relationship fields over filesystem location as the source of truth.

## Derived Index Record

Search indexes are derived, replaceable state:

```yaml
chunk_id: ch_01JINDEX45
tenant_id: tenant_acme
canonical_type: claim
canonical_id: cl_01JXYZ789
canonical_version: 2
text_sha256: "<normalized-text-sha256>"
embedding_model: "<provider-and-version>"
indexed_at: 2026-08-01T12:16:00Z
```

Store enough information to detect stale index entries and remove every derivative when a canonical record changes or is deleted.

## Domain Extensions

Add fields when the domain requires them, for example:

- Jurisdiction and lawful basis for personal data
- Product, environment, region, or repository scope
- Effective date for policy and regulatory claims
- Source signature or approval record
- Translation relationship and source language

Do not remove tenant, provenance, classification, lifecycle, or stable identifier fields to simplify ingestion. Those fields are the control plane for safe retrieval.
