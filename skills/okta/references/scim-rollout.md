# SCIM Rollout

Patterns for inbound (HRIS -> Okta) and outbound (Okta -> app) SCIM 2.0.

---

## Inbound: HRIS -> Okta

### Source of truth

- HRIS (Workday, BambooHR, UKG, ADP) owns: name, email, department, manager, title, employee status, start/end dates
- Okta owns: Okta-specific fields (login, factors, groups derived from rules)
- **Never** edit HRIS-sourced fields in Okta

### Attribute mapping (typical)

| HRIS | Okta profile | Master |
|---|---|---|
| `primaryWorkEmail` | `email`, `login` | HRIS |
| `firstName` / `lastName` | `firstName`, `lastName` | HRIS |
| `workerType` (Regular / Contractor) | `employeeType` | HRIS |
| `department` | `department` | HRIS |
| `manager` | `manager` | HRIS |
| `businessTitle` | `title` | HRIS |
| `status` (Active / Terminated) | drives lifecycle | HRIS |
| `hireDate` / `terminationDate` | drives lifecycle | HRIS |

### Lifecycle events

| HRIS event | Okta action |
|---|---|
| Hire (before start date) | Create user, do NOT activate until start date |
| Start date | Activate; assign apps via group rules; send welcome email |
| Attribute change | Update profile; group rules recompute; app access recomputes |
| Manager change | Update; reassignments trigger downstream |
| Leave of absence | Suspend (do not deactivate); retain data |
| Return from leave | Unsuspend; no re-enrollment needed |
| Termination | Deactivate (not delete); revoke sessions and refresh tokens; schedule data retention per policy |
| Rehire | Reactivate where within retention window; otherwise new user |

### Reconciliation

- **Hourly or more frequent** incremental sync from HRIS
- **Daily full reconciliation** to catch drift
- **Alerting** on:
  - Orphan users in Okta not in HRIS
  - HRIS users not in Okta past start date
  - Unexpected deactivations
  - Sync errors

### Rollout

1. Schema mapping doc signed off by IT, Security, HR
2. Preview org: sync sandbox HRIS population; verify lifecycle
3. Pilot department or cohort in prod; watch tickets
4. Expand by department
5. Freeze manual user creation (UI + API except break-glass)

---

## Outbound: Okta -> App

### Scope

- Users (create / update / deactivate)
- Groups and memberships
- Profile attributes

### Prerequisites

- App supports SCIM 2.0 (check vendor docs)
- SCIM endpoint URL and authentication (bearer token / OAuth)
- SCIM secret stored in vault; injected into Okta config

### Setup steps (in Okta UI / Terraform)

1. Enable API Integration on the app
2. Provide SCIM base URL and credentials
3. Test connection
4. Enable provisioning features:
   - Create users
   - Update user attributes
   - Deactivate users
   - Sync groups and memberships (if supported)
5. Attribute mapping from Okta profile -> SCIM attributes
6. Test with a pilot user: provision, update attribute, deactivate
7. Enable for a group; monitor sync errors
8. Expand

### Attribute mapping cautions

- Only push attributes the app actually needs
- Some apps misbehave when all SCIM attributes are populated; keep minimal
- PII on app side: confirm app's data-handling posture matches classification

### Deactivation semantics

- Most apps deactivate on SCIM; some delete (destructive). Know which.
- For deleting apps, verify retention and restore policy on the app side

### Troubleshooting

- **401 / 403 errors:** token expired, scope too narrow
- **409 conflicts:** user exists in app but not linked - manual reconciliation or "match existing" setting
- **Slow sync:** pagination / rate-limit; increase sync frequency only if app supports it
- **Attribute mismatch:** app rejects a value (e.g., phone format); fix mapping transform

---

## SCIM Without Inbound (when HRIS integration isn't an option)

If HRIS integration is delayed:

- Use Okta as the interim source (not ideal, but common during transitions)
- Enforce that all user creation flows through a controlled API (HR ticket -> API call)
- Plan the HRIS cutover; do not let "interim" become permanent

---

## Monitoring

- Dashboard for sync success rate (inbound + outbound per app)
- Alerts on:
  - Sync failures above threshold
  - Latency above SLA (especially for off-boarding)
  - Unexpected deactivations (possibly HRIS error)
- Audit trail: SCIM events in System Log -> SIEM

---

## Anti-patterns

- Okta as identity source for employees (use HRIS)
- Manual user creation in downstream apps when SCIM would handle it
- SCIM attribute mappings copy-pasted across apps without review
- SCIM credentials stored in Okta UI without vault brokering
- "Delete" semantics used where "deactivate" was intended (data loss)
