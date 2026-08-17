# Decision and Validation Workflow

Use this workflow to prove that architecture complexity serves a measurable outcome. A diagram and an ADR are not evidence by themselves.

## Decision Chain

For each consequential mechanism, complete:

```text
Business outcome:
Critical journey:
Quality-attribute scenario:
Invariant or guarantee:
Facts and evidence:
Assumptions and confidence:
SLI formula and SLO:
Capacity and dependency budgets:
Architecture mechanism:
Failure and overload behavior:
Validation experiment or fitness signal:
Owner:
Reversibility: reversible | costly | effectively irreversible
Review or expiry date:
Rollback trigger:
Revisit trigger:
```

If a component cannot be connected to this chain, remove or defer it.

## Quality-Attribute Scenario

Write a falsifiable scenario:

```text
Given <operating state and load>,
when <stimulus or failure> occurs,
the system must <measurable response>
within <time or error bound>,
while preserving <invariant>,
as verified by <experiment and production signal>.
```

Example:

```text
Given peak checkout load and one unavailable pricing replica,
when a customer submits an order,
99.9% of valid requests complete within 800 ms,
no order is confirmed without an inventory reservation,
and a quarterly dependency-failure exercise plus journey SLI verifies the claim.
```

## SLI and Dependency Budgets

Define user-visible success before component metrics:

```text
availability_sli = successful_eligible_journeys / eligible_journeys
latency_sli = eligible_successful_journeys_within_threshold / eligible_successful_journeys
durability_sli = acknowledged_records_retained / acknowledged_records_due_for_retention
freshness_sli = reads_with_data_age_within_limit / eligible_reads
```

Specify eligibility and exclusions. Do not exclude dependency errors, overload, deployments, or operator mistakes merely because another team owns them.

For a journey requiring independent synchronous dependencies, the product of their availability values is a rough optimistic upper bound:

```text
journey_availability_upper_bound = product(required_dependency_availability)
```

Independence is often false because dependencies share regions, identity, DNS, networks, quotas, or deployment systems. Model correlated failure separately.

Allocate:

- end-to-end latency deadline and per-hop budget;
- availability/error budget across required stages;
- retry budget across the whole call chain;
- concurrency, connection, queue, and memory budgets;
- dependency quotas and failure headroom.

Do not add percentile latencies and call the result an end-to-end percentile. Use budgets for design and validate the full latency distribution under representative load.

## Overload Policy

Define before load arrives:

- admission priority and work that must be rejected first;
- per-tenant or per-principal fairness and hard quotas;
- bounded queue size, maximum age, concurrency, and memory;
- load-shedding response and retry guidance to callers;
- cancellation and deadline propagation;
- user-visible degraded modes;
- recovery from backlog without retry storms.

Measure admitted, rejected, shed, expired, cancelled, and completed work. Alert on user impact and exhaustion, not merely CPU.

## Failure-Domain Map

For each critical journey, list shared failure domains:

| Domain | Shared dependency | Failure effect | Isolation or degraded mode | Validation |
|---|---|---|---|---|
| Region/zone | | | | |
| DNS/network | | | | |
| Identity/policy | | | | |
| Data/control plane | | | | |
| Deployment/config | | | | |
| Quota/account | | | | |
| Observability/audit | | | | |
| Operator/admin | | | | |

Replicas in the same failure domain do not provide independent availability. “Multi-region,” “active-active,” and “cellular” are unproven until shared dependencies and recovery behavior are tested.

## Architecture Fitness

Prefer deterministic, repeatable validation:

- contract and compatibility tests;
- invariant and reconciliation checks;
- load, skew, saturation, and soak tests;
- dependency latency, unavailability, corruption, and quota injection;
- backup restore, regional recovery, and control-plane outage exercises;
- canary and rollback verification;
- cost and unit-economics thresholds;
- ownership, on-call, and runbook exercises.

Record baseline, expected result, stop criteria, observed result, and evidence location. Production telemetry should continue checking the claim after launch.

## Operating-Model Check

Before creating an independently deployed service, cell fleet, or new data platform, verify:

- one accountable team can build, deploy, secure, observe, and recover it;
- on-call and escalation boundaries are independent enough to reduce coupling;
- the team has the required operational expertise and capacity;
- service contracts and dependency ownership are explicit;
- cognitive load and fleet size remain operable;
- the split has a measurable scaling, security, availability, data-ownership, or delivery benefit.

If these conditions are not met, retain a cohesive module or shared deployment boundary and set a concrete extraction trigger.
