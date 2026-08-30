---
name: observability
description: Designs and reviews production observability using structured logging, NDJSON, metrics, SLIs and SLOs, distributed tracing, OpenTelemetry, dashboards, alerts, telemetry pipelines, redaction, retention, and cost controls. Use when instrumenting services, defining log schemas, correlating microservices, designing monitoring or alerting, reviewing telemetry cardinality, or diagnosing whether production signals can answer operational questions.
---

# Observability

Design observability from operational questions and user-visible outcomes. Do
not add logs, metrics, or spans merely to satisfy a three-pillars checklist.
Each signal must support a diagnostic, reliability, security, or business
decision at an acceptable cost.

## Observability Contract

- Start with critical journeys, SLIs, SLOs, failure modes, and the questions an
  operator must answer during an incident.
- Use metrics for bounded aggregate behavior, traces for request and dependency
  paths, and logs for discrete events requiring detailed context.
- Emit structured logs. For container streams, prefer one JSON object per
  physical line on `stdout` or `stderr`; let the platform collect and rotate
  logs.
- Propagate W3C trace context across process boundaries and correlate logs with
  valid trace and span identifiers when context exists.
- Keep metric labels and span names bounded. Never use user IDs, request IDs,
  email addresses, raw URLs, or other unbounded values as metric labels.
- Treat telemetry as sensitive data. Minimize, classify, redact, retain, and
  authorize it deliberately.
- Keep security audit events separate from ordinary application logs when
  integrity, access, or retention requirements differ.
- Bound telemetry queues, retries, memory, disk, network, and cost. Define which
  data may be sampled or dropped under pressure.
- Alert on actionable user impact or imminent budget exhaustion. Every page
  needs an owner, urgency, evidence, and runbook.
- Instrument the telemetry pipeline itself so loss, refusal, delay, and cost are
  visible.

## Workflow

### 1. Define Questions and Reliability Targets

State:

- critical user journeys and owners;
- availability, latency, correctness, freshness, and durability SLIs;
- SLO windows and error budgets;
- known failure and overload modes;
- forensic or regulatory requirements;
- incident questions the current system cannot answer.

Do not begin with a vendor, agent, collector, dashboard, or list of fields.

### 2. Select the Smallest Useful Signals

Choose signals by purpose:

- **Metrics:** rates, ratios, distributions, saturation, queue age, and resource
  budgets that need efficient aggregation and alerting.
- **Traces:** end-to-end latency, dependency paths, retries, fan-out, and
  request-scoped failure analysis.
- **Logs:** state transitions, classified failures, policy decisions, recovery
  actions, and bounded diagnostic details.
- **Profiles:** code-level resource attribution when sampling overhead and
  runtime support are acceptable.

One event may contribute to several signals, but avoid recording the same large
payload in each.

### 3. Define Signal Contracts

For logs, define:

- event name and schema version;
- event and observed timestamps;
- severity semantics;
- service resource identity and deployment environment;
- trace, span, request, correlation, and causation identifiers where relevant;
- allowed attributes, sensitivity classification, size limit, and retention;
- exception shape and redaction behavior.

For metrics, define:

- user-visible or resource outcome;
- type, unit, monotonicity, and aggregation;
- bounded label set and estimated worst-case series count;
- collection interval and retention;
- SLI numerator, denominator, exclusions, and missing-data behavior.

For traces, define:

- propagation format and trust boundary;
- stable low-cardinality span names;
- semantic attributes and error status;
- head or tail sampling policy;
- baggage allowlist, size, and sensitivity policy;
- maximum attributes, events, links, and payload sizes.

Use the structured logging reference
(`${HANDBOOK_ROOT}/skills/observability/references/structured-logging.md`), the
metrics and alerting reference
(`${HANDBOOK_ROOT}/skills/observability/references/metrics-slos-alerting.md`),
and the tracing and pipeline reference
(`${HANDBOOK_ROOT}/skills/observability/references/tracing-telemetry-pipelines.md`)
for detailed contracts.

### 4. Design Collection and Export

Prefer vendor-neutral instrumentation and OpenTelemetry Protocol (OTLP) at
service boundaries where ecosystem support is mature. Keep instrumentation
libraries separate from exporter and backend selection.

Define:

- process, node, sidecar, agent, and gateway responsibilities;
- batching, queue, retry, timeout, and backpressure limits;
- behavior during backend outage or collector saturation;
- egress allowlists, authentication, encryption, and tenant isolation;
- schema transformation and enrichment ownership;
- data residency, retention, deletion, and archive policy;
- cost budgets by signal, tenant, service, and environment.

A persistent collector queue reduces some losses but is not a no-loss
guarantee. Document overflow, expiry, disk failure, and shutdown behavior.

### 5. Build Dashboards and Alerts

Start service dashboards with:

- SLI attainment and error-budget consumption;
- request or job rate, errors, and latency distribution;
- saturation, queue age, rejected work, and dependency health;
- deployment, configuration, and feature-flag changes;
- telemetry pipeline health and data freshness.

Use multi-window burn-rate alerts where an SLO supports them. Page only for
urgent, actionable conditions. Route slower budget consumption and maintenance
risks to tickets or planned work.

### 6. Verify End to End

Test:

- schema validity and single-line encoding;
- redaction against representative secrets and sensitive fields;
- trace propagation through asynchronous and synchronous boundaries;
- metric cardinality under worst-case inputs;
- SLI calculations, alert firing, inhibition, routing, and recovery;
- collector backpressure, queue overflow, restart, and backend outage;
- telemetry delay, duplication, sampling, and loss;
- dashboard and runbook usability during a controlled failure.

Verify from generated telemetry in the target backend, not only from unit tests
or local console output.

## Required Review Output

For an observability design or review, provide:

1. operational questions, critical journeys, and SLOs;
2. signal contracts and correlation strategy;
3. sensitivity, redaction, retention, and access policy;
4. metric cardinality and telemetry volume estimates;
5. collection, export, buffering, retry, and loss behavior;
6. dashboards, alerts, owners, and runbooks;
7. verification plan and known blind spots;
8. cost budget and conditions for reducing telemetry.

## Anti-Patterns

- Logging prose and parsing it later with fragile regular expressions.
- Writing application log files inside containers without an explicit platform
  requirement.
- Treating NDJSON as the only valid telemetry transport.
- Logging raw request or response bodies, tokens, credentials, or unrestricted
  exception context.
- Putting user, request, session, or raw path identifiers in metric labels.
- Generating a new trace or correlation ID at every service hop.
- Marking every span as an error because the business operation was declined.
- Sampling required audit events without a policy that preserves obligations.
- Alerting on CPU alone without connecting it to user impact or capacity risk.
- Unbounded collector queues or retries presented as loss prevention.
- Assuming observability storage is an immutable audit system.
