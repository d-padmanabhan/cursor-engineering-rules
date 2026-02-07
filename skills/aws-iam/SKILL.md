---
name: aws-iam
description: AWS IAM deep-dive skill - principal types, policy evaluation, STS assume role, SCP guardrails, KMS key policies/grants, and AccessDenied debugging. Use when designing AWS authz/authn, cross-account access, or troubleshooting IAM/KMS/SCP AccessDenied errors.
---

# AWS IAM

## When to use

Use this skill when you are working on:

- IAM principals (users, roles, assumed-role sessions, service principals)
- Trust policies (`sts:AssumeRole*`) and cross-account access
- Identity-based vs resource-based policies
- Permission boundaries, session policies, and Organizations SCPs
- KMS key policies, grants, and `kms:Decrypt` / `kms:GenerateDataKey` failures
- Debugging `AccessDenied` in AWS (including cross-account and KMS)

## What to do (workflow)

1. Identify the **runtime principal** (often an STS assumed-role ARN)
2. Identify the **action** + **resource ARN(s)** from the error or design requirement
3. Determine which **policy layers** are in play:
   - identity-based policy
   - resource-based policy
   - permission boundary
   - session policy
   - SCP (Organizations)
4. Look for **explicit deny** first (it wins)
5. For cross-account flows:
   - validate the trust policy (who can assume)
   - validate the permission policy (what the role can do)
   - validate any resource policy (who can access the target resource)
6. For KMS:
   - validate key policy + IAM policy + any grant constraints

## References

- `references/iam-authorization-model.md`
- `references/cross-account-and-externalid.md`
- `references/kms-key-policy-and-grants.md`
