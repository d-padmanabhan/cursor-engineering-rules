# API Evolution and OpenAPI

An API contract includes syntax, semantics, authorization, ordering, timing
expectations, errors, and lifecycle. Compatibility is not determined only by
whether a JSON parser still accepts the payload.

## OpenAPI Version Selection

Use the newest stable OpenAPI version supported by the repository's validated
toolchain. Verify compatibility across:

- schema validators;
- code generators;
- API gateways and policy engines;
- documentation renderers;
- contract-diff tools;
- mocks and test harnesses;
- client language targets.

OpenAPI 3.2.0 is the current published specification as of this reference, but
that does not make it safe to select mechanically. Record a tooling constraint
when an older supported version is necessary and define the upgrade trigger.

## Contract Completeness

Define:

- stable operation IDs;
- server environments and base paths;
- authentication schemes and operation security;
- path, query, header, cookie, and body schemas;
- media types and request size constraints;
- success, asynchronous, error, and rate-limit responses;
- RFC 9457 problem schemas;
- response headers such as `Location`, `ETag`, and `Retry-After`;
- bounded pagination, filtering, and sorting;
- examples that contain only synthetic data;
- webhook and callback contracts where used;
- ownership, support, and deprecation metadata.

Do not treat generated documentation as proof that the contract is complete.

## Compatibility Classification

Potentially breaking changes include:

- removing or renaming an operation, field, header, enum, or problem type;
- changing a method, path, status, media type, field type, format, unit, or
  meaning;
- making optional input required;
- changing defaults, validation bounds, nullability, or unknown-field behavior;
- adding a required response field for strict clients;
- adding an enum value when clients assume exhaustive matching;
- changing authorization, visibility, rate limits, caching, ordering,
  pagination, idempotency, or retry behavior;
- changing timestamps, money, precision, or identifier representation;
- making a formerly synchronous result asynchronous;
- narrowing a support or deprecation window.

An additive field is usually compatible only when consumers tolerate unknown
fields. A new enum value is additive syntax but can break exhaustive consumers.

## Change Workflow

1. Identify affected consumers and support commitments.
2. Diff the machine-readable contract and review semantic behavior.
3. Run provider conformance and consumer contract tests.
4. Test generated clients in supported languages.
5. Provide an overlap period when clients cannot migrate atomically.
6. Publish a migration guide with examples and rollback behavior.
7. Observe adoption before enforcing or removing old behavior.
8. Remove only after the documented support and deprecation conditions are met.

Avoid creating a new major version for every additive change. Do not use a new
version to hide an undocumented behavioral break.

## Version Placement

Path, media-type, header, and date-based versioning can all work. Choose one
based on routing, caching, client ergonomics, gateway support, and support
policy. Apply it consistently.

Query-parameter versioning can be difficult for caches and routing policies and
should not be presented as an equivalent default without explicit handling.

Version the public contract, not every implementation deployment. Keep internal
build or release identifiers separate from the API version.

## Deprecation and Sunset

Deprecation means use is discouraged. Sunset means availability is expected to
end. They are related but not interchangeable.

When using HTTP lifecycle fields:

- follow RFC 9745 for `Deprecation`;
- follow RFC 8594 for `Sunset`;
- ensure the sunset date does not precede deprecation;
- link to migration documentation;
- state affected operations and versions;
- name an owner and support channel;
- define minimum notice and exception policy;
- monitor remaining use without exposing consumer secrets.

Do not commit a stale fixed sunset date in a reusable template. Use a
clearly marked future placeholder that implementers must replace and validate.

## Contract-First and Code-First

Either workflow can succeed if one artifact is authoritative and drift is
blocked.

For contract-first:

- lint and review the specification;
- generate clients or stubs where useful;
- test implementation conformance.

For code-first:

- generate the specification deterministically;
- review the generated diff;
- fail CI when committed output is stale;
- prevent framework internals from becoming the public contract accidentally.

Never edit generated clients manually without a documented regeneration model.
Pin generator versions and review generated-code supply-chain risk.

## Compatibility Verification

Run:

- OpenAPI schema validation;
- style and organization lint;
- breaking-change detection against the supported baseline;
- provider request and response conformance;
- consumer contract tests;
- generated-client compilation and focused behavior tests;
- documentation example execution;
- authorization and negative schema tests;
- deprecation-header and migration-link checks.

Breaking-change tools detect syntax, not every semantic break. Human review must
cover authorization, defaults, ordering, pagination, error behavior, latency,
and operational limits.

## Current Sources

- [OpenAPI Specification](https://spec.openapis.org/oas/latest.html)
- [RFC 9745: The Deprecation HTTP Response Header Field](https://www.rfc-editor.org/rfc/rfc9745)
- [RFC 8594: The Sunset HTTP Header Field](https://www.rfc-editor.org/rfc/rfc8594)
