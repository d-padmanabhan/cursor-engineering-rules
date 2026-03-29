# Podtrace for Kubernetes

Use Podtrace for short-lived, on-demand runtime diagnostics when logs, metrics, and existing tracing do not explain what a pod is doing.

> [!IMPORTANT]
> Podtrace is a diagnostic tool, not a default always-on replacement for application logs, metrics, or distributed tracing.

## When to Use Podtrace

- Unexplained latency inside a pod
- Intermittent 5XX responses with no clear app-level error
- DNS lookups, TCP retransmits, or RTT spikes
- File-system stalls, page faults, OOM symptoms, or CPU blocking
- Production incident response when changing images or adding sidecars is not practical

## Prerequisites

- Linux kernel `5.8+` with BTF support
- Kubernetes cluster access
- Podtrace binary available in `PATH`, or use `./bin/podtrace` when running from a source checkout
- Required privileges or capabilities for eBPF tooling

> [!NOTE]
> Examples below use `podtrace`. If running from the upstream source tree, replace it with `./bin/podtrace`.

## Quick Workflow

1. Confirm the target pod, namespace, and recent symptoms with `kubectl describe pod`, `kubectl logs`, and cluster events.
2. Start with a bounded report using `--diagnose 20s`.
3. Escalate to live mode only if the shorter report does not isolate the problem.
4. Correlate Podtrace output with application logs, service metrics, and downstream dependency health before making changes.

## Common Commands

```bash
# Live runtime stream for a pod
podtrace -n production my-pod

# Bounded diagnosis report
podtrace -n production my-pod --diagnose 20s

# Expose Podtrace metrics locally
podtrace -n production my-pod --metrics

# Export distributed traces to an OTLP collector
podtrace -n production my-pod --tracing \
  --tracing-otlp-endpoint http://otel-collector:4318
```

When `--metrics` is enabled, Podtrace exposes metrics at `http://localhost:3000/metrics`.

## What to Look For

- **Network symptoms**: RTT spikes, retransmits, connection failures, DNS latency
- **Storage symptoms**: slow reads, writes, fsync calls, or sustained file I/O
- **Memory symptoms**: page faults or OOM kill events
- **Application symptoms**: HTTP latency, database call delays, Redis or Kafka activity
- **CPU symptoms**: blocking, scheduling delays, or hot processes

## Data Handling

> [!CAUTION]
> Podtrace can surface application-layer metadata such as HTTP paths, headers, SQL patterns, and other request details. Treat output as sensitive and restrict sharing accordingly.

- Prefer short sessions over long-running captures
- Capture only what is needed to diagnose the issue
- Redact or avoid pasting sensitive output into tickets, chat, or incident docs

## Source

- Upstream project: [gma1k/podtrace](https://github.com/gma1k/podtrace)
