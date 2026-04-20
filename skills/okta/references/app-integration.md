# Okta App Integration Template

Use this template for every new SSO app integration. Fill it in before writing Terraform.

---

## 1. App Overview

- **App name:**
- **Vendor / URL:**
- **Business owner:**
- **Technical owner:**
- **Data sensitivity (tier 1-3):**
- **Expected user population:**

---

## 2. Protocol

- [ ] OIDC (preferred for modern apps)
- [ ] SAML 2.0 (only if app requires)
- [ ] Other (WS-Fed, etc.) - document and justify

### OIDC details

- **Flow:** authorization code + PKCE (public clients) / authorization code + client secret (confidential)
- **Grant types allowed:** (typically just `authorization_code` and `refresh_token`)
- **Redirect URIs:** (explicit list, no wildcards)
- **Logout URI:**
- **Access token lifetime:** (default 60 min)
- **Refresh token rotation:** enabled
- **Scopes:** (minimum required)

### SAML details

- **ACS URL:**
- **Entity ID (Audience):**
- **NameID format:** `emailAddress` or `persistent`, explicit
- **Signature algorithm:** SHA-256
- **Signed assertion:** yes
- **Encrypted assertion:** yes for sensitive apps
- **Assertion lifetime:** 5 minutes (NotBefore / NotOnOrAfter)

---

## 3. Attribute Mapping

Only map what the app needs.

| App attribute | Okta source | Transform | Required? |
|---|---|---|---|
| `email` | `user.email` | none | yes |
| `first_name` | `user.firstName` | none | yes |
| `last_name` | `user.lastName` | none | yes |
| `department` | `user.department` | none | no |
| `employee_id` | `user.employeeNumber` | none | conditional |

---

## 4. Group Assignment

- **Assignment strategy:** Group rule from HRIS attribute (preferred) / static group (with justification)
- **Assigned groups:**
- **Group rule (if dynamic):**
  - e.g., `user.department == "Engineering" AND user.employeeType == "Full-Time"`

---

## 5. Provisioning

- [ ] SCIM (app supports SCIM 2.0)
  - Actions: create / update / deactivate
  - Reactivation behavior documented
  - SCIM secret stored in vault
- [ ] JIT only (login creates / updates user)
- [ ] Manual (requires deprovisioning runbook)

---

## 6. Sign-On Policy

New per-app Sign-On Policy:

| Rule # | Condition | Action |
|---|---|---|
| 1 | Group not in allowed list | Deny |
| 2 | Network zone = BlockedIPs | Deny |
| 3 | Authenticator = WebAuthn AND device managed | Allow, session 8h |
| 4 | Authenticator = Okta Verify (push) AND device managed | Allow, session 4h |
| 5 | Any other | Deny |

- **MFA frequency:** every sign-on / per-session / daily (pick based on tier)
- **Session lifetime:** (match the rules above)

---

## 7. Testing

- [ ] App created in preview org
- [ ] OIDC / SAML handshake successful with a test user
- [ ] Attributes arrive correctly in the app
- [ ] SCIM provisioning tested (create, update, deactivate)
- [ ] Sign-On Policy behaves as expected (deny paths and allow paths)
- [ ] Logout tested (single-logout if configured)
- [ ] Session lifetime honored

---

## 8. Rollout

- [ ] Communication to affected users
- [ ] Help desk primer
- [ ] Rollback plan (deactivate app, fall back to legacy SSO)
- [ ] Phased enablement (by group, by region, etc.)
- [ ] Monitoring dashboard (failures, MFA prompts, session timeouts)

---

## 9. Terraform

Resources to create:

- `okta_app_oauth` or `okta_app_saml`
- `okta_app_group_assignments`
- `okta_app_signon_policy` (Identity Engine) or `okta_policy_rule_signon`
- `okta_app_user_schema_property` (if custom attributes)
- SCIM: `okta_app_oauth_api_scope` / provider-specific config

Module structure:

```
modules/
  okta-app/
    main.tf          # resources
    variables.tf     # app name, groups, redirect URIs, policy tier
    outputs.tf       # app id, client id / entity id
    README.md        # usage example
```

---

## 10. Review Checklist

- [ ] Protocol choice justified (OIDC vs SAML)
- [ ] Minimum redirect URIs / ACS URL
- [ ] Attribute mapping minimal and explicit
- [ ] Group rule uses HRIS attrs where possible
- [ ] SCIM enabled if supported
- [ ] Per-app Sign-On Policy with default deny
- [ ] MFA requirement matches data sensitivity tier
- [ ] Terraform-managed
- [ ] Preview org tested before prod
- [ ] Rollback plan documented
- [ ] SIEM alert on app-policy changes
- [ ] Owner fields filled in
