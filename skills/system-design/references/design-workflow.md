# System Design Workflow and Template

Use this reference to produce a reviewable production design. Delete sections that genuinely do not apply; do not fill them with generic prose.

## Capacity Estimation

Use explicit inputs, units, and a stated peak factor.

Common estimates:

```text
average_requests_per_second = requests_per_day / 86,400
peak_requests_per_second = average_requests_per_second * peak_factor
concurrent_requests = peak_requests_per_second * average_latency_seconds
daily_storage = records_per_day * average_record_bytes * replication_or_overhead_factor
retained_storage = daily_storage * retention_days
network_bytes_per_second = requests_per_second * average_payload_bytes
required_workers = peak_work_per_second * average_work_seconds / target_utilization
```

These are first-order estimates, not capacity promises. Validate them with representative load tests and production telemetry.

For each estimate:

- name the source of every input;
- provide baseline, expected peak, and growth horizon;
- show a range when uncertainty is material;
- include headroom and target utilization;
- identify skew, hot keys, burstiness, and fan-out hidden by averages;
- state the threshold that triggers re-evaluation.

## Architecture Development

### Context and requirements

- Who uses the system and what outcome matters?
- What are the critical reads, writes, workflows, and administrative actions?
- What is explicitly out of scope?
- What existing systems, contracts, teams, dates, and regulations constrain the design?

### Quality attributes

Use measurable targets:

| Attribute | Target | Scope | Evidence or assumption |
|---|---|---|---|
| Availability | | | |
| Latency | | | |
| Throughput | | | |
| Durability | | | |
| Freshness | | | |
| Recovery time | | | |
| Recovery point | | | |
| Retention | | | |
| Cost | | | |

For every critical journey, define the SLI numerator, denominator, scope, and exclusion policy. Allocate end-to-end latency, availability/error, retry, concurrency, and quota budgets across required stages. Treat composed availability as an estimate only and identify correlated dependencies.

Use the decision and validation workflow (`${HANDBOOK_ROOT}/skills/system-design/references/decision-and-validation-workflow.md`) for quality-attribute scenarios, budget arithmetic, fitness signals, and decision lifecycle.

### Context and boundaries

Describe:

- clients and external actors;
- system boundary and trust zones;
- external dependencies and their guarantees;
- component responsibilities and team ownership;
- tenant model, placement, isolation, lifecycle, and noisy-neighbor controls;
- data authority and lifecycle.

Use one context diagram and one component or critical-flow diagram when visuals materially improve understanding. A diagram does not replace contract text.

### Critical flows

For each important flow, document:

1. entry point and authenticated principal;
2. validation and authorization;
3. state reads and writes;
4. remote calls or messages;
5. success response or completion signal;
6. timeout, retry, duplicate, and partial-failure behavior;
7. telemetry and audit evidence.

### Data design

State:

- source of truth and owner for each major entity;
- schema, keys, indexes, and expected access patterns;
- consistency and transaction boundary;
- partitioning, replication, retention, archival, and deletion;
- cache authority and invalidation;
- migration, backfill, reconciliation, and restore.

### Reliability

For each dependency, record:

| Dependency | Failure mode | Detection | Degraded behavior | Recovery |
|---|---|---|---|---|
| | | | | |

Cover overload, latency, unavailability, stale or corrupt data, credential failure, quota exhaustion, and operator error. Avoid automatic retry unless the operation is safe and the retry budget is bounded.

Define admission priority, per-tenant fairness, hard resource bounds, load shedding, cancellation, queue-age limits, and the user-visible degraded outcome.

Map correlated failure domains:

| Domain | Shared dependency | Failure effect | Isolation/degraded mode | Exercise |
|---|---|---|---|---|
| Region/zone | | | | |
| DNS/network | | | | |
| Identity/policy | | | | |
| Data/control plane | | | | |
| Deployment/configuration | | | | |
| Quota/account | | | | |
| Observability/audit | | | | |

### Security and privacy

Document:

- authentication and authorization policy;
- tenant and environment isolation;
- data classification and minimization;
- encryption and key custody;
- secret delivery and rotation;
- ingress and egress policy;
- abuse controls and audit retention;
- threat-model findings and mitigations.

### Operability

Define:

- service-level indicators and error-budget reporting;
- structured logs, metrics, traces, and audit events;
- dashboards and alerts tied to user impact;
- capacity and saturation signals;
- on-call ownership and runbooks;
- operational expertise, cognitive load, service catalog, and escalation boundaries;
- backup/restore and disaster-recovery exercises.

### Cost

Identify dominant cost drivers and scaling dimensions. Compare expected, peak, and failure-mode cost. Include data transfer, retention, idle capacity, observability, third-party API, operational labor, allocation/tagging, anomaly controls, and unit economics such as cost per tenant, request, job, or transaction where material.

## Decision Record

For each consequential choice:

```text
Decision:
Status:
Reversibility: reversible | costly | effectively irreversible
Context and constraints:
Options considered:
Chosen option:
Why:
Consequences:
Evidence:
Validation or fitness signal:
Review or expiry date:
Rollback trigger:
Revisit trigger:
Owner:
```

Prefer explicit revisit triggers such as a throughput threshold, new compliance boundary, unacceptable incident rate, or changed vendor guarantee.

## Migration and Rollout

Sequence toward the target architecture:

1. instrument the current system and establish baseline;
2. introduce compatible contracts and schema changes;
3. backfill or replicate with validation;
4. shadow, dual-read, or canary without creating an unsafe dual write;
5. compare correctness and performance;
6. shift traffic gradually with stop conditions;
7. retain rollback compatibility;
8. remove the old path only after the recovery window.

State data rollback semantics separately from application rollback. A binary rollback cannot automatically reverse committed data or external effects.

## Design Document Template

```markdown
# Design: [System or capability]

## Status and owners

## Context

## Requirements

## Non-goals

## Assumptions and evidence

## SLOs and capacity estimates

## Decision evidence and dependency budgets

## Proposed architecture

## Critical flows

## Data ownership and consistency

## Reliability and recovery

## Tenancy, failure domains, and overload

## Security and privacy

## Observability and operations

## Cost model

## Alternatives considered

## Migration and rollout

## Validation plan

## Risks and open decisions

## Decision record
```
