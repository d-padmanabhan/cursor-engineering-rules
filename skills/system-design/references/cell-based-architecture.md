# Cell-Based Architecture

Cell-based architecture limits failure impact by partitioning a workload into bounded, independently operated replicas. AWS calls these replicas **cells**; Azure commonly uses **deployment stamps**, **scale units**, or **cells**; Google SRE guidance describes related **vertical partitioning**. Use the provider's terminology when discussing a specific implementation.

A cell boundary must isolate the failure modes it claims to contain. Multiple compute stacks sharing one authoritative database, synchronous control plane, deployment path, or hard quota are replicas—not independent cells.

## Decide Whether Cells Are Justified

Use cells when measured scale, tenant isolation, regional/residency constraints, release safety, or outage-impact targets justify duplicated infrastructure and fleet operations.

Prefer a simpler deployment when:

- ordinary horizontal or vertical scaling meets the targets;
- only one data store needs sharding;
- the data model requires frequent cross-partition transactions or scatter-gather;
- every cell needs a full copy of globally authoritative mutable data;
- the organization cannot automate provisioning, placement, migration, rollout, drift detection, and recovery;
- reduced blast radius does not justify idle headroom and operating cost.

Record the failure-impact target, partition key, expected cell count, minimum cell cost, migration requirement, and condition that would reverse the choice.

## Partition and Placement

Choose a partition key that:

- matches a natural workload boundary such as tenant, account, geography, or resource owner;
- is available before most request processing;
- minimizes cross-cell operations;
- supports stable placement and explicit migration;
- accounts for skew and tenants that exceed normal cell capacity.

The placement service should consider measured usage, demand forecast, cell saturation, quotas, residency, affinity, migration cost, and operating headroom. Support dedicated placement or a documented split strategy for tenants larger than one cell.

Do not use a hash-ring change that silently remaps the fleet unless redistribution and authority transfer are explicitly designed and tested.

## Routing Contract

Keep routing thin, deterministic, horizontally scalable, and free of business logic.

The routing contract must define:

- tenant/entity-to-cell mapping and version;
- cache freshness and last-known-good behavior;
- stale-client redirects or equivalent transition behavior;
- response when a cell is unavailable;
- authorization for placement changes;
- audit and rollback of mapping updates.

Serving should continue for unaffected cells when the placement control plane is unavailable. Persist and use the last validated routing state—AWS describes this property as **static stability**. Fail conservatively rather than publish uncertain placement.

DNS or direct cell endpoints can reduce a shared routing tier but complicate remapping and client freshness. A common ingress simplifies clients but becomes a critical shared surface that needs independent scaling, regional redundancy, and failure testing.

## Control Plane and Data Plane

The control plane owns provisioning, placement, mapping publication, migration, rollout, and retirement. The data plane owns request routing and cell-local serving.

- Cell serving must not synchronously depend on control-plane availability.
- Validate and version configuration before publication.
- Keep rollback-compatible routing and configuration.
- Test stale, unavailable, delayed, and corrupt control-plane output.
- Limit administrative blast radius by cell and by rollout wave.

## Isolation and Shared Dependencies

Prefer cell-local databases, queues, caches, storage, mutable configuration, service quotas, and synchronous dependencies. Central analytics may consume asynchronous outputs but must not be on the serving path.

Inventory shared:

- identity and authorization services;
- DNS, gateways, certificate authorities, and key management;
- databases, queues, object stores, and global tables;
- CI/CD, artifact registries, feature flags, and configuration;
- observability, audit, and incident tooling;
- account/project/subscription quotas and network infrastructure.

For each shared dependency, state why sharing is acceptable, its correlated blast radius, degraded behavior, and the test that proves the claim. Frequent cross-cell traffic is evidence that the partition boundary is wrong.

## Cell Sizing and Overload

Define a tested maximum across relevant dimensions: requests/events per second, tenants, storage, connections, bandwidth, workers, and dependent-service quotas.

- Load-test one cell at its supported maximum, including skew and dependency degradation.
- Reserve headroom for failures, migration, and uneven tenant growth.
- Bound queues, concurrency, retries, and per-tenant resource use.
- Prioritize critical work and define rejection, shedding, or degraded responses.
- Model minimum infrastructure, idle capacity, fleet deployment, observability cardinality, and migration bandwidth.

Smaller cells reduce failure impact and scaling cliffs but increase replica count and idle capacity. Larger cells improve utilization and reduce fleet overhead but increase outage impact and quota risk.

## Migration and Rebalancing

Build online movement before cells are full:

1. reserve and validate destination capacity;
2. copy state to a non-authoritative destination;
3. reconcile and verify lag, completeness, and invariants;
4. transfer write authority with a versioned fence;
5. publish the new mapping;
6. redirect stale traffic from the old cell;
7. monitor and retain rollback compatibility;
8. remove old state only after the recovery window.

Define behavior for in-flight writes, delayed messages, duplicate delivery, caches, stale clients, and rollback after authority transfer. Migration operations must be idempotent and auditable.

## Evacuation and Recovery

A cell is a fault-containment boundary, not automatic failover capacity.

- Decide whether cells fail closed, degrade locally, or evacuate.
- Provision destination headroom before promising evacuation.
- Throttle movement so a local incident does not overload healthy cells.
- Separate regional, zonal, data-corruption, and control-plane recovery.
- Define data-authority and RPO/RTO behavior for every mode.
- Exercise cell isolation, restore, evacuation, and return-to-service.

Mass failover is unsafe when healthy cells cannot absorb the displaced load. Preserving isolation may be safer than redistributing traffic.

## Rollout and Observability

Provision cells with repeatable infrastructure as code and detect drift continuously. Deploy a canary inside a canary cell, then advance by cell or small wave. Gate progression on absolute SLOs, relative canary comparison, business invariants, and fleet capacity. Keep schema and routing changes compatible across mixed versions.

Attach cell identity and routing-map version to logs, metrics, traces, alerts, and audit events. Monitor:

- per-cell and fleet SLOs;
- router health and mapping freshness;
- capacity, saturation, rejected work, and tenant imbalance;
- cross-cell calls and shared-dependency failures;
- migration lag and authority state;
- deployed version, configuration drift, and rollout state.

Correlated symptoms across cells often reveal a hidden shared dependency.

## Current Sources

- [AWS: Reducing the Scope of Impact with Cell-Based Architecture](https://docs.aws.amazon.com/wellarchitected/latest/reducing-scope-of-impact-with-cell-based-architecture/cell-based-architecture.html)
- [AWS: Control plane and data plane](https://docs.aws.amazon.com/wellarchitected/latest/reducing-scope-of-impact-with-cell-based-architecture/control-plane-and-data-plane.html)
- [AWS: Cell routing](https://docs.aws.amazon.com/wellarchitected/latest/reducing-scope-of-impact-with-cell-based-architecture/cell-routing.html)
- [AWS: Cell sizing](https://docs.aws.amazon.com/wellarchitected/latest/reducing-scope-of-impact-with-cell-based-architecture/cell-sizing.html)
- [Azure Architecture Center: Deployment Stamps pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/deployment-stamp)
- [Google Cloud: Partition cloud applications to avoid global outages](https://cloud.google.com/blog/products/devops-sre/how-to-partition-cloud-applications-to-avoid-global-outages)
- [Google SRE Workbook: Canarying Releases](https://sre.google/workbook/canarying-releases/)
- [Google SRE Book: Handling Overload](https://sre.google/sre-book/handling-overload/)
