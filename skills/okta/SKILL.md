---
name: okta
description: Okta Workforce Identity playbook. Workflows for new SSO app integration, sign-on policy hardening, SCIM provisioning rollout, IdP migration, login-failure debugging, signing key rotation, and admin role audit. Use when designing, operating, or auditing Okta (orgs, apps, users/groups, policies, lifecycle, Workflows, ASA, Admin API, terraform-provider-okta).
---

# Okta Workforce Identity - Playbook

**Companion rule:** `317-okta.mdc`. This skill turns those patterns into end-to-end workflows.

**Scope:** Okta Workforce Identity Cloud (WIC). For Customer Identity Cloud (Auth0 / Okta CIC), patterns differ; consult Auth0 docs for tenants, connections, hooks, and actions.

---

## When to invoke

Use when the user:

- Is adding or changing an SSO/SAML/OIDC app integration
- Needs to tighten or audit sign-on policies, MFA, or authenticator policies
- Is rolling out SCIM provisioning (inbound from HRIS or outbound to apps)
- Is migrating from ADFS, Ping, Azure AD / Entra ID, or OneLogin
- Needs to debug a user login failure with evidence from System Log
- Must rotate signing keys, API tokens, or certificates
- Is auditing admin roles, API token usage, or lifecycle hygiene
- Is designing Workflows for JML or cross-app orchestration
- Is managing Okta via `terraform-provider-okta`

---

## Golden Rules (anchor for every workflow)

1. **HRIS is the source of truth**, not Okta.
2. **MFA for everyone; phishing-resistant MFA for admins.**
3. **OAuth 2.0 for Okta** (client-credentials) beats long-lived SSWS tokens.
4. **Per-app sign-on policy, default deny.**
5. **Terraform is the source of config; click-ops is drift.**
6. **System Log belongs in the SIEM**, not just the Okta UI.

---

## Workflow 1 - New SSO App Integration

Ship a new app with SSO and (where possible) provisioning.

### Steps

1. **Choose the protocol.** OIDC for modern apps and APIs. SAML only when the app requires it.
2. **Catalog first.** If the app is in the Okta Integration Network (OIN), use the OIN template; do not hand-roll config.
3. **Pick the sign-on flow.**
   - OIDC: authorization code + PKCE (public clients) or code + client secret (confidential).
   - SAML: signed SHA-256, audience restriction set to the exact SP, NameID explicit.
4. **Configure trusted origins / redirect URIs** to the minimum set.
5. **Attribute mapping.** Only map what the app needs. Explicit transforms, no pass-through.
6. **Provisioning.**
   - SCIM inbound if the app supports it (Okta creates users in the app).
   - SCIM outbound not typical for apps (HRIS -> Okta path already covers this).
   - Without SCIM: JIT provisioning at login; document deprovisioning (often manual).
7. **Group assignment.** Via group rules on HRIS attributes, not manual assignment.
8. **Sign-On Policy.** Create a per-app policy:
   - Default deny
   - Allow specified groups only
   - MFA required (phishing-resistant if sensitive)
   - Session lifetime appropriate for app
9. **Testing.** Preview org first, then prod. Test with a non-admin user.
10. **Rollout.** Communications, help desk primer, and a rollback plan (deactivate app, re-enable old SSO).
11. **Terraform.** Import or author resources: `okta_app_oauth` / `okta_app_saml`, `okta_app_group_assignment`, `okta_app_policy_signon`.

**Deliverable:** Terraform PR, Sign-On Policy doc, rollout plan.

See [references/app-integration.md](references/app-integration.md) for the template and review checklist.

---

## Workflow 2 - Harden Sign-On Policies

Audit and tighten existing Sign-On Policies (org-wide and per-app).

### Steps

1. **Inventory.** List all Sign-On Policies + which apps they govern. Any apps using the default policy? That's a finding.
2. **Tier the apps** by sensitivity (admin consoles, finance, source code, marketing tools, etc.).
3. **For each tier, set:**
   - Required authenticators (tier 1 = phishing-resistant; lower tiers = Okta Verify)
   - MFA frequency (every sign-on vs session-bound vs daily)
   - Session lifetime
   - Device assurance (managed device, screen lock, biometric)
   - Network zone conditions (block known-bad, loosen on corporate)
