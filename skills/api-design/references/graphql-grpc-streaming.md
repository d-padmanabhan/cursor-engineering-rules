# GraphQL, gRPC, Batch, and Streaming APIs

Alternative interface styles do not relax authentication, authorization,
validation, bounded execution, compatibility, or observability requirements.

## GraphQL

### Schema and Authorization

- Design the schema around consumer tasks without exposing persistence objects
  mechanically.
- Authorize every sensitive object, field, relationship, mutation, and
  subscription in trusted resolver or policy code.
- Prevent input fields such as role, owner, tenant, price, or approval state
  from bypassing policy.
- Use cursor connections with bounded `first` or `last` values and stable
  ordering.
- Define nullability and error propagation deliberately.
- Avoid exposing sensitive fields merely because another resolver already
  loaded the object.

### Demand Control

Bound:

- document bytes;
- operation count per request;
- depth and breadth;
- aliases and duplicated selections;
- list multipliers and field cost;
- variables and input nesting;
- resolver time and downstream calls;
- batch requests;
- subscriptions per principal;
- response bytes and execution time.

Apply per-principal rate and cost limits. Static depth alone is not sufficient
because shallow queries can fan out broadly.

Use request-scoped DataLoader instances. A process-global loader can leak cached
objects across users or tenants. Include authorization-relevant context in any
cache key and avoid caching forbidden results across principals.

For public APIs, consider trusted or persisted operations when client and
deployment constraints permit them. Define introspection policy by environment
and consumer need. Disabling introspection is not an authorization control.

### GraphQL Verification

Test field-level authorization, aliases, fragments, nested lists, batching,
cost limits, resolver cancellation, N+1 behavior, error redaction,
subscriptions, and cross-request loader isolation.

## gRPC and Protobuf

### RPC Contract

- Set and propagate deadlines and cancellation.
- Authenticate and authorize through interceptors plus method or resource
  policy, not network location.
- Bound message size, stream duration, concurrent streams, and in-flight work.
- Retry only safe or idempotent methods according to an explicit service
  configuration.
- Define health, readiness, overload, and graceful shutdown behavior.
- Use rich error details based on `google.rpc.Status` where ecosystem support
  is validated; keep client-safe messages and stable machine details.
- Define streaming flow control, half-close, cancellation, idle timeout, and
  keepalive behavior.

### Protobuf Compatibility

- Never renumber or reuse field tags.
- Reserve removed field numbers and names.
- Never reuse enum numeric values with a different meaning.
- Prefer additive fields and methods.
- Do not change wire types, singular/repeated cardinality, or field semantics
  incompatibly.
- Define presence, default, unknown-field, and enum-unknown behavior.
- Use bounded `page_size` and opaque `page_token` fields for list methods.
- Run Protobuf breaking-change checks against the supported baseline.

Authentication, authorization, quotas, and idempotency belong in the RPC
contract even when they are not represented directly in the `.proto` file.

Use the networking transport skill
(`${HANDBOOK_ROOT}/skills/networking-transport/SKILL.md`) for HTTP/2,
connections, keepalive, flow control, and wire-format trade-offs.

## Batch APIs

Prefer ordinary operations or asynchronous jobs unless batching materially
reduces cost or latency.

When a batch endpoint is justified:

- allowlist operations rather than accepting arbitrary internal paths;
- apply the same authentication and authorization as standalone operations;
- validate every item and bound total items, bytes, concurrency, and time;
- define all-or-nothing versus best-effort semantics;
- define item ordering and dependency behavior;
- use per-item stable identity and idempotency when effects can be retried;
- return safe per-item status or Problem Details;
- prevent one expensive item from monopolizing the batch;
- avoid exposing raw exception or rejection objects.

For large or long-running batches, create an asynchronous job resource.

## Server-Sent Events

Define:

- authentication at connection time and reauthorization policy;
- authorization for each stream or topic;
- replay and `Last-Event-ID` semantics;
- event IDs, schema versions, ordering, and retention;
- heartbeat interval and intermediary idle timeouts;
- connection, tenant, and subscription quotas;
- backpressure, slow-client, and disconnect behavior;
- token expiry and revocation;
- reconnection and duplicate handling.

Do not place secrets in URLs because URLs commonly appear in logs and browser
history.

## WebSockets

Define:

- origin policy for browser clients;
- authenticated handshake and token-expiry behavior;
- authorization for every message type and subscription;
- versioned message schemas;
- maximum frame and message sizes;
- rate, connection, subscription, and in-flight limits;
- ping, pong, idle, read, write, and total session timeouts;
- backpressure and slow-consumer behavior;
- reconnect, resume, ordering, and duplicate semantics;
- server shutdown and connection draining.

Parse each message into a constrained schema before dispatch. Never let a
client-supplied action name invoke arbitrary application methods.

## Webhooks

Inbound and outbound webhook security, replay, idempotency, SSRF, and durable
delivery requirements are defined in the API security and resilience reference
(`${HANDBOOK_ROOT}/skills/api-design/references/security-resilience.md`).

Document event types, schema versions, delivery IDs, ordering guarantees,
retry schedule, disablement policy, secret rotation, retention, and
reconciliation. A webhook is an at-least-once notification unless a stronger
end-to-end guarantee is explicitly implemented and proven.

## Verification

Apply deterministic fault and abuse tests:

- GraphQL cost, authorization, alias, batch, and loader-isolation tests;
- gRPC deadline, cancellation, retry, status, streaming, and Protobuf
  compatibility tests;
- batch partial-failure, amplification, and per-item authorization tests;
- SSE and WebSocket slow-consumer, reconnect, token-expiry, quota, and shutdown
  tests;
- webhook signature, replay, duplicate, redirect, timeout, and reconciliation
  tests.

## Current Sources

- [GraphQL Security](https://graphql.org/learn/security/)
- [Protocol Buffers Programming Guides](https://protobuf.dev/programming-guides/)
- [gRPC Guides](https://grpc.io/docs/guides/)
