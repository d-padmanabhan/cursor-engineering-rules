---
name: domain-driven-design
description: Designs and reviews software domain models using Domain-Driven Design, including subdomains, bounded contexts, context maps, ubiquitous language, aggregates, value objects, domain events, repositories, and anti-corruption layers. Use when business rules are complex, service or module boundaries are unclear, teams disagree on terminology, or the user mentions DDD, bounded contexts, aggregates, or domain modeling.
---

# Domain-Driven Design

Use Domain-Driven Design (DDD) to make complex business rules and ownership boundaries explicit. Do not use DDD vocabulary to disguise ordinary CRUD or technology-driven service decomposition.

## DDD Contract

- Start from business capabilities, policies, language, and change patterns, not tables, endpoints, or deployment units.
- Treat one model as valid only inside its bounded context. The same term may intentionally mean different things elsewhere.
- Use a ubiquitous language shared by domain experts and engineers in conversations, code, tests, APIs, and events.
- Align boundaries with cohesive invariants and ownership. A bounded context is a semantic and organizational boundary, not automatically a microservice.
- Keep aggregate boundaries small. One aggregate is one transactional consistency boundary.
- Reference other aggregates by stable identity rather than loading or mutating a large object graph.
- Make cross-context contracts explicit and versioned. Use an anti-corruption layer when an upstream model must not leak inward.
- Prefer a modular monolith until independent deployment, scaling, security, data ownership, or team autonomy justifies distribution.
- Validate models through concrete scenarios and examples with domain experts.

## Workflow

### 1. Establish the domain language

Collect:

- business outcomes and critical decisions;
- domain terms and definitions;
- actors, commands, policies, constraints, and exceptional cases;
- examples that distinguish similar concepts;
- terms with conflicting meanings across teams.

Create a glossary only from validated language. Treat unresolved synonyms and overloaded terms as modeling questions.

### 2. Classify subdomains

Separate:

- **Core subdomains**: differentiated capabilities that justify focused investment.
- **Supporting subdomains**: necessary business-specific capabilities that are not differentiators.
- **Generic subdomains**: commodity capabilities better bought, reused, or delegated when practical.

Do not label every component "core." The classification should influence build-versus-buy, staffing, design depth, and tolerance for vendor coupling.

### 3. Discover bounded contexts

For each candidate context, state:

- purpose and language;
- decisions and invariants it owns;
- authoritative data;
- team or owner;
- commands, queries, and published contracts;
- upstream and downstream relationships;
- expected rate and reason for change.

Split when language, invariants, ownership, or change cadence diverge materially. Merge contexts that are separated only by technical layers or speculative scaling.

Use the strategic design reference (`${HANDBOOK_ROOT}/skills/domain-driven-design/references/strategic-design.md`) for context maps and integration relationships.

### 4. Model behavior inside a context

Identify:

- entities with continuity and identity;
- value objects defined by immutable attributes;
- aggregates that protect invariants;
- aggregate roots as the only external mutation entry point;
- domain events that record meaningful completed facts;
- domain services for stateless domain behavior that has no natural entity or value-object home;
- repositories for loading and saving aggregate roots.

Application services orchestrate use cases, authorization, transactions, and external ports. They should not contain the domain rules that determine valid state.

Use the tactical modeling reference (`${HANDBOOK_ROOT}/skills/domain-driven-design/references/tactical-modeling.md`) for aggregate and event design.

### 5. Design cross-context interaction

Choose deliberately:

- synchronous request/response for immediate decisions;
- asynchronous events for facts and decoupled reactions;
- published language for stable shared contracts;
- anti-corruption layer for translation and model protection;
- separate ways when integration cost exceeds its value.

Do not share database tables, ORM entities, or mutable domain objects across bounded contexts. Shared kernels require explicit joint ownership and should remain small.

For consistency across contexts, use the distributed transactions skill (`${HANDBOOK_ROOT}/skills/distributed-transactions/SKILL.md`).

### 6. Validate and evolve

Validate with:

- example mapping or scenario walkthroughs;
- aggregate invariant tests;
- contract tests between contexts;
- architecture tests for forbidden dependencies;
- production signals tied to domain outcomes;
- explicit migration and compatibility plans.

Revisit boundaries when language, ownership, coupling, or change patterns provide evidence that the model is wrong. Avoid large rewrites solely to achieve a theoretically pure model.

## Review Questions

1. Which business decision or invariant does each model element protect?
2. Where does each term have one precise meaning?
3. Does each bounded context own its data and contract?
4. Can one command atomically preserve one aggregate's invariants?
5. Are cross-aggregate workflows explicit and eventually consistent where necessary?
6. Does infrastructure vocabulary leak into the domain model?
7. Are boundaries supported by team ownership and change patterns?
8. Is DDD complexity justified by domain complexity?

## Anti-Patterns

- One enterprise-wide canonical model for unrelated teams and workflows.
- One bounded context or service per database table.
- Aggregates that load an entire customer, account, or order graph.
- Repositories for every entity regardless of aggregate ownership.
- Anemic models where application services hold every business rule.
- Domain events used as commands or mutable data-transfer objects.
- Shared databases presented as independent services.
- Generic `Manager`, `Processor`, or `Service` types that conceal domain language.
- Applying event sourcing, CQRS, or microservices merely because DDD is mentioned.

## Required Output

Produce:

1. Domain goal, assumptions, and validated terminology
2. Subdomain classification
3. Bounded contexts with ownership and authoritative data
4. Context map and integration contracts
5. Key aggregates, invariants, commands, and domain events
6. Transaction and consistency boundaries
7. Migration and validation plan
8. Risks, unresolved language, and evidence that would change the model
