# Structured Logging

Structured logging preserves event fields as typed data instead of embedding
them in prose. NDJSON is a common stream encoding: each physical line contains
one complete JSON object. It is useful for container logs and line-oriented
collectors, but it is not the only valid representation. OpenTelemetry Protocol
(OTLP), journald, and native platform APIs may carry the same structured event
without NDJSON.

## Runtime Output

For ordinary containerized services:

- write application logs to `stdout` or `stderr`;
- emit exactly one encoded event per physical line;
- escape embedded newlines and control characters through the JSON encoder;
- do not write or rotate application log files inside the container;
- let the container runtime, node agent, or platform own collection and
  rotation;
- define behavior when the output stream blocks or the collector falls behind.

File output is justified only when the runtime or legacy integration requires
it. In that case, define ownership, permissions, rotation, retention, disk
limits, crash recovery, and collection explicitly.

## Event Schema

Use a stable envelope that can map to the OpenTelemetry log data model:

```json
{"timestamp":"2026-08-30T10:00:00.000Z","severity_text":"INFO","service.name":"checkout","service.version":"2026.08.30","deployment.environment.name":"production","event.name":"order.accepted","body":"Order accepted","trace_id":"4bf92f3577b34da6a3ce929d0e0e4736","span_id":"00f067aa0ba902b7","request_id":"req_01","schema_version":1,"order.count":1}
```

This is an application serialization, not a claim that OpenTelemetry mandates
these exact JSON property names. Define and test the mapping to the selected
collector or backend.

Recommended concepts:

- **Timestamp:** when the event occurred, in UTC with unambiguous precision.
- **Observed timestamp:** when a collector observed the event, when relevant.
- **Severity text and number:** preserve source severity and map it
  consistently.
- **Resource:** service name, version, instance, environment, region, cell, and
  tenant boundary where safe and useful.
- **Event name:** stable identifier for the event class, without variable data.
- **Body:** concise human-readable message or structured body.
- **Attributes:** typed event-specific context.
- **Trace context:** trace ID, span ID, and trace flags when a valid current
  context exists.
- **Schema version:** explicit event-contract version when consumers depend on
  the shape.

Use a stable `event.name` for queries and automation. Human-readable messages
may change without becoming an API.

## Correlation

Use identifiers for different purposes deliberately:

- `trace_id` and `span_id` correlate execution through a distributed trace;
- `request_id` identifies an ingress request for support and protocol
  diagnostics;
- `correlation_id` groups a business operation that may outlive one trace;
- `causation_id` identifies the command or event that caused another event;
- idempotency keys prevent duplicate mutation and are not automatically safe
  log fields.

Propagate existing context across service boundaries. Do not generate a new
correlation identifier at every hop. Validate external identifiers for length
and format before logging, and do not let callers control trusted resource
fields such as service, environment, or tenant.

## Severity

Define severity by operational meaning:

- `DEBUG`: detailed diagnostics disabled or sampled in normal production use;
- `INFO`: expected lifecycle or business events useful for operations;
- `WARN`: degraded or risky condition that recovered or needs attention;
- `ERROR`: operation failed or produced an invalid result;
- `FATAL`: process cannot continue safely.

Do not log the same exception at every layer. The boundary that decides the
outcome should emit the principal failure event; lower layers should preserve
causal error context.

## Sensitive Data and Injection

Treat all log attributes as potential data egress.

- Never log credentials, tokens, authorization headers, session cookies,
  private keys, secret values, or raw payment data.
- Avoid raw request and response bodies. Extract the minimum classified fields
  needed for the operational question.
- Minimize personal data such as email addresses, IP addresses, user agents,
  account identifiers, and location. Apply documented purpose, access,
  retention, and deletion controls when collection is justified.
- Redact by schema and field classification before serialization. Do not rely
  only on regular expressions after ingestion.
- Reject or bound oversized fields, collections, stack traces, and arbitrary
  metadata.
- Use structured encoders so untrusted values cannot forge additional lines or
  fields.
- Scrub exception messages and stack traces because dependencies may include
  secrets or payload fragments.

Hashing an identifier does not automatically make it anonymous. Stable hashes
can remain linkable and vulnerable to enumeration.

## Errors

Represent errors with bounded structured fields:

```json
{"event.name":"payment.authorization.failed","severity_text":"ERROR","error.type":"ProviderTimeout","error.code":"PAYMENT_PROVIDER_TIMEOUT","error.retryable":true,"trace_id":"4bf92f3577b34da6a3ce929d0e0e4736","span_id":"00f067aa0ba902b7"}
```

Prefer stable error type and code fields over parsing messages. Include a stack
trace only where policy allows it, cap its size, and avoid duplicating it across
layers.

## Schema Evolution

- Add optional fields compatibly.
- Do not silently change a field's type or meaning.
- Version events when consumers cannot tolerate a compatible extension.
- Maintain producer and consumer contract tests for automated log processing.
- Define missing, null, redacted, and unknown semantics.
- Keep resource identity separate from event-varying attributes.

A shared logging package can enforce encoding, context injection, and
redaction, but it must not become a mandatory synchronous network dependency.
Keep the event contract language-neutral and let each runtime use an idiomatic
adapter.

## Volume, Sampling, and Retention

- Estimate events per request, bytes per event, peak throughput, daily ingest,
  indexed fields, and retained storage.
- Sample repetitive low-value diagnostics before export when policy permits.
- Preserve the signals needed to measure sampling and data loss.
- Do not probabilistically sample required audit records.
- Define separate retention by event class and environment.
- Remove debug logging after bounded diagnostic windows.

## Application Logs and Audit Events

Application logs optimize diagnosis and operations. Audit events prove
security, identity, administrative, financial, or data-access decisions.

Audit events commonly require:

- actor, action, target, authority, policy version, decision, result, and time;
- append-only or immutable storage;
- stricter access and longer retention;
- completeness monitoring and reconciliation;
- legal or regulatory ownership.

Do not claim that mutable application log storage satisfies an audit
requirement.

## Verification

Test:

1. one event produces one valid JSON line when NDJSON is selected;
2. strings containing newlines and control characters cannot forge events;
3. secret and sensitive-field fixtures are removed or rejected;
4. trace context appears only when valid context exists;
5. schema types remain stable across versions;
6. oversized events are bounded with visible counters;
7. collector interruption produces documented buffering or loss behavior;
8. retention and deletion policies work in the target backend.

## Current Sources

- [OpenTelemetry Logs Data Model](https://opentelemetry.io/docs/specs/otel/logs/data-model/)
- [OpenTelemetry Logging](https://opentelemetry.io/docs/specs/otel/logs/)
- [Kubernetes Logging Architecture](https://kubernetes.io/docs/concepts/cluster-administration/logging/)
