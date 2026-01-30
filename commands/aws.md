---
description: Design/review AWS changes using 410-aws.mdc (and IaC rules as applicable)
---

# AWS MODE ACTIVATED

You are now in **AWS MODE**. Any AWS-related work MUST follow:

- `rules/410-aws.mdc` (AWS platform engineering + best practices)
- `rules/100-core.mdc` (minimal, production-ready changes)
- `rules/310-security.mdc` (least privilege, no secrets)

Use this command when the user asks to:

- Design AWS architecture or service usage
- Modify/review AWS infrastructure code (Terraform/CloudFormation)
- Debug AWS operational issues (permissions, networking, failures)

## Guardrails (mandatory)

- Default to **least privilege** and secure-by-default configurations.
- Never embed credentials/secrets in code or docs.
- If touching infra-as-code, follow the repo’s IaC rules (`180-terraform.mdc`, `170-cloudformation.mdc`) as applicable.
- For any action that would change real AWS resources, require explicit user authorization and show the plan/impact first.

## Step 0: Determine intent (design vs implement vs review)

Infer intent from the user’s request. If ambiguous, ask **≤3** clarifying questions (account/region, service boundaries, security constraints, scale).

## Design

- Provide a minimal architecture plan (components, flows, IAM boundaries)
- Call out security posture (networking, encryption, logging)
- Prefer managed services and clear operational ownership

## Modify / Implement

- Keep diffs minimal and scoped
- Add/adjust IAM only as needed (least privilege)
- Ensure tagging conventions (if applicable)

## Review

Prioritize:

- **Critical**: public exposure, missing encryption, overly broad IAM, secrets handling, missing audit logging
- **Recommended**: operability (alarms/logs), cost footguns, scaling defaults
- **Optional**: naming/structure consistency

## Done condition

End with:

- Files changed (or “no changes made”)
- How to validate (lint/plan) and expected operational behavior
