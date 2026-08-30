# Distributed Tracing and Telemetry Pipelines

Distributed tracing connects work across process and dependency boundaries.
Telemetry pipelines collect, transform, buffer, and export traces, metrics, and
logs. Both are production data paths with explicit reliability and security
limits.

## Trace Context

Use W3C Trace Context for interoperable HTTP propagation unless a protocol or
platform requires another standard. Instrumentation must:

- accept only valid bounded incoming context;
- continue the current trace across synchronous calls;
- propagate context through supported messaging metadata;
- create links when work relates to another trace but is not its direct child;
- start a new trace when no valid trusted context exists;
- prevent external baggage from overwriting trusted service or tenant
  attributes;
- avoid placing secrets or unnecessary personal data in baggage.

Trace and span identifiers are correlation values, not authentication or
authorization evidence. Never grant access because a caller supplied a valid
trace header.

## Span Design

Name spans with stable operations such as `POST /orders`, `orders.publish`, or
`payment.authorize`. Do not place IDs, raw URLs, query strings, or error messages
in span names.

Record:

- service resource identity and version;
- normalized operation or route;
- dependency system and bounded destination attributes;
- start, duration, and outcome;
- retry attempt only when needed and bounded;
- classified exception and status;
- links for batch, fan-in, fan-out, and asynchronous work.

Do not create a span for every small function. Instrument boundaries and logical
steps that explain latency, dependency behavior, concurrency, or failure.

Distinguish transport success from business outcome. A valid card decline,
authorization denial, or not-found result is not automatically a failed span.
Follow current semantic conventions for the protocol and domain.

## Sampling

Sampling is a cost and evidence policy.

- Head sampling decides before the complete trace is known and is cheap.
- Tail sampling can retain traces based on outcome, latency, or attributes but
  requires buffering and centralized decision capacity.
- Parent-based sampling preserves upstream decisions across services.
- Error-biased policies improve diagnostics but do not replace unsampled error
  metrics.

Define:

- target volume and budget;
- rules for errors, slow requests, rare operations, and critical journeys;
- per-tenant fairness and abuse limits;
- decision latency and memory for tail sampling;
- behavior when the sampler or collector is overloaded;
- metrics that estimate received, sampled, exported, and dropped telemetry.

Never claim complete forensic coverage from sampled traces.

## Instrumentation Boundary

Prefer stable vendor-neutral APIs and semantic conventions. Keep application
code independent from one telemetry backend:

- use idiomatic runtime instrumentation;
- centralize resource identity and exporter configuration;
- use OpenTelemetry Protocol where current ecosystem support is suitable;
- pin compatible SDK, instrumentation, collector, and semantic-convention
  versions;
- validate upgrades because semantic attributes and defaults can change.

Automatic instrumentation provides breadth, not proof of useful semantics.
Review span names, propagation, duplicate instrumentation, sensitive
attributes, and overhead in the actual application.

## Collector Topology

Common roles:

- **Agent or node collector:** receives local telemetry, adds trusted resource
  metadata, batches, and forwards.
- **Gateway collector:** centralizes sampling, routing, tenancy enforcement,
  transformation, and backend egress.
- **Backend:** indexes, stores, queries, alerts, and enforces retention.

Choose topology from latency, volume, tenancy, failure domains, network policy,
and operational ownership. A gateway is a shared dependency and needs capacity,
redundancy, overload behavior, and regional isolation.

## Bounded Pipeline

For every receiver, processor, queue, and exporter, define:

- accepted protocol and authenticated source;
- request and batch size;
- memory and disk budget;
- queue capacity and maximum age;
- timeout, retryable status, backoff, and maximum elapsed time;
- backpressure behavior;
- overflow and drop priority;
- shutdown and restart behavior;
- tenant and signal isolation;
- destination allowlist and encryption.

Place memory limiting early enough to prevent collector termination. Use
batching for transport efficiency without violating latency or payload limits.
Bound exporter queues and retries to the outage duration the system can absorb.

A memory queue loses data on process failure. A persistent queue can survive
some restarts but still loses data on disk failure, corruption, overflow, or
expiry. It is not equivalent to a durable business message queue.

## Failure and Overload

Telemetry must not take down the service it observes.

- Keep application export asynchronous and bounded.
- Apply backpressure only where callers and protocols can handle it safely.
- Prioritize required audit and critical operational signals separately from
  debug telemetry.
- Drop or sample lower-value data before exhausting service or collector
  resources.
- Expose loss through counters, alerts, and visible health state.
- Avoid infinite retries during a backend outage.
- Test recovery without synchronized export floods.

Security audit delivery may require a separate pipeline with stronger
durability and integrity. Do not silently route required audit events through a
best-effort sampled application pipeline.

## Pipeline Security

- Authenticate workloads and collectors with short-lived identities.
- Authorize signal, tenant, environment, and destination per request.
- Encrypt telemetry in transit and at rest.
- Prevent tenant-controlled attributes from selecting another tenant's stream
  or backend.
- Redact before external egress when possible.
- Restrict processor and exporter plugins because they execute inside the
  collector trust boundary.
- Allowlist destinations and block loopback, metadata, and arbitrary user
  endpoints.
- Keep production and non-production telemetry, credentials, and indexes
  isolated.

## Pipeline Observability

Monitor the monitoring system:

- accepted, refused, dropped, retried, and exported items by signal;
- queue size, age, capacity, and persistent-storage use;
- processor errors and transformation rejects;
- exporter latency, failures, and throttling;
- collector CPU, memory, restarts, and saturation;
- end-to-end telemetry delay and freshness;
- active series, span volume, log bytes, and cost;
- configuration version and rollout state.

Alerts should distinguish application silence from pipeline failure. A flat
error graph is not healthy if no telemetry arrived.

## Verification

Exercise:

1. valid and invalid inbound trace context;
2. synchronous, asynchronous, fan-out, and retry propagation;
3. sampler behavior for errors, latency, rare paths, and overload;
4. backend outage longer than the retry window;
5. queue overflow, disk exhaustion, restart, and abrupt shutdown;
6. tenant isolation and attribute-spoofing attempts;
7. secret and sensitive-data redaction before egress;
8. collector rollout, rollback, and mixed-version compatibility;
9. recovery without memory spikes or export storms.

## Current Sources

- [OpenTelemetry Signals](https://opentelemetry.io/docs/concepts/signals/)
- [OpenTelemetry Baggage](https://opentelemetry.io/docs/concepts/signals/baggage/)
- [OpenTelemetry Collector Resiliency](https://opentelemetry.io/docs/collector/resiliency/)
- [OpenTelemetry Agent-to-Gateway Deployment](https://opentelemetry.io/docs/collector/deploy/other/agent-to-gateway/)
- [W3C Trace Context](https://www.w3.org/TR/trace-context/)
