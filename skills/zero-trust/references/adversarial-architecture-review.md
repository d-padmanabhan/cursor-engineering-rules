# Adversarial Architecture Review

Use this workflow to challenge a proposed Zero Trust pattern without turning the exercise into offensive role-play. The objective is evidence that the design prevents, detects, contains, and recovers from credible abuse.

## 1. Pattern Contract

Record:

- business outcome and protected assets;
- human, workload, device, service, agent, and administrator principals;
- issuers, policy decision points, policy enforcement points, and resource owners;
- credentials, tokens, assertions, certificates, and capability lifetimes;
- data flows, classifications, egress destinations, and tenant boundaries;
- expected scale, quotas, latency, availability, cost, and operational owners;
- claimed guarantees and explicit non-goals.

Do not accept “identity-aware,” “mTLS,” “private network,” or “AI guardrails” as guarantees without naming the decision and enforcement behavior.

## 2. Reality Check

Challenge:

- Which assumptions have evidence, and which are estimates?
- What happens when the IdP, policy engine, CA, secret store, gateway, model provider, or audit sink is slow or unavailable?
- Do retries amplify authentication, authorization, or downstream load?
- Can quotas, certificate issuance, key operations, logging volume, or cross-region transfer create a cost or availability incident?
- Who operates every new control, and what is the recovery runbook?
- Does one control-plane compromise bypass multiple supposed layers?
- Is there a simpler architecture with a smaller blast radius?
- Under what conditions should this pattern not be used?

Reject designs whose production safety depends on undocumented vendor behavior or unlimited control-plane availability.

## 3. Defensive Abuse Simulation

For each credible path, capture:

| Field | Required content |
|---|---|
| Asset and objective | What the adversary seeks |
| Preconditions | Access or compromise already required |
| Entry and path | Trust boundaries and controls traversed |
| Identity used | Human, workload, agent, service, or administrator |
| Blast radius | Tenants, resources, data, duration |
| Persistence | Tokens, grants, sessions, keys, policies, memory |
| Evidence | Signals that should exist during the attempt |

Consider only applicable paths:

- stolen or replayed token/assertion;
- issuer, audience, subject, actor, or client substitution;
- confused-deputy and delegation-chain widening;
- overprivileged workload, agent, or integration;
- lateral movement across tenant, environment, cluster, account, or cloud;
- prompt injection or tool-chain manipulation;
- data exfiltration through allowed APIs, logs, model calls, or egress;
- shadow or orphaned non-human identity;
- policy, CA, IdP, CI/CD, or administrative control-plane compromise;
- revocation gaps and stale downstream sessions.

## 4. Defender Mapping

For every abuse path, define:

```text
Priority:
Attack path:
Prevent:
Detect:
Contain:
Recover:
Owner:
Verification:
Residual risk:
```

Detection is mandatory. A preventive control without a signal, owner, or test is an assumption.

Controls must protect distinct boundaries. Repeating the same authorization decision in three proxies is not defense in depth if no control detects stolen identity, limits egress, or contains persistence.

## 5. Verification

Use deterministic tests where possible:

- wrong issuer, audience, client, subject, actor, scope, nonce, or signature;
- expired, replayed, downscoped, revoked, or not-yet-valid credential;
- policy engine unavailable, stale, or returning malformed decisions;
- tenant and environment crossover attempts;
- sensitive action without required approval;
- model/tool input containing adversarial instructions;
- audit sink unavailable or delayed;
- quota exhaustion, retry storms, latency, and cost caps;
- kill switch, token invalidation, and credential replacement;
- restore and incident-evidence retrieval.

For each test, record expected enforcement point, decision, audit event, alert, and recovery outcome.

## 6. Exit Criteria

The architecture is ready only when:

- blocker attack paths are prevented or explicitly accepted by an authorized owner;
- high-impact attempts produce actionable detection;
- kill switches and recovery paths work across affected trust domains;
- degraded modes fail securely and meet stated availability constraints;
- cost and quota limits have hard stops where abuse could cascade;
- operators can answer who acted, through which identity, under which policy, and with what result;
- the design states a simpler rejected alternative and when the chosen pattern should not be used.
