---
name: api-design
description: Designs and reviews production APIs across REST/HTTP, OpenAPI, GraphQL, gRPC, webhooks, asynchronous operations, batch endpoints, SSE, and WebSockets. Use when defining resources, routes, methods, status codes, problem details, pagination, idempotency, conditional writes, API schemas, compatibility, deprecation, authentication, authorization, rate limits, or protocol contracts.
---

# API Design

Mandatory API gates are owned by the API rule
(`${HANDBOOK_ROOT}/rules/320-api-design.mdc`). This skill owns design workflow,
trade-offs, examples, and protocol-specific guidance.

## Non-Negotiables

- Design from consumers, business invariants, trust boundaries, and failure
  behavior before choosing endpoint shapes.
- Let resource identifiers name nouns and protocol operations express behavior.
  Model a business action as a subordinate resource when that produces a clear
  lifecycle.
- Follow HTTP safety, idempotency, cache, conditional-request, and status-code
  semantics. Idempotence means the intended server effect is stable, not that
  every response is byte-identical.
- Authenticate the principal and authorize every protected object, tenant,
  relationship, field, and action on the server.
- Validate and bound every path, query, header, cookie, message, and body input.
  Serialize responses from allowlisted schemas rather than persistence objects.
- Use RFC 9457 Problem Details for new public HTTP error contracts unless an
  existing compatibility commitment requires another documented shape.
- Make retryable mutations safe with a stable operation identity, atomic state,
  and reconciliation. Never imply that transport delivery proves exactly-once
  business processing.
- Protect mutable resources from lost updates when concurrency matters.
- Treat the API description as a versioned contract. Detect breaking changes,
  provide migration evidence, and deprecate deliberately.
- Bound payloads, pagination, batches, queries, streams, execution time,
  concurrency, retries, queues, and per-principal cost.
- Keep secrets, credentials, raw payloads, and unnecessary personal data out of
  errors and telemetry.

## Design Workflow

### 1. Define Consumers and Guarantees

Document:

- consumers, trust levels, environments, and ownership;
- critical operations and business invariants;
- latency, availability, durability, freshness, and consistency needs;
- authentication mechanism and authorization policy inputs;
- expected load, object size, request size, page size, concurrency, and growth;
- retry, duplicate, ordering, and partial-failure behavior;
- compatibility window, support policy, and deprecation owner.

Do not start by listing endpoints.

### 2. Select the Interface Style

Choose the smallest interface that fits:

- REST/HTTP for resource-oriented public or broadly interoperable APIs;
- GraphQL for consumer-selected graphs when demand control and field
  authorization are enforceable;
- gRPC for typed service-to-service contracts, streaming, and generated clients
  where HTTP/2 and Protobuf are operationally supported;
- webhook delivery for provider-initiated notifications;
- SSE for server-to-client event streams over HTTP;
- WebSockets for bounded bidirectional sessions;
- asynchronous operation resources for long-running work;
- batch endpoints only when network savings justify their authorization,
  isolation, and partial-result complexity.

Use the networking transport skill
(`${HANDBOOK_ROOT}/skills/networking-transport/SKILL.md`) for transport and wire
format selection.

### 3. Model Resources and Operations

For REST/HTTP:

- use stable, lowercase collection nouns and one multiword convention;
- use opaque identifiers and avoid exposing storage topology;
- nest only for true containment or scope;
- use query parameters for filtering, sorting, pagination, field selection, and
  other optional refinement;
- never place state-changing behavior behind GET, HEAD, or a query action such
  as `?action=delete`;
- use an explicit command endpoint only when no honest resource lifecycle fits,
  then document its authorization, idempotency, result, and failure semantics.

Examples of resource-modeled actions include an order cancellation resource,
an export job, or a password-reset request.

### 4. Define the Contract

Specify:

- method or operation semantics;
- request media type, schema, requiredness, defaults, unknown-field policy, and
  size limit;
- success status, headers, body schema, and empty-body behavior;
- RFC 9457 problem types, safe details, field pointers, and retryability;
- JSON naming, timestamp, identifier, decimal, money, unit, enum, null, and
  absent-value conventions;
- filtering operators, sort grammar, deterministic tie-break order, duplicate
  parameter behavior, and maximum page size;
- cache scope, validators, conditional reads, and conditional writes;
- asynchronous status, polling, cancellation, result, failure, expiry, and
  retention behavior.

Use the REST and HTTP contracts reference
(`${HANDBOOK_ROOT}/skills/api-design/references/rest-http-contracts.md`).

### 5. Design Security and Failure Behavior

Define authentication separately from authorization. Apply bounded schemas
before policy or business logic, and apply output filtering after authorization.

For mutations and remote dependencies, define:

- idempotency key ownership, request fingerprint, atomic persistence, replayed
  response, conflict behavior, and retention;
- optimistic concurrency and stale-write response;
- one end-to-end deadline, attempt timeouts, retry owner, transient failure
  classes, backoff, jitter, and retry budget;
- rate-limit principal, quota unit, window, response headers, and overload
  behavior;
- outbound destination and redirect policy;
- webhook signature, timestamp, replay, durable handoff, and redelivery policy;
- redacted audit, logs, metrics, and traces.

Use the security and resilience reference
(`${HANDBOOK_ROOT}/skills/api-design/references/security-resilience.md`), the
service resilience skill
(`${HANDBOOK_ROOT}/skills/service-resilience/SKILL.md`), and the distributed
transactions skill
(`${HANDBOOK_ROOT}/skills/distributed-transactions/SKILL.md`).

### 6. Define Evolution

Choose the newest OpenAPI version supported by the repository's validated
toolchain. Do not copy a version number from a handbook example without
checking generator, validator, gateway, and documentation compatibility.

Classify changes across request schemas, response schemas, requiredness,
defaults, enums, error types, status codes, ordering, pagination, authorization,
and observable behavior. Additive syntax can still be behaviorally breaking.

Use the evolution and OpenAPI reference
(`${HANDBOOK_ROOT}/skills/api-design/references/evolution-openapi.md`).

### 7. Apply Protocol-Specific Controls

GraphQL, gRPC, webhooks, SSE, WebSockets, and batch APIs retain the same
identity, authorization, validation, resource, compatibility, and observability
requirements. Add protocol-specific demand, flow-control, deadline, schema, and
connection-lifecycle controls.

Use the GraphQL, gRPC, and streaming reference
(`${HANDBOOK_ROOT}/skills/api-design/references/graphql-grpc-streaming.md`).

### 8. Verify the Contract

Run applicable:

- schema lint and validation;
- request and response conformance tests;
- authorization tests for object, tenant, relationship, action, and field
  boundaries;
- negative tests for unknown, malformed, oversized, duplicate, stale, replayed,
  and out-of-order inputs;
- OpenAPI or Protobuf breaking-change checks;
- consumer contract and generated-client tests;
- retry, timeout, idempotency, concurrency, and partial-failure tests;
- load, abuse, rate-limit, streaming, and backpressure tests;
- documentation examples against the production contract.

## Review Output

For a design or review, report:

1. consumers, invariants, and trust boundaries;
2. interface style and resource or operation model;
3. request, response, error, pagination, and async contracts;
4. authentication, authorization, validation, and abuse controls;
5. idempotency, concurrency, retry, and partial-failure behavior;
6. compatibility, versioning, and deprecation plan;
7. verification, observability, and unresolved risks.
