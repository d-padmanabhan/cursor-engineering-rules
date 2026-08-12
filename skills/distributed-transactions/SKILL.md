---
name: distributed-transactions
description: Designs and reviews cross-service consistency using Transactional Outbox/Inbox, Saga orchestration, Saga choreography, compensating actions, idempotency, and eventual consistency. Use when the user mentions outbox, inbox, saga, orchestration, choreography, compensation, distributed transaction, dual write, CDC relay, duplicate delivery, or cross-service workflow consistency.
---

# Distributed Transactions

Use this skill when one business operation spans services, databases, brokers, or external systems and cannot rely on one local ACID transaction.

## Non-Negotiables

- Prefer one local ACID transaction when the data can remain inside one ownership boundary.
- Never implement a database write followed by direct message publication as an unprotected dual write.
- Assume messages can be delayed, duplicated, reordered, and redelivered.
- Make externally visible commands and consumers idempotent at the business-effect boundary.
- Acknowledging or committing a message is not proof that the business effect occurred exactly once.
- Compensation is a new business action, not a database rollback. It can fail and may require human resolution.
- Persist workflow state, deadlines, attempts, and decisions durably. Do not keep authoritative Saga state only in process memory.
- Bound retries and timeouts; quarantine poison messages and expose reconciliation paths.

## Choose the Simplest Correct Pattern

1. **One service and one database:** use a local transaction.
2. **Publish an event after a local state change:** use Transactional Outbox.
3. **Protect a consumer from duplicate business effects:** use Inbox/deduplication, a domain idempotency key, or both.
4. **A short cross-service flow with clear central ownership and complex compensation:** prefer Saga orchestration.
5. **A loosely coupled event reaction with few participants and no central workflow state:** choreography may fit.
6. **Many ordered steps, long waits, approvals, deadlines, or operational intervention:** use a durable workflow engine or explicit orchestrator.
7. **Strong global atomicity is genuinely mandatory:** reconsider service/data boundaries before reaching for distributed locking or two-phase commit.

## Design Workflow

Before proposing implementation, document:

- business invariant and consistency boundary;
- participating services and data owners;
- commands, events, correlation ID, causation ID, aggregate ID, and idempotency keys;
- state machine, terminal states, deadlines, retry policy, and concurrency policy;
- compensation for each completed step and what cannot be compensated;
- message ordering requirements and partition/routing key;
- duplicate, stale, late, and out-of-order handling;
- operator visibility, reconciliation query, replay policy, and manual-resolution path;
- schema/version evolution and deployment compatibility;
- retention and cleanup for Outbox, Inbox, workflow, and audit records.

Do not start with a framework or broker feature. Start with invariants and failure modes.

## Transactional Outbox and Inbox

Write the domain change and Outbox row in the same local transaction. A separate relay publishes pending rows and marks publication progress without assuming publish-and-mark is atomic. Give each event a stable identifier and enough routing/version metadata for deterministic handling.

Consumers must make duplicate delivery harmless. Record processed message identity in the same local transaction as the business effect where possible. A transport-level dedupe window alone is insufficient for long-lived business guarantees.

Use the [Outbox and Inbox reference](file:///Users/Devesh_Padmanabhan/.cursor/agent-engineering-handbook/skills/distributed-transactions/references/outbox-inbox.md) for schema, relay, CDC, polling, retention, and recovery details.

## Saga Orchestration and Choreography

### Prefer orchestration when

- the workflow has many steps, branches, waits, or deadlines;
- compensation order matters;
- one team owns the end-to-end process;
- operators need one authoritative workflow state;
- participants should not know the full process.

### Prefer choreography when

- reactions are independently valuable and loosely coupled;
- the participant graph is small and understandable;
- no central component needs to decide the next step;
- event contracts and ownership remain clear without circular dependencies.

Choreography is not “no orchestration”; the emergent event graph becomes the workflow and must still be observable, versioned, bounded, and testable.

Use the [Saga reference](file:///Users/Devesh_Padmanabhan/.cursor/agent-engineering-handbook/skills/distributed-transactions/references/saga-orchestration-choreography.md) for state, compensation, isolation anomalies, timeouts, and recovery.

## Reliability Contract

- Use stable operation and message identifiers generated before retries.
- Distinguish retrying transport from retrying the business command.
- Reject or ignore stale state transitions with an explicit version or expected-state check.
- Serialize operations per aggregate when concurrent transitions would violate invariants.
- Keep handlers deterministic around recorded input; isolate nondeterministic calls behind persisted results.
- Use dead-letter handling only with ownership, alerts, replay safety, and a runbook.
- Reconciliation compares authoritative business state to Outbox, Inbox, broker, and workflow state; it does not blindly replay everything.

## Observability

Emit structured events and metrics for:

- workflow state transitions and age;
- relay backlog age and publish attempts;
- duplicate and stale-message counts;
- retry, timeout, compensation, and manual-resolution counts;
- dead-letter depth and oldest-message age;
- correlation and causation across every command and event.

Never log secrets or unrestricted payloads. Prefer identifiers, state, schema version, and redacted failure context.

## Testing

Test failure boundaries, not only the happy path:

- crash after domain commit but before publish;
- publish succeeds but publication marking fails;
- duplicate, delayed, stale, and out-of-order delivery;
- consumer crash before and after local commit;
- concurrent commands for the same aggregate;
- timeout followed by a late success;
- compensation failure and repeated compensation;
- schema version skew during rolling deployment;
- replay from dead-letter storage and reconciliation repair.

Use deterministic fault injection and verify durable state after each interruption.

## Review Output

For a design or code review, report:

1. **Invariant and boundary**
2. **Critical correctness risks**
3. **Chosen pattern and why**
4. **Message/workflow state contract**
5. **Idempotency, ordering, timeout, and compensation behavior**
6. **Recovery and reconciliation**
7. **Tests and operational signals**

Reject vague claims such as “Kafka guarantees exactly once” or “the Saga rolls everything back.” State the actual end-to-end guarantee and its limits.
