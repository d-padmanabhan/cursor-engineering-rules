# Saga Orchestration and Choreography

A Saga coordinates local transactions so a multi-service business process reaches a successful, compensated, rejected, expired, or manually resolved terminal state.

## Model the State Machine First

Define:

- stable Saga and business-operation IDs;
- explicit states and valid transitions;
- command issued and outcome received for each step;
- deadlines and timeout transitions;
- retryable versus terminal failures;
- compensation eligibility and reverse ordering;
- late, duplicate, stale, and conflicting outcome behavior;
- terminal states, including manual intervention;
- versioning rules for in-flight instances.

Persist transitions atomically with any outgoing command intent, normally through an Outbox.

## Orchestration

An orchestrator owns workflow state and sends commands to participants.

Advantages:

- explicit control flow and compensation order;
- one place for deadlines, retries, and operator visibility;
- participants remain focused on local behavior;
- easier reasoning for branching or long-running workflows.

Costs:

- orchestrator availability and evolution become critical;
- central logic can become coupled to participant details;
- one team must own the end-to-end process and runbook.

Use durable workflow state or a workflow engine. Do not rely on in-memory timers or process-local state.

## Choreography

Participants react to events and emit subsequent events without a central decision maker.

Advantages:

- loose runtime coupling;
- independent reactions can evolve separately;
- natural fit for small, event-driven processes.

Costs:

- the workflow graph becomes implicit;
- circular dependencies and event storms are easier to create;
- timeouts, compensation order, and end-to-end status are harder to own;
- adding a participant can change global behavior without one visible state machine.

Document the event graph, owners, terminal outcomes, deadlines, and operational query. If those cannot be stated clearly, use orchestration.

## Commands and Events

- A command asks one owner to perform an action and expects a recorded outcome.
- An event states a fact that already happened.
- Do not encode imperative workflow coupling as misleading domain events.
- Include correlation, causation, operation, aggregate, and schema-version metadata.
- Participants must validate current state before applying a transition.

## Compensation

For every forward step, classify compensation as:

- exact reversal;
- semantic counter-action;
- partial mitigation;
- impossible after a defined point of no return.

Examples of semantic compensation include refunds, cancellation requests, inventory release, and corrective ledger entries. Do not delete audit history to simulate rollback.

Compensation itself requires:

- an idempotency key;
- durable state and retry policy;
- authorization and policy checks;
- timeout and late-success handling;
- observability and manual-resolution ownership.

If compensation fails permanently, move to an explicit state such as `compensation_failed` or `manual_resolution_required`; never report the Saga as successfully rolled back.

## Isolation Anomalies

Sagas do not provide serializable isolation across services. Design for:

- lost updates;
- dirty reads of intermediate state;
- concurrent Sagas acting on the same aggregate;
- write skew and invariant violations;
- a timeout racing with a late success.

Mitigations include semantic locks, reservations, escrow, expected-version checks, aggregate-level serialization, commutative updates, and revalidation before irreversible actions.

## Timeouts and Late Outcomes

A timeout means the outcome is unknown, not necessarily failed. Record the deadline transition, query authoritative participant state when possible, and define what happens if success arrives after compensation started.

Never issue compensation solely because a network call timed out unless the participant contract makes that safe.

## Versioning and Deployment

- Version commands, events, and persisted workflow definitions.
- Keep handlers backward compatible through rolling deployment and maximum workflow duration.
- Pin each Saga instance to a workflow version or define tested migration.
- Do not reinterpret old persisted states with new transition semantics accidentally.

## Operations and Recovery

Provide:

- query by Saga, business operation, correlation, and participant IDs;
- state age and stuck-workflow alerts;
- transition and command-attempt history;
- safe retry of one idempotent step;
- reviewed compensation or manual-resolution commands;
- reconciliation against participant authoritative state;
- immutable operator audit.

Administrative actions must enforce authorization, show the expected state transition, and reject stale operator decisions.

## Selection Smells

Prefer orchestration when choreography requires a “manager” service that listens to every event anyway. Prefer redesign when the workflow continually violates service boundaries or requires synchronous global consistency. Do not introduce a Saga merely because multiple services are present; read-only calls and independent notifications may not form one distributed transaction.
