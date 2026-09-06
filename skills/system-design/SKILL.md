---
name: system-design
description: Designs and reviews production software systems using requirements, SLOs, capacity estimates, service and data boundaries, consistency, scaling, reliability, security, observability, cost, and migration plans. Use for system design, architecture review, scalability, capacity planning, high availability, multi-tenancy, cell-based or cellular architecture, deployment stamps, technical design documents, or end-to-end production architecture.
---

# Production System Design

Use this skill to turn business requirements and operational constraints into the simplest production architecture that can be built, operated, evolved, and recovered safely.

This is not an interview-diagram generator. Every component and complexity must earn its place through a requirement, measured constraint, or explicit risk.

## System Design Contract

- Start with requirements, constraints, scale, and failure tolerance before selecting technologies.
- Separate facts, assumptions, estimates, and decisions.
- Quantify demand and SLOs enough to expose bottlenecks; never invent precision.
- Tie every consequential mechanism to a quality-attribute scenario, measurable evidence, and a rollback or revisit trigger.
- Prefer a modular monolith or one ownership boundary until independent scaling, deployment, security, data ownership, or team autonomy justifies a split.
- Keep data ownership explicit. Shared databases and synchronous call chains create coupling even when diagrams show separate services.
- Map correlated failure domains and hidden shared dependencies; replicated components are not isolated when they share a control plane, data store, quota, identity service, or deployment path.
- State consistency and durability guarantees at each boundary.
- Design degraded behavior, recovery, and migration, not only the healthy steady state.
- Treat security, privacy, operability, and cost as design inputs, not review-stage additions.
- Verify current vendor limits, guarantees, defaults, and pricing against official sources before relying on them.

## Workflow

### 1. Frame the problem

Capture:

- users, business outcome, and critical journeys;
- functional requirements and explicit non-goals;
- compliance, privacy, residency, and trust boundaries;
- existing system and migration constraints;
- delivery timeline, team ownership, and operational capability.

Ask at most three focused questions that would materially change the architecture. When answers are unavailable, proceed with clearly labeled assumptions and explain their impact.

### 2. Define quality targets

Specify:

- availability and durability targets;
- the SLI numerator, denominator, scope, and exclusion policy for each critical journey;
- latency objectives by critical journey and percentile;
- end-to-end latency and availability budgets allocated across required dependencies;
- throughput, concurrency, data volume, retention, and growth;
- recovery time objective and recovery point objective;
- consistency and freshness requirements;
- cost or resource envelope.

Do not collapse all endpoints and workloads into one SLO.

### 3. Estimate capacity

Show units and arithmetic for baseline, peak, and growth horizon. Estimate requests or events per second, concurrent work, storage, bandwidth, and dominant compute or I/O demand. Include headroom and identify the inputs most sensitive to uncertainty.

Use the design workflow and template (`${HANDBOOK_ROOT}/skills/system-design/references/design-workflow.md`) for estimation and document structure.

### 4. Establish boundaries and contracts

Define:

- system context and external dependencies;
- component or service responsibilities and owners;
- tenancy model, placement boundary, noisy-neighbor controls, and tenant lifecycle;
- synchronous APIs, asynchronous events, and compatibility rules;
- data stores, authoritative ownership, indexes, and lifecycle;
- identity, authorization, encryption, and secret boundaries.

Prefer cohesive boundaries over technology-driven decomposition.

### 5. Design runtime behavior

Trace critical write and read paths. For every remote dependency, state:

- timeout and retry ownership;
- idempotency and duplicate behavior;
- ordering and concurrency requirements;
- admission priority, tenant fairness, bounded queues and concurrency, backpressure, shedding, and user-visible overload behavior;
- one end-to-end retry and deadline budget rather than retries at every layer;
- cache correctness and invalidation;
- partial failure and degraded mode.

Use the networking skill (`${HANDBOOK_ROOT}/skills/networking-transport/SKILL.md`) for transport choices, the service resilience skill (`${HANDBOOK_ROOT}/skills/service-resilience/SKILL.md`) for circuit breakers, bulkheads, retry policy, and degraded behavior, and the distributed transactions skill (`${HANDBOOK_ROOT}/skills/distributed-transactions/SKILL.md`) when one business operation spans consistency boundaries.

### 6. Design operations and recovery

Specify:

- logs, metrics, traces, audit events, dashboards, and alerts;
- health, dependency, saturation, queue-age, and business-invariant signals;
- backup, restore, failover, reconciliation, and disaster-recovery tests;
- failure-domain mapping across region, DNS, identity, configuration, deployment, quotas, observability, and shared control/data planes;
- deployment, rollback, feature flag, and schema migration strategy;
- runbooks, on-call and escalation ownership, operational expertise, cognitive load, and manual intervention.

