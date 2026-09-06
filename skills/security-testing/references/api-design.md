# API Security Testing

Use the API design skill
(`${HANDBOOK_ROOT}/skills/api-design/SKILL.md`) for interface semantics and
contracts. This reference owns focused negative security testing.

## Test from the Trust Boundary

Build tests from the API's principals, resources, relationships, fields,
actions, and state transitions. Cover both allow and deny decisions.

For every protected operation, vary:

- unauthenticated, malformed, expired, revoked, and wrong-audience credentials;
- principal, role, scope, tenant, organization, and ownership;
- resource IDs, parent IDs, related IDs, and collection filters;
- writable and readable fields;
- operation state and concurrency version;
- direct endpoint, batch, GraphQL, gRPC, stream, and asynchronous-status access.

Do not accept a successful list filter as proof that member endpoints enforce
the same scope.

## BOLA, BFLA, and Mass Assignment

Test horizontal and vertical identifier substitution. Attempt access to another
tenant's child through an authorized parent and an authorized child through
another parent. Test guessed, stale, deleted, and malformed identifiers.

Add authority-bearing input fields such as:

- `tenant_id`;
- `owner_id`;
- `role`;
- `is_admin`;
- `price`;
- `approved`;
- internal lifecycle state.

Verify that unknown or forbidden fields are rejected or ignored according to
the documented schema and cannot affect stored or returned state.

Test field-level output filtering for personal, financial, credential, and
administrative attributes.

## Parser and Size Abuse

Test:

- unsupported and conflicting media types;
- duplicate JSON keys and query parameters;
- unknown fields;
- null versus absent values;
- extreme numbers, strings, arrays, maps, and nesting;
- malformed Unicode and control characters;
- compressed-body expansion;
- file and archive traversal;
- batch amplification;
- GraphQL aliases, fragments, breadth, depth, and field cost;
- gRPC message and stream limits;
- WebSocket frame and message limits.

Confirm that parsing fails before business or policy side effects.

## Mutation, Retry, and Concurrency

For idempotent and idempotency-protected operations, inject:

- lost responses;
- concurrent duplicate requests;
- same key with a different payload;
- crash before and after local commit;
- dependency timeout followed by late success;
- retry after key expiry;
- stale `If-Match`;
- compensation and reconciliation failure.

Verify one intended business effect, the documented replayed result, safe
conflict behavior, and visible reconciliation.

## SSRF and Webhooks

For user-influenced destinations, test alternate IP representations, DNS
changes, redirects, embedded credentials, disallowed ports, private and
link-local addresses, metadata endpoints, oversized responses, and timeout
behavior.

For inbound webhooks, test modified raw bytes, wrong key, old and future
timestamps, duplicate delivery IDs, schema-version mismatch, key rotation,
acknowledgement crash windows, and repeated processing.

## Error and Telemetry Exposure

Trigger parser, authentication, authorization, policy, database, dependency,
timeout, and internal failures. Verify that responses and telemetry do not
expose:

- credentials, tokens, cookies, keys, or connection strings;
- stack traces, SQL, internal paths, or dependency payloads;
- account or resource existence when policy requires concealment;
- raw request or response bodies;
- unnecessary personal or tenant data.

Validate correlation identifiers for format and length. Ensure route templates,
not raw attacker-controlled paths, are used for metric dimensions.

## Rate and Cost Controls

Test limits by principal, tenant, IP where relevant, resource, operation, and
cost. Attempt evasion through concurrency, batching, aliases, multiple
connections, retries, pagination, and alternate credentials.

Verify bounded failure behavior when the limiter or identity dependency is
unavailable. Rate limiting must not become the only authorization control.

## Evidence

Record:

- tested principal and resource relationship;
- request shape with secrets removed;
- expected and actual status or protocol result;
- authorization or policy decision identifier;
- resulting durable state;
- duplicate or side-effect count;
- relevant redacted telemetry;
- exact build and contract version.

Use synthetic accounts and resources. Never run destructive security tests
against production without explicit authorization and an isolated test plan.
