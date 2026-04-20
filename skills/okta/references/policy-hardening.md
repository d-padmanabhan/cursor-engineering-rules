# Okta Policy Hardening

Sign-On, Authenticator, and MFA Enrollment policies - tiers, defaults, and anti-patterns.

---

## Sensitivity Tiers

Tier apps by blast radius. Match policies to tier.

| Tier | Examples | Session | MFA | Factors |
|---|---|---|---|---|
| **Tier 1 - Critical** | Cloud admin consoles, source code, secrets manager, payment systems, privileged-access broker | 1-2 h, MFA each sign-on | phishing-resistant (WebAuthn / FIDO2) required | WebAuthn primary; Okta Verify FastPass acceptable |
| **Tier 2 - Sensitive** | HRIS, billing, customer data, production observability, VPN | 4-8 h, MFA daily or per-session | phishing-resistant preferred; push acceptable | WebAuthn or Okta Verify push |
| **Tier 3 - Standard** | Productivity (email, chat, docs), marketing tools | 8-24 h, MFA at policy intervals | Okta Verify (push / TOTP) | Okta Verify; WebAuthn for those who have it |
| **Tier 4 - Public / Vendor** | Kiosks, public-facing dashboards | Session-bound | MFA enrollment required; any supported factor | Any phishing-resistant factor |

---

## Authenticator Policy (org-wide)

Define which authenticators users can enroll.

**Enabled:**

- WebAuthn / FIDO2 (required for admin roles and Tier 1 apps)
- Okta Verify (push, TOTP, FastPass)
- TOTP app (as backup)
- Phone / SMS (recovery only; not primary factor)

**Disabled (or recovery-only):**

- Security Question
- Email (primary factor)

**Identity Engine Authenticator settings:**

- WebAuthn: require user verification, resident key where platform supports
- Okta Verify: require biometric when platform supports; FastPass with managed device

---

## MFA Enrollment Policy

- **New users:** mandatory enrollment within first sign-in; cannot defer
- **Multiple factors required:** at least two enrolled (primary + backup)
- **Factor reset:** helpdesk-initiated only, with identity-verification process (no self-service SMS reset)

---

## Sign-On Policy (default / org-wide)

**Make the default strict.** Per-app policies override when needed.

Recommended default rules (in evaluation order):

1. **Deny** from high-risk IPs / countries / ThreatInsight high-risk
2. **Deny** if no MFA enrolled (push to enrollment flow)
3. **Allow** from managed device + phishing-resistant MFA, session 8h
4. **Allow** from managed device + Okta Verify push, session 4h, MFA every 8h
5. **Allow** from unmanaged device + phishing-resistant MFA, session 2h, MFA each sign-on
6. **Deny** everything else

---

## Per-App Sign-On Policy

Every Tier 1 and Tier 2 app has its own policy. Override default for stricter rules only; never looser.

Example for a Tier 1 admin console:

1. **Allow** if user in `app-admin-cloud-prod` AND WebAuthn enrolled AND device assured AND network zone = Corporate/VPN, session 1h, MFA each sign-on
2. **Allow** if user in `app-admin-cloud-prod` AND WebAuthn enrolled AND device assured AND network zone = other, session 1h, MFA each sign-on AND step-up
3. **Deny** all else

---

## Network Zones

- **Corporate / VPN zones** - known office IPs, VPN egress
- **BlockedIPs zone** - known-bad, tor exits, high-risk countries (or use ThreatInsight)
- Use as rule conditions, not as replacement for MFA

---

## ThreatInsight / Risk Scoring

- **Enabled org-wide**
- Sign-on rules use risk score to step up, prompt more factors, or deny
- Alerts on high-risk sign-in bursts

---

## Legacy Apps (SWA)

- Avoid SWA (password vaulting) where possible; advocate for OIDC/SAML
- If SWA is the only option:
  - Auto-generated random password (user doesn't see it)
  - MFA on the Okta sign-on (before SWA handoff)
  - Session lifetime short

---

## Anti-patterns

- SMS as a primary factor in 2026
- Security Questions anywhere
- "Allow from anywhere with any factor" (the default many orgs ship with)
- No Sign-On Policy change control (click-ops)
- Password policies that require rotation on a schedule (NIST recommends against; rotate on compromise)
- Session lifetimes of "Never" for productivity apps
- MFA "remember device for 30 days" on admin consoles

---

## Rollout Sequence

1. Define tiers + target policies in a doc.
2. Preview org: implement; test with non-admin + admin.
3. IT / Security first in prod; measure helpdesk impact.
4. Roll out by department; tune thresholds.
5. Tighten to the target state; remove legacy factors.
6. Lock in via Terraform; enable drift alerts; schedule quarterly review.