Use the security testing skill
(`${HANDBOOK_ROOT}/skills/security-testing/SKILL.md`), Zero Trust skill
(`${HANDBOOK_ROOT}/skills/zero-trust/SKILL.md`), and observability skill
(`${HANDBOOK_ROOT}/skills/observability/SKILL.md`) for specialist review.

### 7. Compare alternatives

Compare two or three credible options against the actual requirements. Include:

- benefits and liabilities;
- operational and migration cost;
- failure blast radius;
- lock-in and reversibility;
- validation signal, decision owner, and review or expiry date;
- condition that would invalidate or roll back the choice.

Choose one and record why it is the simplest option that meets the targets. Do not produce a technology shopping list without a decision.

### 8. Plan delivery and validation

Define incremental slices, compatibility transitions, data migration, load and failure testing, production signals, and rollback criteria. Prefer reversible steps and shadowing, canaries, or dual-read verification where appropriate.

## Specialist Routing

Route depth instead of copying domain procedures:

- Cloud architecture: cloud platforms (`${HANDBOOK_ROOT}/skills/cloud-platforms/SKILL.md`)
- API contracts and protocol surfaces: API design (`${HANDBOOK_ROOT}/skills/api-design/SKILL.md`) and mandatory API gates (`${HANDBOOK_ROOT}/rules/320-api-design.mdc`)
- Domain boundaries and models: Domain-Driven Design (`${HANDBOOK_ROOT}/skills/domain-driven-design/SKILL.md`)
- Dependency failure, overload, and isolation: service resilience (`${HANDBOOK_ROOT}/skills/service-resilience/SKILL.md`)
- Logs, metrics, traces, SLOs, alerts, and telemetry pipelines: observability (`${HANDBOOK_ROOT}/skills/observability/SKILL.md`)
- PostgreSQL: database PostgreSQL (`${HANDBOOK_ROOT}/skills/database-postgresql/SKILL.md`)
- Data platforms and pipelines: data engineering (`${HANDBOOK_ROOT}/skills/data-engineering/SKILL.md`)
- Event platforms and Kafka governance: Kafka rule (`${HANDBOOK_ROOT}/rules/483-kafka.mdc`), data engineering (`${HANDBOOK_ROOT}/skills/data-engineering/SKILL.md`), and distributed transactions (`${HANDBOOK_ROOT}/skills/distributed-transactions/SKILL.md`)
- Persistent AI memory and retrieval: memory architecture (`${HANDBOOK_ROOT}/skills/memory-architecture/SKILL.md`)
- Infrastructure implementation and topology automation: infrastructure as code (`${HANDBOOK_ROOT}/skills/infrastructure-iac/SKILL.md`)
- Containers: containers orchestration (`${HANDBOOK_ROOT}/skills/containers-orchestration/SKILL.md`) and Kubernetes containers (`${HANDBOOK_ROOT}/skills/kubernetes-containers/SKILL.md`)
- Architecture visualization: React Flow architecture diagrams (`${HANDBOOK_ROOT}/skills/reactflow-architecture-diagrams/SKILL.md`) or documentation standards (`${HANDBOOK_ROOT}/skills/documentation-standards/SKILL.md`)
- Stakeholder-weighted decisions: multi-perspective review (`${HANDBOOK_ROOT}/skills/multi-perspective-review/SKILL.md`)

## Review Mode

When reviewing an existing design:

1. Restate the claimed requirements and guarantees.
2. Trace critical paths, dependency budgets, tenant/cell placement, and state ownership.
3. Test the design against peak load, unfair tenants, dependency and control-plane failure, regional failure, data corruption, and operator error.
4. Identify unsupported assumptions and missing evidence.
5. Rank findings as Critical, Recommended, or Optional.
6. Propose the smallest correction and how to validate it.

Use the architecture review checklist (`${HANDBOOK_ROOT}/skills/system-design/references/architecture-review-checklist.md`).

For cellular designs, use the cell-based architecture reference (`${HANDBOOK_ROOT}/skills/system-design/references/cell-based-architecture.md`). For consequential decisions, use the decision and validation workflow (`${HANDBOOK_ROOT}/skills/system-design/references/decision-and-validation-workflow.md`).

## Required Output

Produce:

1. Context, requirements, non-goals, and assumptions
2. SLOs and capacity estimates
3. Proposed architecture and critical flows
4. Data ownership and consistency model
5. Reliability, security, observability, and cost controls
6. Alternatives and decision rationale
7. Migration, testing, and rollout plan
8. Risks, unresolved questions, and decision triggers

Distinguish verified evidence from recommendations. Cite current vendor documentation for claims about vendor behavior.
