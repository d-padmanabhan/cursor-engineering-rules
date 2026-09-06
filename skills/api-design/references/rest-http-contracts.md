# REST and HTTP Contracts

Use RFC 9110 semantics rather than framework folklore. Consistency matters, but
consistent misuse of HTTP remains incorrect.

## Resources and Paths

Prefer collection and member resources:

```text
GET    /orders
POST   /orders
GET    /orders/{order_id}
PUT    /orders/{order_id}
PATCH  /orders/{order_id}
DELETE /orders/{order_id}
```

Model actions as resources when they have identity, state, or a result:

```text
POST /orders/{order_id}/cancellations
POST /exports
GET  /operations/{operation_id}
```

Do not use safe methods for mutations:

```text
GET /orders/{order_id}?action=cancel
```

An explicit command endpoint can be honest when no useful resource model exists.
Document its effect, authorization, idempotency, status, and result contract.

Use lowercase plural collection segments and one delimiter for multiword names.
Keep identifiers opaque. Avoid leaking table names, region topology, shard
placement, implementation class names, or internal service names.

Nest only where the parent identifies true containment or authorization scope.
Deep nesting creates duplicated routes and ambiguous ownership.

## Method Semantics

- `GET` and `HEAD` are safe and idempotent. They must not trigger a
  client-visible mutation.
- `PUT` replaces the selected resource representation and is idempotent.
- `PATCH` applies a defined patch document. Publish the supported media type,
  path semantics, validation, atomicity, and idempotency behavior.
- `DELETE` is idempotent in intended effect; repeated responses can differ.
- `POST` creates, submits, or processes according to the target resource's
  documented semantics. Protect retries when duplicate effects matter.
- `OPTIONS` reports communication options where the deployment supports it.

Do not call an operation idempotent merely because duplicates are unlikely.

## Status and Header Contract

Choose status by outcome, not method alone:

- `200 OK`: successful response with a representation;
- `201 Created`: a resource was created; include `Location` when its URI is
  available;
- `202 Accepted`: work was durably accepted but is incomplete;
- `204 No Content`: success with no response content;
- `304 Not Modified`: a conditional read validator matched;
- `400 Bad Request`: malformed request syntax or generic request failure;
- `401 Unauthorized`: authentication is missing or invalid, with an appropriate
  challenge when applicable;
- `403 Forbidden`: the authenticated principal is not authorized;
- `404 Not Found`: resource absent, or intentionally concealed when policy
  requires indistinguishability;
- `405 Method Not Allowed`: method unsupported for the resource; include
  `Allow`;
- `406 Not Acceptable`: no acceptable response representation;
- `409 Conflict`: request conflicts with current resource or operation state;
- `412 Precondition Failed`: a supplied validator such as `If-Match` is stale;
- `415 Unsupported Media Type`: request content type is unsupported;
- `422 Unprocessable Content`: syntax is understood but content fails defined
  semantic validation;
- `428 Precondition Required`: the server requires a conditional request;
- `429 Too Many Requests`: quota exceeded; include an actionable
  `Retry-After` when known;
- `503 Service Unavailable`: temporary overload or unavailability;
- `504 Gateway Timeout`: a gateway did not receive a timely upstream response.

POST can legitimately produce `200`, `201`, `202`, or `204`. DELETE can produce
`200`, `202`, or `204`. Document each operation rather than using one status
table mechanically.

## Problem Details

For new public HTTP APIs, use RFC 9457
`application/problem+json`:

```json
{
  "type": "https://api.acme.com/problems/validation-failed",
  "title": "Request validation failed",
  "status": 422,
  "detail": "One or more fields are invalid.",
  "instance": "/problems/01JEXAMPLE",
  "code": "VALIDATION_FAILED",
  "request_id": "req_01JEXAMPLE",
  "errors": [
    {
      "pointer": "/email",
      "code": "INVALID_FORMAT"
    }
  ]
}
```

Keep `type` stable. Treat `title` as the summary for the problem type, `status`
as advisory when carried in the body, and `detail` as occurrence-specific but
safe text. Use JSON Pointer for field locations. Never expose stack traces, SQL,
policy internals, credentials, raw dependency errors, or account-existence
details.

An established non-RFC error envelope can remain for compatibility, but define
one contract and map it consistently.

## Query Parameters

Use query parameters to refine a collection. Define:

- allowed filter fields and operators;
- encoding for repeated values;
- unknown and duplicate parameter behavior;
- null, empty, omitted, and default semantics;
- sort fields, direction syntax, and deterministic tie-break ordering;
- maximum query length, filter count, and page size;
- field-selection authorization and response-cache implications.

Never concatenate filter or sort input into SQL, shell, path, or expression
languages. Map allowlisted API fields to parameterized backend operations.

## Pagination

Offset pagination is simple but can duplicate or omit records while the dataset
changes. Use it for bounded, stable, or administrative datasets where that
behavior is acceptable.

Cursor pagination requires:

- a deterministic total ordering with an immutable tie-breaker;
- an opaque, bounded cursor;
- binding to relevant principal, tenant, filter, sort, and page-size context;
- tamper detection when clients must not alter cursor state;
- expiry and invalid-cursor behavior;
- a maximum page size;
- explicit behavior for inserts, deletes, and updates between requests.

Do not promise snapshot consistency unless the storage and cursor contract
actually provide it. Totals can be expensive and can disclose population size;
make them an intentional contract.

## Representations

Standardize:

- JSON property casing;
- RFC 3339 timestamps with an offset or `Z`;
- calendar dates separately from timestamps;
- IDs as opaque strings at the API boundary;
- decimal, money, currency, and measurement units;
- enum extensibility and unknown-value behavior;
- absent versus explicit `null`;
- create, update, patch, and read representations;
- collection envelopes and pagination links;
- content negotiation and character encoding.

Do not serialize persistence records directly. Output schemas prevent accidental
field disclosure and decouple storage changes from API contracts.

## Conditional Requests and Caching

Use validators for read efficiency and optimistic concurrency:

- `ETag` plus `If-None-Match` for conditional reads;
- a strong `ETag` plus `If-Match` for writes where lost updates matter;
- `412 Precondition Failed` for a stale supplied validator;
- `428 Precondition Required` when the server requires a precondition.

Define canonical validator generation and whether weak validators are permitted.

Cache only representations safe for their cache scope. Authenticated,
tenant-specific, or personal-data responses normally require `private`,
`no-cache`, or `no-store` according to the actual reuse policy. Never mark a
response `public` merely for performance. Set `Vary` deliberately when
representation selection depends on request headers.

## Asynchronous Operations

For long-running work, `202 Accepted` means accepted, not completed. Return a
status resource:

```http
HTTP/1.1 202 Accepted
Location: /operations/op_01JEXAMPLE
Retry-After: 5
```

Define:

- durable acceptance point;
- operation states and allowed transitions;
- status-resource authorization;
- progress semantics;
- polling interval and backoff;
- cancellation and race behavior;
- terminal result or RFC 9457 problem;
- expiry, retention, and idempotent resubmission;
- webhook or stream notification as an optional optimization, not the only
  recovery path.

## Current Sources

- [RFC 9110: HTTP Semantics](https://www.rfc-editor.org/rfc/rfc9110)
- [RFC 9457: Problem Details for HTTP APIs](https://www.rfc-editor.org/rfc/rfc9457)
- [RFC 3339: Date and Time on the Internet](https://www.rfc-editor.org/rfc/rfc3339)
