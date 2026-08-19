# Strategic Domain Design

Strategic Domain-Driven Design identifies where a model applies, who owns it, and how it relates to other models.

## Bounded Context Test

A bounded context should have:

- one coherent purpose and language;
- explicit model and invariant ownership;
- authoritative data and lifecycle;
- a named team or owner;
- defined inbound and outbound contracts;
- an independently understandable change history.

A bounded context does not require a separate process, repository, database, or deployment. Start with modules when distribution is not justified.

Weak boundary signals:

- one context per noun or table;
- identical language and ownership on both sides;
- chatty synchronous calls required for every operation;
- shared transactions or direct table access;
- boundaries copied from organization charts without domain evidence.

## Context Map Relationships

Use the smallest relationship that accurately describes influence and integration:

| Relationship | Meaning | Main risk |
|---|---|---|
| Partnership | Two contexts coordinate planning and evolution | Coupled delivery schedules |
| Shared kernel | Contexts jointly own a deliberately small model subset | Coordination and accidental expansion |
| Customer-supplier | Upstream plans around explicit downstream customer needs | Downstream dependence on upstream priorities |
| Conformist | Downstream adopts the upstream model without translation | Upstream concepts leak into downstream design |
| Anti-corruption layer | Downstream translates the upstream contract into its own model | Translation ownership and operational overhead |
| Open host service | Upstream exposes a supported integration protocol | Contract stability and support burden |
| Published language | A documented shared interchange schema | Schema governance and semantic drift |
| Separate ways | Contexts deliberately do not integrate | Duplication or delayed consistency |

Do not use relationship names as decoration. Record which team is upstream, who controls compatibility, and who operates translation failures.

## Anti-Corruption Layer

Use an anti-corruption layer (ACL) when:

- integrating a legacy or vendor model;
- the upstream language conflicts with the downstream domain;
- upstream churn must not force domain-wide changes;
- security or data classification requires filtering;
- multiple upstream representations need one downstream concept.

An ACL owns:

- protocol and schema adaptation;
- semantic translation;
- identifier mapping;
- validation and normalization;
- error classification;
- compatibility and observability.

It does not make an unreliable dependency reliable. Pair it with explicit resilience and reconciliation policies.

## Domain Discovery

Use concrete business scenarios:

1. Start with a trigger or command.
2. Identify the decision and required information.
3. State the invariant and authority.
4. Identify the resulting facts or domain events.
5. Ask which terms change meaning across steps or teams.
6. Group cohesive decisions and language.
7. test candidate boundaries against ownership and change history.

Treat workshop output as a hypothesis. Validate it against code, incidents, data ownership, support workflows, and domain-expert review.

## Migration

For an existing system:

1. Name current seams and shared-data coupling.
2. Select one valuable boundary with clear ownership.
3. Introduce an explicit contract or translation layer.
4. Move behavior before moving data when that reduces risk.
5. Add compatibility, shadow, and reconciliation checks.
6. Cut ownership over incrementally.
7. Remove the old path only after production evidence supports it.

Avoid a big-bang rewrite to "implement DDD." Boundary quality improves through tested slices.
