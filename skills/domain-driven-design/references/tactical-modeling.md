# Tactical Domain Modeling

Tactical patterns express business rules inside one bounded context. They do not determine distributed topology.

## Building Blocks

### Entity

Use an entity when continuity and identity matter across state changes. Equality follows domain identity, not every attribute.

### Value object

Use an immutable value object when meaning is defined by attributes. Validate it at construction so invalid instances cannot circulate.

Examples include money with currency, date ranges, geographic coordinates, and normalized account references.

### Aggregate

An aggregate is a small consistency boundary:

- one aggregate root controls external mutation;
- every successful command leaves invariants valid;
- one local transaction changes one aggregate;
- other aggregates are referenced by stable identity;
- cross-aggregate reactions use explicit workflows or domain events.

Do not use aggregate boundaries to mirror serialization trees or foreign-key relationships.

### Repository

A repository presents aggregate roots as a domain collection. Its interface uses domain concepts and does not expose ORM, transport, or query-builder details.

Repositories do not belong on every entity. Child entities are loaded and saved through their aggregate root.

### Domain service

Use a domain service for meaningful stateless domain behavior that cannot naturally belong to one entity or value object. Name it in the ubiquitous language.

Do not turn all behavior into services. That creates an anemic domain model.

### Domain event

A domain event is an immutable fact that the domain considers meaningful:

- past-tense business name;
- stable event identity and occurrence time;
- aggregate identity and necessary facts;
- explicit schema version;
- no promise of global ordering unless implemented.

Keep internal domain events distinct from integration events when external contracts require filtering, enrichment, translation, or stronger compatibility.

## Aggregate Design Procedure

For each command:

1. Name the business intent.
2. Identify the invariant that must hold immediately.
3. Determine the minimum state needed to decide.
4. Choose the aggregate root that owns the decision.
5. Validate and mutate only through root behavior.
6. Record resulting domain events.
7. Commit the aggregate and durable publication record atomically when an integration event must follow.
8. Handle cross-aggregate reactions asynchronously or through an explicit Saga when immediate atomicity is impossible.

If an aggregate routinely requires unbounded collections, cross-team locks, or unrelated data, its boundary is probably too large.

## Example

```text
Command: ReserveInventory(order_id, lines)

Aggregate: StockItem per catalog item
Invariant: reserved quantity cannot exceed available quantity
Immediate transaction: reserve one StockItem
Cross-item outcome: orchestration tracks all line reservations
Domain event: InventoryReserved
Failure behavior: release completed reservations through idempotent compensation
```

The order is not one giant aggregate with every stock item. The workflow coordinates multiple aggregate transactions.

## Application and Infrastructure Boundaries

Application services:

- authenticate and authorize the use case;
- load aggregate roots;
- invoke domain behavior;
- control the local transaction;
- persist changes;
- arrange durable event publication;
- translate outcomes to the protocol.

Infrastructure adapters implement repositories, clocks, identity providers, message relays, and external gateways. Domain code depends on ports or domain-facing abstractions, not framework-specific types.

## Testing

Prioritize:

- executable examples in domain language;
- invariant and state-transition tests;
- value-object property tests for boundaries and algebraic rules;
- repository contract tests;
- event schema compatibility tests;
- cross-context consumer-driven or integration contract tests;
- architecture tests preventing forbidden inward dependencies.

Do not mock every entity interaction. Test observable domain behavior and invariants.