4. **Fix the default policy.** Make it strict; treat it as the floor, not the norm.
5. **Remove legacy factors.** SMS only as a recovery channel, not a primary factor; Security Question disabled.
6. **Propose changes in the preview org first.** Test with non-admin + admin accounts.
7. **Roll out in waves.** Start with IT / Security, expand by department.
8. **Monitor.** Watch System Log for failed sign-ins, factor-reset bursts, access denials - tune before the helpdesk tickets pile up.

**Deliverable:** Policy audit doc, Terraform changes, rollout plan, SIEM alert for policy-change events.

---

## Workflow 3 - SCIM Provisioning Rollout

Move from manual or JIT provisioning to SCIM (inbound from HRIS, outbound to apps).

### Inbound (HRIS -> Okta)

1. **Source selection.** Workday, BambooHR, UKG, ADP, etc. Okta has certified connectors.
2. **Schema mapping.** Map HRIS attributes to Okta profile. Decide what Okta owns vs what HRIS owns (HRIS masters identity attributes; Okta masters Okta-specific fields).
3. **Sync scope.** Full population, pilot department, or contractor-only initially.
4. **Dry-run.** Use the connector's dry-run / preview mode.
5. **Reconciliation plan.** What happens if HRIS has a user Okta doesn't (create)? Vice versa (deactivate)? Conflict (HRIS wins).
6. **Cutover.** Freeze manual user creation. Enable sync. Monitor.
7. **Lifecycle automation.** Ensure deactivation / termination events propagate within SLA (ideally minutes).

### Outbound (Okta -> App)

1. **App compatibility.** Check if the app supports SCIM 2.0.
2. **Scope.** Push users / groups / both? Provisioning actions (create, update, deactivate, reactivate)?
3. **Secret handling.** SCIM credentials from vault, not clipboard.
4. **Test.** Provision a test user, update profile, deactivate; verify each in the app.
5. **Enable for one group, then roll out.**

**Deliverable:** SCIM connector config (Terraform where supported), reconciliation report, monitoring dashboard for sync errors.

---

## Workflow 4 - Migrate from Another IdP

Common: ADFS, Ping, Azure AD / Entra ID, OneLogin, CA SiteMinder.

### Steps

1. **Inventory.** Apps, attributes, sign-on policies, users, groups, policies, provisioning integrations, custom code.
2. **Okta org setup.** Prod org; preview org for testing.
3. **Identity federation strategy.**
   - Big-bang (risky for large estates)
   - Phased (per-department or per-app), with Okta as inbound federated IdP trusting the legacy IdP during transition
   - Coexistence (Okta as primary, legacy IdP for specific apps) - typical for 6-18 months
4. **User migration.**
   - HRIS-sourced: enable inbound SCIM / connector.
   - AD-sourced: install AD Agent; set up Desktop SSO where applicable.
5. **App migration.** Per app: recreate in Okta (OIN template preferred), test, cut over, decommission legacy.
6. **MFA.** Enroll users in Okta Verify / WebAuthn during first Okta sign-in; do not carry legacy factors.
7. **Workflows / automation.** Port custom provisioning to Okta Workflows or to your own code against Okta API.
8. **Cutover per app.** Rollback plan = switch DNS / SSO URL back; practice the rollback.
9. **Decommission legacy.** Only after months of overlap, clean audit, and communication.

**Deliverable:** Migration plan, per-app cutover runbook, rollback procedures, go/no-go checklist.

---

## Workflow 5 - Debug a Login Failure

When a user can't sign in or an app fails SSO.

### Steps

1. **Get specifics.** User email, app, approximate time, error shown, recent changes.
2. **Open System Log.** Filter by user (`actor.alternateId`) and time window.
3. **Look for the event chain.**
   - `user.authentication.auth_via_IDP` (IdP flow)
   - `user.session.start` / `user.session.start_mfa`
   - `app.generic.unauthed_app_access_attempt` (policy denial)
   - `policy.evaluate_sign_on` (which policy, which rule, outcome)
