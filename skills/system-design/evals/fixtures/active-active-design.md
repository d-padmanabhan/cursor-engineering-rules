# Active-Active Checkout Proposal

Checkout runs in two regions and is advertised as 99.99% available with a 500 ms p99 target. Traffic shifts automatically between regions.

Every checkout synchronously requires:

- a global identity service with a 99.9% availability objective;
- a pricing API with a 99.95% objective;
- one globally shared database control plane;
- one DNS provider and one configuration service.

Both regions deploy together. Each client retries twice, but there is no end-to-end deadline or retry budget. The design document does not define the checkout SLI denominator, exclusions, dependency latency allocation, degraded behavior, failover capacity, or evidence from regional/control-plane exercises.
