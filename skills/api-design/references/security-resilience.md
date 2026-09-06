# API Security and Resilience

API correctness includes adversarial inputs, partial failure, retries, overload,
and authorization changes. A valid schema or authenticated request is not
sufficient.

## Authorization

Authentication identifies a principal. Authorization decides whether that
principal may perform one action on one resource in the current context.

Enforce authorization for:

- object identifiers;
- tenant and organization boundaries;
- parent-child relationships;
- collection filters and search scope;
- actions and state transitions;
- sensitive fields in input and output;
- GraphQL fields and subscriptions;
- batch items and asynchronous status resources;
- webhook endpoint ownership and secret rotation.

Never accept `owner_id`, `tenant_id`, role, price, approval state, or similar
authority-bearing fields from a client without independent policy validation.
Do not rely on a gateway or user interface as the only authorization layer.

Use indistinguishable failures when revealing resource existence creates a
security or privacy risk.

## Boundary Validation

Parse path, query, header, cookie, body, message, and upload data into bounded
schemas. Define behavior for unknown and duplicate fields. Normalize only after
parsing and before policy checks.

Bound:

- request and decompressed body size;
- string, collection, nesting, and numeric ranges;
- file count, type, size, and archive extraction;
- query parameter count and expression complexity;
- batch item count and concurrency;
- GraphQL document depth, breadth, aliases, operation count, and field cost;
- stream frame, message, connection, and subscription counts;
- response and dependency body size.

Serialize responses through allowlisted output schemas. Input validation does
not replace SQL parameterization, context-specific output encoding, safe URL
handling, or authorization.

## Tokens and API Keys

Validate JWTs with fixed trusted:

- issuer;
- audience;
- allowed algorithms;
- signature key source and rotation;
- token type where profiles define one;
- expiry and not-before policy;
- subject and required authorization claims.

Do not select algorithms or key locations from untrusted token data. Follow the
JWT Best Current Practice and the protocol profile in use.

API keys require high entropy, one-time display, server-side hashing, a
non-secret identifier or prefix, scopes, ownership, expiry, rotation,
revocation, rate attribution, and audited use. Never transport keys in query
parameters or log them.

## Idempotency

`Idempotency-Key` is a widely used convention, not a finalized IETF standard.
For a retryable non-idempotent mutation:

1. Require the client to reuse one stable key for the same logical operation.
2. Scope the key to the authenticated principal and operation.
3. Bind it to a canonical request fingerprint.
4. Atomically create an in-progress record with the business transaction or
   durable command intent.
5. Return a conflict for the same key with a different fingerprint.
6. Serialize concurrent attempts or return a documented in-progress response.
7. Persist and replay the original status, selected headers, and body.
8. Define retention, expiry, retry-after-expiry, and reconciliation.

Never silently generate a replacement key for a retry. A cache-only
check-then-write is not atomic with the business effect.

## Deadlines and Retries

Set one end-to-end deadline. Allocate smaller attempt timeouts within it. Retry
only classified transient failures when the operation is idempotent or
protected by a stable idempotency contract.

Bound attempts, total elapsed time, concurrency, and retry amplification. Honor
safe `Retry-After` guidance. Use exponential backoff with jitter where retries
are appropriate. Propagate cancellation. Do not retry authentication,
authorization, validation, not-found, or conflict responses without a specific
contract.

Route deeper dependency policy to the service resilience skill
(`${HANDBOOK_ROOT}/skills/service-resilience/SKILL.md`).

## Rate Limits and Overload

Define:

- principal or resource being limited;
- operation cost;
- window or token-bucket semantics;
- burst capacity;
- tenant fairness and priority;
- response status and `Retry-After`;
- supported rate-limit fields when clients consume them;
- behavior when the limiter or identity dependency fails.

Rate limiting complements authorization and capacity controls. It is not an
authorization mechanism.

## Outbound URLs and SSRF

When users can influence a destination:

- allowlist schemes, ports, and destinations;
- reject embedded credentials;
- resolve and reject loopback, private, link-local, multicast, and metadata
  addresses;
- revalidate every redirect and resolved address;
- protect against DNS rebinding;
- bound connect, read, total time, redirects, and response size;
- enforce egress policy independently of application validation.

Do not expose a generic fetch-arbitrary-URL capability.

## Webhooks

For inbound webhooks:

- verify the signature over the exact raw bytes;
- use a versioned signing contract and constant-time comparison;
- enforce a bounded timestamp tolerance;
- reject replay through a durable event or delivery identifier;
- validate event type, schema version, and size;
- persist a durable handoff before acknowledging when processing cannot finish
  synchronously;
- make processing idempotent;
- define acknowledgement, retry, ordering, dead-letter, and reconciliation
  behavior;
- rotate signing secrets without an ambiguous cutover.

For outbound webhook registration, apply the SSRF contract. Sign deliveries,
use stable delivery IDs and timestamps, define retry and disablement behavior,
and expose delivery observability without leaking payloads or secrets.

## CORS

CORS is a browser response-sharing policy, not authorization. Use exact,
environment-specific origins. Credentialed browser APIs must not combine
credentials with a wildcard origin. Allow only required methods and headers,
including actual mutation and idempotency headers. Bound preflight caching and
test allowed and denied origins.

## Telemetry and Audit

Emit bounded, redacted:

- server-generated request or correlation ID;
- trace context;
- route template, not raw path;
- method or operation, status, outcome, and latency;
- dependency outcome and retry count;
- rate-limit and overload decisions;
- authorization decision audit events where required.

Validate caller-provided correlation values before use. Never log authorization
headers, cookies, keys, raw bodies, query values, personal data, raw exception
messages, or stacks without explicit classification and controls.

Use the observability skill
(`${HANDBOOK_ROOT}/skills/observability/SKILL.md`) for schemas, cardinality,
retention, and telemetry pipelines.

## Security Verification

Test:

- unauthenticated and expired credentials;
- wrong issuer, audience, algorithm, scope, tenant, owner, relationship, and
  field access;
- identifier substitution and collection filter bypass;
- mass assignment and over-broad output;
- malformed, unknown, duplicate, oversized, deeply nested, and compressed
  payloads;
- duplicate mutations, concurrent idempotency attempts, and fingerprint
  mismatch;
- stale write preconditions;
- SSRF through redirects, alternate address forms, and DNS changes;
- webhook signature, timestamp, replay, key rotation, and duplicate delivery;
- rate-limit evasion, batch amplification, GraphQL aliases, and stream quotas;
- redaction and safe error behavior.

## Current Sources

- [OWASP API Security Top 10](https://owasp.org/API-Security/)
- [RFC 8725: JSON Web Token Best Current Practices](https://www.rfc-editor.org/rfc/rfc8725)
- [RFC 9110: HTTP Semantics](https://www.rfc-editor.org/rfc/rfc9110)
