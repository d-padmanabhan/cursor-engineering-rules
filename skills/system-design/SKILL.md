---
name: system-design
description: Designs and reviews production software systems using requirements, SLOs, capacity estimates, service and data boundaries, consistency, scaling, reliability, security, observability, cost, and migration plans. Use when the user asks for system design, architecture design, architecture review, scalability, capacity planning, high availability, a technical design document, or an end-to-end production architecture.
---

# Production System Design

Use this skill to turn business requirements and operational constraints into the simplest production architecture that can be built, operated, evolved, and recovered safely.

This is not an interview-diagram generator. Every component and complexity must earn its place through a requirement, measured constraint, or explicit risk.

## System Design Contract

- Start with requirements, constraints, scale, and failure tolerance before selecting technologies.
- Separate facts, assumptions, estimates, and decisions.
- Quantify demand and SLOs enough to expose bottlenecks; never invent precision.
- Prefer a modular monolith or one ownership boundary until independent scaling, deployment, security, data ownership, or team autonomy justifies a split.
- Keep data ownership explicit. Shared databases and synchronous call chains create coupling even when diagrams show separate services.
- State consistency and durability guarantees at each boundary.
- Design degraded behavior, recovery, and migration—not only the healthy steady state.
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
- latency objectives by critical journey and percentile;
- throughput, concurrency, data volume, retention, and growth;
- recovery time objective and recovery point objective;
- consistency and freshness requirements;
- cost or resource envelope.

Do not collapse all endpoints and workloads into one SLO.

### 3. Estimate capacity

Show units and arithmetic for baseline, peak, and growth horizon. Estimate requests or events per second, concurrent work, storage, bandwidth, and dominant compute or I/O demand. Include headroom and identify the inputs most sensitive to uncertainty.

Use the [design workflow and template](file:///Users/Devesh_Padmanabhan/.cursor/agent-engineering-handbook/skills/system-design/references/design-workflow.md) for estimation and document structure.

### 4. Establish boundaries and contracts

Define:

- system context and external dependencies;
- component or service responsibilities and owners;
- synchronous APIs, asynchronous events, and compatibility rules;
- data stores, authoritative ownership, indexes, and lifecycle;
- identity, authorization, encryption, and secret boundaries.

Prefer cohesive boundaries over technology-driven decomposition.

### 5. Design runtime behavior

Trace critical write and read paths. For every remote dependency, state:

- timeout and retry ownership;
- idempotency and duplicate behavior;
- ordering and concurrency requirements;
- backpressure, admission control, and overload behavior;
- cache correctness and invalidation;
- partial failure and degraded mode.

Use the [networking skill](file:///Users/Devesh_Padmanabhan/.cursor/agent-engineering-handbook/skills/networking-transport/SKILL.md) for transport choices and the [distributed transactions skill](file:///Users/Devesh_Padmanabhan/.cursor/agent-engineering-handbook/skills/distributed-transactions/SKILL.md) when one business operation spans consistency boundaries.

### 6. Design operations and recovery

Specify:

- logs, metrics, traces, audit events, dashboards, and alerts;
- health, dependency, saturation, queue-age, and business-invariant signals;
- backup, restore, failover, reconciliation, and disaster-recovery tests;
- deployment, rollback, feature flag, and schema migration strategy;
- runbooks, ownership, escalation, and manual intervention.

Use the [security testing skill](file:///Users/Devesh_Padmanabhan/.cursor/agent-engineering-handbook/skills/security-testing/SKILL.md), [Zero Trust skill](file:///Users/Devesh_Padmanabhan/.cursor/agent-engineering-handbook/skills/zero-trust/SKILL.md), and [observability rule](file:///Users/Devesh_Padmanabhan/.cursor/agent-engineering-handbook/rules/330-observability.mdc) for specialist review.

### 7. Compare alternatives

Compare two or three credible options against the actual requirements. Include:

- benefits and liabilities;
- operational and migration cost;
- failure blast radius;
- lock-in and reversibility;
- condition that would invalidate the choice.

Choose one and record why it is the simplest option that meets the targets. Do not produce a technology shopping list without a decision.

### 8. Plan delivery and validation

Define incremental slices, compatibility transitions, data migration, load and failure testing, production signals, and rollback criteria. Prefer reversible steps and shadowing, canaries, or dual-read verification where appropriate.

## Specialist Routing

Route depth instead of copying domain procedures:

- Cloud architecture: [cloud platforms](file:///Users/Devesh_Padmanabhan/.cursor/agent-engineering-handbook/skills/cloud-platforms/SKILL.md)
- APIs: [API design rule](file:///Users/Devesh_Padmanabhan/.cursor/agent-engineering-handbook/rules/320-api-design.mdc)
- PostgreSQL: [database PostgreSQL](file:///Users/Devesh_Padmanabhan/.cursor/agent-engineering-handbook/skills/database-postgresql/SKILL.md)
- Data platforms and pipelines: [data engineering](file:///Users/Devesh_Padmanabhan/.cursor/agent-engineering-handbook/skills/data-engineering/SKILL.md)
- Containers: [containers orchestration](file:///Users/Devesh_Padmanabhan/.cursor/agent-engineering-handbook/skills/containers-orchestration/SKILL.md) and [Kubernetes containers](file:///Users/Devesh_Padmanabhan/.cursor/agent-engineering-handbook/skills/kubernetes-containers/SKILL.md)
- Architecture visualization: [React Flow architecture diagrams](file:///Users/Devesh_Padmanabhan/.cursor/agent-engineering-handbook/skills/reactflow-architecture-diagrams/SKILL.md) or [documentation standards](file:///Users/Devesh_Padmanabhan/.cursor/agent-engineering-handbook/skills/documentation-standards/SKILL.md)
- Stakeholder-weighted decisions: [multi-perspective review](file:///Users/Devesh_Padmanabhan/.cursor/agent-engineering-handbook/skills/multi-perspective-review/SKILL.md)

## Review Mode

When reviewing an existing design:

1. Restate the claimed requirements and guarantees.
2. Trace critical paths and state ownership.
3. Test the design against peak load, dependency failure, regional failure, data corruption, and operator error.
4. Identify unsupported assumptions and missing evidence.
5. Rank findings as Critical, Recommended, or Optional.
6. Propose the smallest correction and how to validate it.

Use the [architecture review checklist](file:///Users/Devesh_Padmanabhan/.cursor/agent-engineering-handbook/skills/system-design/references/architecture-review-checklist.md).

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