4. **Read the `outcome.reason`** and `debugContext` fields - they tell you exactly which rule denied.
5. **Common causes:**
   - Wrong group membership (user not in app's assigned group)
   - Policy rule denies based on device / network / factor
   - Factor enrollment incomplete
   - Session expired; re-authentication required but blocked by policy
   - App secret / signing cert expired or rotated
   - Clock skew (SAML NotBefore / NotOnOrAfter)
   - SCIM deactivated the user (terminated in HRIS)
6. **Reproduce** with a test user in preview org where possible.
7. **Document the finding** in the ticket. If it's a config bug, fix via Terraform; if it's a user issue, correct via supported self-service or helpdesk-verified process.

**Deliverable:** System Log excerpts, root cause, fix (code or process).

---

## Workflow 6 - Rotate Signing Keys and API Tokens

### App signing keys (SAML, OIDC client secrets)

1. **Schedule.** Quarterly or on compromise; never "someday".
2. **Dual-key rollout.** Add new key; publish both; wait for all relying parties to pick up the new JWKS; retire old key.
3. **SAML certs.** Upload the new IdP cert to the SP; both certs valid during overlap; then remove the old one.
4. **Document** the rotation in the runbook and audit log.

### API tokens (SSWS or OAuth client credentials)

1. **Mint the new token** scoped to the same role and service principal.
2. **Update the secret in the vault**.
3. **Let callers pick up the new secret** (hot reload or rolling restart).
4. **Monitor for failures**; roll back if needed.
5. **Revoke the old token** only after no usage for a grace period.

### ASA certificates

1. ASA rotates per-session ephemeral certs automatically. For the project / role CA, rotate per ASA guidance.

**Deliverable:** Runbook entries, SIEM alerts for token creation, evidence of old-key retirement.

---

## Workflow 7 - Admin Role Audit

Quarterly or after any org change.

### Steps

1. **List everyone with admin roles.** Super Admin, Org Admin, Read-Only Admin, App Admin, Group Admin, Help Desk Admin, API-scoped admins.
2. **Map each admin to:**
   - A named person (no group assignments for Super Admin)
   - A business justification
   - Scope (all apps vs specific apps; all groups vs specific groups)
3. **Flag findings:**
   - Standing Super Admin on a human (remove; use JIT)
   - Over-scoped admin (reduce)
   - Ex-employee (remove - should have been caught by lifecycle, confirm incident)
   - Shared accounts acting as admins (convert to per-user)
4. **Audit API tokens.** Every token maps to a service principal + business justification. Rotate any without.
5. **Audit Workflow connections.** Each connection uses a scoped service principal.
6. **File remediation tickets.** Track to close.

**Deliverable:** Admin audit report, remediation tickets, updated governance doc.

---

## Review Output Format

When reviewing an Okta change, structure findings like this:

```
[BLOCKER] <one-line summary>
Finding: <what's wrong>
Evidence: <System Log ID or Terraform diff or Okta UI screenshot reference>
Fix: <specific, actionable>

[IMPORTANT] <...>
[SUGGESTION] <...>
```

BLOCKER = weakens baseline posture (MFA off, Super Admin grant, policy loosened, TF drift to click-ops).
IMPORTANT = misalignment with the rule in `317-okta.mdc`.
SUGGESTION = cleanup / best-practice.

---

## Common Failure Modes

- Super Admin as "the integration account" - replace with OAuth 2.0 for Okta + scoped role.
- One Sign-On Policy for everything - per-app policies.
- Manual user creation for employees - HRIS source of truth.
- SMS as primary MFA - Okta Verify / WebAuthn.
- System Log viewed by humans only - stream to SIEM.
- Click-ops in Okta UI while Terraform "owns" the org - drift detection + disabling UI where possible.
- No reconciliation plan for SCIM - defaults can deactivate unexpectedly.
- Legacy IdP kept "just in case" indefinitely - plan decommission with a date.

---

## References

- [references/app-integration.md](references/app-integration.md) - New SSO app template (OIDC/SAML), Sign-On Policy template, review checklist
- [references/policy-hardening.md](references/policy-hardening.md) - Sign-On / Authenticator / MFA policy tiers and defaults
- [references/scim-rollout.md](references/scim-rollout.md) - SCIM inbound + outbound rollout patterns
- [references/system-log-queries.md](references/system-log-queries.md) - Useful System Log queries for debugging and audit

## Related

- Rule: `317-okta.mdc` (Okta-specific patterns)
- Rule: `315-iam.mdc` (protocols: OIDC, SAML, PKCE, PKI)
- Rule: `316-zero-trust.mdc` (always-on Zero Trust principles)
- Rule: `412-aws-iam.mdc` (AWS-Okta federation)
- Skill: `aws-iam` (AWS IAM patterns, cross-account)
- Skill: `zero-trust` (identity under Zero Trust)
