# Architecture Review Checklist

Review claims against evidence, critical flows, and failure behavior. A missing answer is a finding when it affects correctness or operability.

## Requirements and Evidence

- [ ] Functional requirements, non-goals, constraints, and owners are explicit
- [ ] SLOs apply to specific user journeys and percentiles
- [ ] Capacity estimates show inputs, units, peak factor, growth, and uncertainty
- [ ] Vendor guarantees, limits, defaults, and pricing are verified against current official sources
- [ ] Assumptions have impact and a validation or revisit trigger

## Boundaries and Correctness

- [ ] Components have cohesive responsibilities and named owners
- [ ] Data has one authoritative owner; shared writes are eliminated or justified
- [ ] APIs and events define versioning and compatibility
- [ ] Transaction and consistency boundaries preserve business invariants
- [ ] Idempotency, ordering, concurrency, and duplicate behavior are explicit
- [ ] Cache invalidation and stale-read behavior are defined
- [ ] Time, identity, money, and other sensitive domain semantics use authoritative representations

## Reliability and Recovery

- [ ] Every remote call has bounded timeout, retry ownership, and retry-safety analysis
- [ ] Queues have backpressure, age limits, poison-message handling, and reconciliation
- [ ] Overload behavior protects critical work and downstream dependencies
- [ ] Availability assumptions match each dependency's actual failure domain
- [ ] Partial, regional, and control-plane failures have defined degraded behavior
- [ ] Backup restore, failover, recovery time, and recovery point are tested
- [ ] Late success, duplicate completion, and operator retry cannot corrupt state
- [ ] Rollback distinguishes binaries, schemas, data, and external side effects

## Performance and Scale

- [ ] Read and write paths identify dominant CPU, memory, storage, network, and lock costs
- [ ] Partition keys avoid expected hot spots and preserve required ordering
- [ ] Fan-out and amplification are included in capacity estimates
- [ ] Connection pools, concurrency limits, and quotas are bounded
- [ ] Load testing represents skew, burst, payload, dependency latency, and steady-state duration
- [ ] Scaling signals and target utilization leave failure headroom

## Security and Privacy

- [ ] Authentication and authorization are enforced at every trust boundary
- [ ] Tenant and environment isolation prevent cross-boundary access
- [ ] Data classification, minimization, retention, deletion, and residency are addressed
- [ ] Encryption, key custody, and secret delivery follow least privilege
- [ ] Ingress validation, egress restrictions, rate limits, and abuse controls are defined
- [ ] Audit events answer who did what, when, why, and with what result
- [ ] Threat-model findings have owners and verification

## Observability and Operations

- [ ] Service-level indicators measure user-visible outcomes
- [ ] Logs, metrics, traces, and audit events share correlation identifiers
- [ ] Alerts are actionable and tied to symptoms, saturation, invariants, or exhausted budgets
- [ ] Dashboards expose dependency health, backlog age, capacity, and business completion
- [ ] Runbooks cover diagnosis, mitigation, recovery, and escalation
- [ ] Ownership spans deployment, incidents, migrations, and third-party failures
- [ ] Administrative repair actions are authorized, idempotent, and audited

## Evolvability and Delivery

- [ ] The initial architecture is the simplest one that meets current requirements
- [ ] Service boundaries reflect ownership or scaling needs, not fashion
- [ ] Schema and contract changes support rolling deployment
- [ ] Migration avoids unsafe dual writes and validates data equivalence
- [ ] Rollout is incremental with canaries, stop criteria, and rollback compatibility
- [ ] Irreversible decisions and vendor lock-in are identified
- [ ] Each major decision has a concrete revisit trigger

## Cost and Sustainability

- [ ] Dominant cost drivers and scaling dimensions are modeled
- [ ] Expected, peak, and failure-mode cost are considered
- [ ] Data transfer, retention, observability, and idle capacity are included
- [ ] Operational complexity and staffing are treated as costs
- [ ] Cost controls cannot silently violate reliability or security targets

## Finding Format

```text
Priority: Critical | Recommended | Optional
Claim or gap:
Evidence:
Failure scenario:
Impact:
Smallest correction:
Validation:
Owner or decision needed:
```

## Review Exit Criteria

A design is ready to implement when:

- critical invariants and failure behavior are understood;
- material assumptions are validated or explicitly accepted;
- the selected option meets measurable targets with reasonable headroom;
- migration and rollback paths are credible;
- unresolved risks have owners, deadlines, and containment;
- production validation signals are defined before rollout.
