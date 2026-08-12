# Transactional Outbox and Inbox

Use Outbox to atomically record a domain change and the intent to publish. Use Inbox or domain idempotency to make redelivery harmless at the consumer.

## Outbox Record

A minimal record normally includes:

- globally unique event ID;
- aggregate type, aggregate ID, and aggregate version;
- event type and schema version;
- payload or a durable payload reference;
- correlation and causation IDs;
- creation time;
- publication status, attempt count, and next-attempt time;
- lease owner and lease expiry when polling concurrently;
- publication time or broker metadata when available.

Generate event identity before retryable work. Never derive identity from a relay attempt.

## Atomic Producer Transaction

Inside one database transaction:

1. validate the expected aggregate state or version;
2. apply the domain change;
3. insert the Outbox record;
4. commit.

The broker call occurs outside this transaction. If the local transaction rolls back, neither business state nor publication intent survives.

Do not mark a row published before the broker acknowledges publication. If publication succeeds and marking fails, the relay will publish again; consumer idempotency is therefore mandatory.

## Relay Choices

### Polling publisher

Use when:

- database polling is operationally acceptable;
- portability and implementation simplicity matter;
- modest publication latency is acceptable.

Requirements:

- claim bounded batches with a lease or database-supported skip-locked pattern;
- preserve per-aggregate order where required;
- avoid holding transactions open during broker calls;
- use bounded retries with jitter;
- measure oldest-pending age, batch latency, failures, and abandoned leases.

### Change data capture relay

Use when:

- lower latency or high throughput justifies CDC infrastructure;
- the database log and connector are supported operationally;
- schema and connector lifecycle ownership is clear.

CDC removes application polling but does not remove duplicate delivery, schema evolution, offset recovery, or consumer idempotency. Treat connector offsets and publication state as production data with backup and recovery procedures.

## Ordering

Global order is usually unnecessary and expensive. State the narrow ordering invariant:

- per aggregate;
- per account, order, or workflow;
- no ordering requirement.

Route related events to the same broker partition when transport order is required. Include aggregate version and make consumers reject, defer, or reconcile stale and future versions explicitly.

## Consumer Inbox

In one local consumer transaction:

1. attempt to insert the message ID into an Inbox table with a unique constraint;
2. if it already exists, return the previously recorded outcome or safely acknowledge;
3. validate expected domain state/version;
4. apply the business effect;
5. record any resulting Outbox events;
6. commit;
7. acknowledge the message.

When the external side effect cannot share the transaction, use the provider's idempotency key, a durable command state machine, or a compensating/reconciliation process. An Inbox row written before an unprotected external call can suppress a needed retry; one written after the call can permit duplicates.

## Retention and Cleanup

Retention must exceed the longest credible replay, redelivery, incident-recovery, and audit window. Clean records in bounded batches and preserve identifiers required for idempotency.

Before deleting:

- verify publication and consumer retention assumptions;
- account for restored backups and delayed dead-letter replay;
- preserve immutable audit evidence where required;
- monitor cleanup lag and failures.

## Reconciliation

Provide queries or jobs that detect:

- committed domain changes without Outbox intent;
- pending or repeatedly failing Outbox records;
- broker publications without expected downstream state;
- Inbox records without completed business effects;
- aggregate version gaps or permanent future-version messages.

Repair must be idempotent, scoped, reviewed, and auditable. Do not use unrestricted bulk replay as the default recovery mechanism.

## Anti-Patterns

- Database commit followed by an unprotected broker publish
- Deleting Outbox rows immediately after send
- Treating broker producer idempotence as end-to-end exactly once
- Deduplicating only in memory or cache without a durable business guarantee
- Using payload hashes as message identity when two legitimate events can have the same payload
- One global ordered partition for unrelated aggregates
- Retrying poison messages forever
