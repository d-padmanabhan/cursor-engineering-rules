# KMS key policy vs IAM policy vs grants (what matters)

KMS is commonly misunderstood because **key policies** are first-class authorization controls.

## Three mechanisms

- **Key policy**: attached to the KMS key; primary control plane for the key
- **IAM policy**: permissions attached to an IAM principal (role/user)
- **Grant**: delegated permission issued at runtime with explicit constraints (often used by AWS services)

## Practical rules

- If a principal has an IAM policy allowing `kms:Decrypt` but the key policy does not allow it, you can still get `AccessDenied`
- For AWS services, prefer using service integrations that result in **grants** rather than broad key policies

## Grant grantee principals (common gotchas)

A grant grantee principal can be:

- AWS account root principal
- IAM user
- IAM role
- STS assumed-role session
- federated user

But typically not:

- IAM group
- service principal (for example `lambda.amazonaws.com`)
- AWS Organizations / OU
