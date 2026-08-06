# Memory Retrieval and Evaluation

Retrieval is an authorization-sensitive ranking system. It must select useful, attributable, current claims without exposing records the caller is not allowed to know.

## Retrieval Sequence

Apply these stages in order:

1. **Resolve request context**
   - Authenticated principal and delegated actor
   - Tenant and authorization scopes
   - Purpose, environment, locale, and time
   - Query classification and context budget
2. **Apply deterministic filters**
   - Tenant and access policy
   - Data classification and purpose restrictions
   - Approved retrieval states
   - Validity interval, retention state, and deletion state
3. **Generate candidates**
   - Exact identifiers and metadata
   - Keyword or full-text search
   - Graph relationships
   - Embedding similarity
4. **Rerank**
   - Query relevance
   - Directness and authority of supporting evidence
   - Domain-specific freshness
   - Review state and conflict status
   - Diversity across sources and claims
5. **Assemble context**
   - Enforce token and item budgets
   - Exclude redundant candidates
   - Surface unresolved conflicts together
   - Return claim IDs, evidence citations, and validity metadata
6. **Audit**
   - Record principal, tenant, policy version, selected claim IDs, index version, and result
   - Redact query text or outputs when classification requires it

Authorization must not be implemented as a similarity penalty. Unauthorized records must be absent from the candidate set.

## Ranking Principles

Avoid one universal trust score. A useful rank combines independent signals whose meaning remains inspectable:

- Relevance to the current query
- Evidence relationship: direct support, indirect support, or contradiction
- Source authority for this specific claim
- Required freshness for the domain
- Claim review and dispute state
- Coverage diversity
- Request purpose and context

Examples:

- A current primary API reference should outrank an old user-confirmed note about an API signature.
- A signed architecture decision may outrank a newer chat transcript about the same decision.
- A current incident status may require recency to dominate historical authority.

Record ranking reasons so reviewers can explain why a claim was selected.

## Duplicate and Conflict Handling

Embedding similarity creates candidates for comparison:

- High similarity may mean duplicate wording, related concepts, or opposing claims.
- Low similarity may still hide a structured contradiction.
- Exact content hashes identify byte-equivalent evidence, not equivalent meaning.

Use deterministic keys where the domain has them, such as `(tenant, subject, predicate, scope, validity_interval)`. Then compare candidate claims:

1. Same meaning and compatible scope: propose a merge or alias.
2. Compatible facts with different detail: preserve both and link them.
3. Mutually incompatible facts: mark both disputed and open a conflict review.
4. Newer approved fact with explicit replacement scope: supersede while preserving lineage.

Do not silently delete or merge canonical records based only on model output.

## Context Assembly

Context quality usually degrades before the model reaches its maximum context size. Define budgets for:

- Maximum claims and evidence excerpts
- Maximum tokens
- Maximum records from one source
- Minimum source diversity when corroboration is required
- Reserved space for instructions, user input, tool output, and response

Prefer concise claim statements with targeted evidence excerpts over entire documents. Keep instructions and retrieved content in distinct channels where the runtime supports it.

## Evaluation Dataset

Build a versioned, representative dataset containing:

- Query and authenticated request context
- Expected relevant claim IDs
- Acceptable alternative claim IDs
- Prohibited claim IDs, including other-tenant and unauthorized records
- Expected conflict or insufficiency behavior
- Freshness cutoff where applicable
- Maximum context budget

Include normal, ambiguous, stale, adversarial, multilingual, and no-answer cases. Synthetic fixtures must not contain production or customer data.

## Core Metrics

Measure at the configured context budget:

- **Precision at k:** selected claims that are relevant
- **Recall at k:** expected claims successfully selected
- **Mean reciprocal rank or normalized discounted cumulative gain:** ordering quality when rank matters
- **Citation correctness:** cited evidence supports the generated claim
- **Grounded response rate:** material assertions are supported by retrieved evidence
- **Stale retrieval rate:** expired or superseded claims selected
- **Conflict surfacing rate:** incompatible relevant claims surfaced together
- **Abstention quality:** insufficient evidence produces an explicit gap instead of fabrication
- **Unauthorized retrieval rate:** selected prohibited records; required target is zero
- **Deletion propagation:** deleted records absent from canonical, index, cache, and output paths
- **Index freshness:** delay between canonical approval or deletion and searchable state
- **Latency, token use, and cost:** measured by request class

Set thresholds from risk and baseline measurements. Do not invent universal precision or latency targets.

## Adversarial and Failure Tests

Test at least:

- Source content containing instructions to ignore policy or reveal secrets
- Cross-tenant near-duplicate documents
- A stale approved claim conflicting with current primary evidence
- Two approved claims that conflict within the same validity scope
- Deleted content remaining in an embedding index or cache
- Index updates delayed or partially failed
- Embedding provider unavailable
- Authorization service unavailable
- Malformed metadata that omits tenant or classification
- Queries designed to infer prohibited data through repeated retrieval

Fail closed on missing identity, tenant, or authorization context. Define degraded behavior separately for unavailable semantic ranking, such as authorized keyword retrieval or explicit temporary failure.

## Release and Rollback

Before rollout:

1. Compare the proposed retriever with the current baseline on the same dataset.
2. Review regressions by risk, not only aggregate score.
3. Confirm isolation and deletion tests pass.
4. Version the schema, index, embedding model, ranking policy, and dataset.
5. Define rollback for canonical writes and derived indexes.
6. Monitor retrieval gaps, policy denials, conflicts, stale results, latency, and cost after release.

Re-evaluate after schema changes, model changes, ranking changes, new tenants, or material shifts in source content.
