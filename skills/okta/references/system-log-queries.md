# Okta System Log - Useful Queries

The System Log is Okta's audit surface. Use it for debugging, audit, and alerting.

---

## Basic filters (Okta UI or API)

All queries below can be run in the UI (Reports -> System Log) or against `/api/v1/logs` with the `filter` or `q` parameter.

---

## Debug a user login failure

**UI filter:**

```
Actor: <user@example.com>
Time: last 1 hour
Event type: policy.evaluate_sign_on OR user.session.start OR user.authentication.auth_via_IDP
```

**API (`filter`):**

```
actor.alternateId eq "user@example.com" and published gt "<iso-ts-1h-ago>"
```

Look for `outcome.result == DENY` and read `outcome.reason` + `debugContext.debugData`.

---

## All sign-in denials in the last hour

```
eventType eq "user.session.start" and outcome.result eq "DENY"
```

Aggregate by `outcome.reason` to see common denial patterns. A spike is either a policy change, a degraded IdP connection, or an attack.

---

## Admin role grants

```
eventType eq "user.account.privilege.grant"
```

Alert on any match. Each event's `target[]` includes the user who received the role and the role itself.

---

## Authenticator / factor changes

```
eventType sw "user.mfa"
```

Covers enrollment, reset, removal, challenge success/failure. Alert on unexpected factor removals for any user; high-confidence signal for account takeover.

---

## Policy changes

```
eventType sw "policy"
```

Catches policy create/update/delete. Should correlate with a Terraform apply log; anything else is click-ops drift.

---

## API token creation / rotation

```
eventType eq "api_token.create" or eventType eq "api_token.revoke"
```

Alert on creation; verify each against a ticket.

---

## Okta Workflows activity

```
eventType sw "workflows."
```

Track flow executions, failures. `target[]` shows the flow; `outcome` shows the result.

---

## App configuration changes

```
eventType sw "application.lifecycle" or eventType sw "application.user_membership"
```

Change audit for apps - create, delete, assign, unassign, suspend, reactivate.

---

## Impossible travel / suspicious sign-ins

Build this by combining:

```
eventType eq "user.session.start" and outcome.result eq "SUCCESS"
```

with `client.geographicalContext` fields. Compute time-distance between successive sign-ins per user; flag impossible travel.

ThreatInsight and Risk Scoring surface some of this natively; cross-reference.

---

## "Who did this" patterns

**Who deactivated user X?**

```
eventType eq "user.lifecycle.deactivate" and target.id eq "00u..."
```

Look at `actor` for the admin or service principal.

**Who changed policy P?**

```
eventType eq "policy.lifecycle.update" and target.id eq "00p..."
```

---

## Service principal / machine-to-machine audit

**All events by a specific API token / service principal:**

```
actor.id eq "<service-principal-id>"
```

**Uses of a specific API token:**

```
authenticationContext.credentialProvider eq "OKTA_AUTHENTICATION_PROVIDER" and actor.type eq "SystemPrincipal"
```

Combine with a token-to-service mapping you maintain.

---

## SCIM provisioning errors

```
eventType sw "application.user_membership" and outcome.result eq "FAILURE"
```

Filter by app to isolate noisy integrations.

---

## Export to SIEM

Pick one:

1. **Log Streaming (native)** - AWS EventBridge or Splunk; best option if supported
2. **Event Hooks** - Okta pushes events to an HTTPS endpoint you run; durable if you implement idempotent consumption
3. **Polling** - simple but lossy at scale; use with continuation cursors (`?after=...`) not time-based pagination

All events contain a unique `uuid`; use it as the idempotency key in the SIEM pipeline.

---

## Retention

- System Log retention in Okta itself is typically 90 days for most tenants
- Extend via SIEM for compliance retention (1-7 years typical)
- Store the `uuid` + full event JSON; compress; immutable storage

---

## Alerting examples

| Alert | Condition |
|---|---|
| Admin role granted | `eventType eq "user.account.privilege.grant"` |
| MFA factor removed | `eventType eq "user.mfa.factor.deactivate"` |
| Policy changed | `eventType sw "policy.lifecycle"` |
| API token created | `eventType eq "api_token.create"` |
| Unusual sign-in volume | count > baseline + N stddev over 15 min |
| Failed sign-in burst | `outcome.result eq "FAILURE"` count > N per user in 5 min |
| Org impersonation | `eventType eq "user.session.impersonation.initiate"` |
