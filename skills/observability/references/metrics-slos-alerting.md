# Metrics, SLOs, Dashboards, and Alerts

Metrics are bounded numeric signals optimized for aggregation. Begin with a
decision or reliability question, not a dashboard layout.

## Metric Contract

For each metric, define:

- name and one precise meaning;
- type and monotonicity;
- unit and base-unit conversion;
- labels and allowed values;
- worst-case series count;
- collection interval and aggregation;
- reset, missing, stale, and partial-data behavior;
- owner and consumers;
- retention and cost.

Prefer counters for cumulative events, histograms for aggregatable
distributions, and gauges for current state. Use summaries only when their
client-side quantiles and cross-instance aggregation limitations are
understood.

## Naming and Units

Follow the selected ecosystem's current semantic conventions. For Prometheus:

- use snake case;
- use base units such as seconds and bytes;
- use `_total` for counters where the client library does not add it;
- do not encode label names in the metric name;
- expose raw counters and derive rates in the backend;
- keep one metric meaningful when summed or averaged across intended labels.

Do not mechanically rename established OpenTelemetry semantic conventions to
match a different backend. Define the translation at the collection or export
boundary.

## Cardinality Budget

Every unique metric label set creates a time series. Estimate the upper bound:

```text
series = metric variants
       * methods
       * normalized routes
       * status classes
       * regions
       * cells
       * remaining bounded labels
```

Reject unbounded or attacker-controlled labels:

- user, account, tenant, session, request, trace, or order IDs;
- email addresses and IP addresses;
- raw URLs, query strings, exception messages, SQL, or stack traces;
- timestamps, UUIDs, hashes, and arbitrary headers;
- dynamic pod or process values when aggregation does not need them.

Use normalized routes, status classes, bounded operation names, logs, traces,
or exemplars for high-cardinality detail. Tenant labels require an explicit,
bounded tenancy model and cost decision; "we need per-tenant dashboards" is not
enough for unbounded series creation.

Monitor active series, churn, rejected samples, ingestion bytes, query cost,
and cardinality by metric and label.

## SLIs and SLOs

An SLI must represent a user-visible outcome or a necessary correctness
property. Define:

- eligible population;
- good-event criteria;
- valid-event denominator;
- exclusions and why they are not user failures;
- aggregation window;
- missing-data and low-traffic behavior;
- source of truth and data delay;
- ownership and review cadence.

Examples include successful valid requests, jobs completed before a deadline,
fresh reads, durable writes, and correct authorization decisions. CPU,
container restarts, and queue depth are diagnostic or capacity signals, not
user-facing SLIs by themselves.

An SLO states the target and window. The error budget is the allowed bad-event
fraction or duration. Avoid targets selected only because they look standard.
Use product impact, dependency capability, historical evidence, and cost.

## Alerting

Alerts must produce an action:

- **Page:** urgent user impact or imminent exhaustion requiring immediate human
  response.
- **Ticket:** slower error-budget consumption, capacity risk, or maintenance
  work.
- **Dashboard only:** useful context with no direct action.

For SLO-backed services, prefer multi-window, multi-burn-rate alerts that pair
a longer window for significance with a shorter window for continued impact.
Derive thresholds from the SLO and budget policy rather than copying fixed
numbers from another service.

Every alert needs:

- service and owner;
- user impact and urgency;
- expression and data source;
- pending duration or paired windows;
- missing-data behavior;
- deduplication and inhibition policy;
- runbook and dashboard links;
- safe diagnostic steps;
- recovery condition;
- test evidence.

Alert on symptoms for paging and use cause-oriented signals for diagnosis.
Avoid paging independently on every replica or every layer of the same failure.

## Dashboards

A service landing dashboard should answer:

1. Are users meeting the SLO?
2. How quickly is the error budget being consumed?
3. Which operation, region, cell, tenant class, or dependency is affected?
4. Did a deployment, configuration, schema, or feature-flag change precede the
   impact?
5. Is the service saturated, shedding load, or accumulating old work?
6. Is telemetry complete and fresh enough to trust?

Show distributions rather than averages for latency. Display units, query
windows, time zones, data freshness, and links to definitions.

Avoid dashboards containing every available metric. A panel without a decision
or diagnostic question is inventory, not observability.

## Change and Business Signals

Record deployments, rollbacks, configuration publication, migration phases,
feature-flag changes, and major dependency events as annotations or bounded
events. Correlate them with service health without adding commit SHA or
deployment ID as an unbounded metric label.

Track business outcomes only when definitions, data classification, ownership,
and retention are explicit. Product analytics and operational telemetry may
require different stores and access policies.

## Verification

Test metrics and alerts as code:

- unit-test metric registration and label constraints;
- generate worst-case label inputs and enforce series budgets;
- test SLI numerator, denominator, exclusions, and empty windows;
- replay synthetic time series to verify firing and recovery;
- test paging routes, deduplication, inhibition, and runbook access;
- compare dashboard queries against known fixtures;
- verify telemetry delay or gaps do not silently report success.

## Current Sources

- [Prometheus Metric and Label Naming](https://prometheus.io/docs/practices/naming/)
- [Prometheus Alerting Rules](https://prometheus.io/docs/prometheus/latest/configuration/alerting_rules/)
- [Google SRE Workbook: Alerting on SLOs](https://sre.google/workbook/alerting-on-slos/)
- [Google SRE Workbook: Monitoring](https://sre.google/workbook/monitoring/)
