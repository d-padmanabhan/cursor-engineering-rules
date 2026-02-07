# AWS IAM authorization model (quick, practical)

## The four inputs AWS evaluates

- **Principal**: who is calling (often an STS assumed-role session)
- **Action**: the API operation
- **Resource**: the ARN(s) being accessed
- **Context**: request attributes and condition keys

## The policy layers

In real systems, multiple layers can apply to the same request:

- Identity-based policy (attached to a role/user)
- Resource-based policy (S3 bucket policy, KMS key policy, Lambda permission, API Gateway resource policy, etc.)
- Permission boundary (limits the principal's maximum permissions)
- Session policy (optional, passed to STS at assume-role time)
- SCP (Organizations) (limits max permissions in an account/OU; does not grant)

> [!IMPORTANT]
> **Explicit deny wins** across all layers.

## Identity-based vs resource-based (fast rules)

- **Identity-based policy**: Principal is implicit (the attached identity)
- **Resource-based policy**: Principal is explicit (who is allowed)
- Cross-account access often requires **both**:
  - the caller has permissions, and
  - the resource policy (if present) trusts the caller principal

## Practical debugging checklist

1. Get the caller identity:

```bash
aws sts get-caller-identity
```

1. Confirm the principal ARN is what you expect (role vs assumed-role)
2. Search for explicit denies (policies, boundaries, SCP)
3. Check KMS key policy separately for KMS errors
