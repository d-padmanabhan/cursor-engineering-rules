# Circuit Breakers and Bulkheads

Circuit breakers limit repeated calls likely to fail. Bulkheads prevent one workload or dependency from consuming capacity needed by another. Neither pattern creates capacity or corrects a broken dependency.

## Circuit Breaker State Model

### Closed

Requests flow normally. Record eligible outcomes in a bounded rolling window.

### Open

Reject or route requests immediately for a bounded open interval. Return a stable failure classification so callers do not retry blindly.

### Half-open

Allow a tightly bounded number or rate of probes. Close only after enough successful evidence. Reopen on qualifying failure.

## Breaker Policy

Define:

- scope key: dependency, endpoint, operation, tenant, shard, or region;
- eligible failures;
- minimum sample volume;
- count, rate, or latency threshold;
- rolling window;
- open duration and jitter;
- maximum concurrent half-open probes;
- success evidence required to close;
- fallback or rejection behavior;
- state metrics and operator override policy.

Exclude caller validation, authentication, authorization, deterministic business rejection, and local programming errors. Counting them as dependency failures opens the wrong circuit.

Prefer a failure-rate or slow-call-rate threshold after a minimum sample volume over a fixed consecutive-failure count. Low-traffic endpoints need different evidence from high-volume paths.

## Breaker Scope

Too broad:

- one global state for all tenants, regions, endpoints, and operations;
- one noisy or invalid caller can block healthy work;
- recovery probes do not represent every affected partition.

Too narrow:

- every process instance has too little traffic to detect failure;
- aggregate dependency pressure remains uncontrolled;
- operators cannot explain divergent states.

Choose the narrowest scope that matches the actual failure domain while retaining enough observations for a meaningful decision.

Distributed breaker state is rarely free. Local breakers react quickly and avoid a shared control-plane dependency but can produce uneven behavior. Central state coordinates decisions but introduces latency, availability, and stampede risks. Start local unless coordinated state is justified by evidence.

## Recovery Safety

- Jitter open intervals to avoid synchronized probing.
- Limit half-open probes globally or per meaningful partition.
- Keep attempt deadlines and concurrency bounds active during probes.
- Do not close after one lucky success when the ordinary load is much larger.
- Observe accepted, rejected, probe, successful, failed, and state-transition counts.
- Alert on long-open circuits, oscillation, and fallback saturation.

## Bulkhead Forms

| Form | Isolates | Trade-off |
|---|---|---|
| Connection pool | Dependency or destination | Idle reserved connections |
| Semaphore | Concurrent operations | Rejection or waiting when full |
| Worker pool | Workload or priority | Capacity fragmentation |
| Bounded queue | Burst and consumer lag | Queue latency and expiry |
| Tenant partition | Noisy neighbors | Uneven tenant demand |
| Cell or stamp | Infrastructure blast radius | Replication and routing complexity |
| Separate quota | CPU, memory, API, or storage use | Reserved capacity and administration |

## Bulkhead Sizing

Size from:

- peak admitted arrival rate;
- service time distribution;
- downstream safe concurrency;
- caller deadline;
- queue-age objective;
- reserved priority capacity;
- failover and recovery headroom.

Define behavior at the boundary:

- reject immediately;
- wait only within remaining deadline;
- shed lower-priority work;
- route to another healthy partition when correctness permits;
- enqueue durably for asynchronous processing.

Unbounded waiting defeats isolation. A bulkhead is effective only if work outside it retains usable capacity.

## Composition

A common order is:

```text
admission and quota
  -> end-to-end deadline
  -> bulkhead acquisition
  -> circuit-breaker decision
  -> bounded retry with attempt timeout
  -> dependency call
  -> classified outcome and metrics
```

The exact order depends on whether rejected, probe, and retry attempts should consume scarce bulkhead capacity. Document the choice and test it under overload.
