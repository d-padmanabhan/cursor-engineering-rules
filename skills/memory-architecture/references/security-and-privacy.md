# Memory Security and Privacy

Persistent memory expands the duration and blast radius of every ingestion mistake, authorization defect, and disclosure. Treat the ingestion pipeline, canonical store, search index, context assembler, model provider, and lifecycle jobs as separate trust boundaries.

## Threat Model

Protect against:

- Cross-tenant or cross-user retrieval
- Unauthorized writes, approvals, exports, or deletions
- Prompt injection and memory poisoning from source content
- Secrets or personal data stored without purpose or consent
- Sensitive content sent to an embedding or model provider
- Stale, disputed, or superseded claims presented as current
- Deletion that leaves derived chunks, embeddings, caches, or backups searchable
- Shared service identities that prevent attribution
- Inference attacks through repeated searches, counts, or error differences
- Compromised lifecycle jobs that silently escalate trust or rewrite history

## Identity and Authorization

- Authenticate every reader, writer, reviewer, and background workload.
- Use separate workload identities for ingestion, indexing, retrieval, review, and deletion.
- Authorize each operation against tenant, resource, action, purpose, and classification.
- Apply authorization before search and again before context is returned.
- Use short-lived, scoped credentials supplied by the tool or workload layer. Do not expose credentials to the model.
- Deny when identity, tenant, policy, or classification metadata is absent.
- Audit allowed and denied trust decisions with correlation IDs and policy versions.

Namespaces and metadata filters improve organization but are not sufficient authorization controls unless enforced by a trusted policy layer.

## Tenant Isolation

Choose isolation proportional to impact:

- Separate stores, indexes, and keys for high-risk tenants or regulated boundaries
- Separate index partitions with mandatory policy enforcement for lower-risk shared infrastructure
- Per-tenant encryption context and backup boundaries where supported
- Explicit tests proving another tenant's IDs and near-duplicate content cannot be retrieved

Never assemble context from a global candidate set and remove other tenants only after ranking. Filtering must occur before candidate generation.

## Ingestion and Memory Poisoning

Treat every source as untrusted data:

1. Validate type, size, encoding, and required metadata.
2. Identify source principal, acquisition method, and content hash.
3. Classify data and detect secrets or prohibited content.
4. Preserve source text as data, never as system instructions.
5. Extract proposed claims into a lower-trust state.
6. Require deterministic validation or authorized review before approval.
7. Record which parser, model, prompt, and policy version produced each proposal.

Source authority affects evidentiary weight, not whether embedded instructions are executable. An official document can still contain examples, quoted attacks, or text that must not control the agent.

## Sensitive Data

Before storing or embedding content, define:

- Purpose and lawful basis where personal data is involved
- Data owner and approved readers
- Allowed regions and processors
- Retention and deletion obligations
- Whether the content may leave the trust domain
- Whether redaction, tokenization, or field-level encryption is required

Do not store secrets as agent memory. Store references to a secret broker or narrow tool capability. Redact logs and evaluation fixtures.

If an external embedding or model provider is used, verify current provider terms and configuration for retention, training use, residency, encryption, and deletion. Apply egress policy before content leaves the system.

## Encryption and Key Scope

- Encrypt canonical records, indexes, backups, and transport paths.
- Scope keys by environment, tenant, or data class when blast radius requires it.
- Keep key administration separate from memory administration.
- Rotate and revoke access without requiring the model to handle key material.
- Test recovery and deletion behavior for encrypted backups.

Encryption does not replace authorization or prevent a permitted service from returning the wrong tenant's content.

## Human Control

Require explicit human or policy-controlled approval for:

- Promoting inferred claims to approved high-trust memory
- Resolving conflicting approved claims
- Changing tenant or classification
- Extending retention for sensitive records
- Bulk export, bulk deletion, or cross-tenant migration

Approval records must identify the claim version, approver, decision, time, and policy. A model-generated statement that a user approved something is not an approval artifact.

Provide users with a way to inspect, correct, dispute, export, and delete memory about them when required by product policy or law.

## Lifecycle and Deletion

Maintain an inventory of:

- Canonical evidence and claims
- Search chunks and embeddings
- Query and response caches
- Generated summaries that persist
- Replicas, archives, and backups
- Analytics and audit records

A deletion workflow must:

1. Authorize and record the request.
2. Mark the canonical record unavailable immediately.
3. Remove or tombstone derived index entries and caches.
4. Propagate to replicas and downstream stores.
5. Handle backups according to documented policy.
6. Verify the record can no longer be retrieved.
7. Preserve only the minimum audit proof allowed by policy.

## Availability and Failure Behavior

Define behavior for unavailable dependencies:

- Authorization unavailable: fail closed.
- Tenant context missing: fail closed.
- Semantic index unavailable: use an explicitly approved authorized fallback or return an error.
- Review workflow unavailable: retain proposed state; do not auto-approve.
- Deletion propagation failed: keep the record unavailable and alert until cleanup completes.
- Audit sink unavailable: buffer safely or stop sensitive operations according to policy.

## Review Checklist

- [ ] Principals and workload identities are distinct and attributable
- [ ] Tenant and authorization filters run before retrieval
- [ ] Raw sources are treated as untrusted data
- [ ] Trust escalation requires authorized approval
- [ ] Personal data and secrets have explicit handling rules
- [ ] External model and embedding egress is constrained
- [ ] Encryption and key scope match the classification
- [ ] Conflicts, supersession, and deletion preserve auditability
- [ ] Canonical and derived stores share a tested deletion path
- [ ] Cross-tenant, poisoning, inference, and stale-memory tests exist
- [ ] Sensitive operations have deterministic policy and audit events
