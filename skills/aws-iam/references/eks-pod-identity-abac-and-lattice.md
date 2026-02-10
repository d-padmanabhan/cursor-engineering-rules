# EKS Pod Identity ABAC tags + VPC Lattice auth policies (namespace scoping)

EKS Pod Identity attaches a predefined set of **session tags** to the temporary credentials it vends to pods.
Those tags can be used as **principal tags** for authorization decisions (ABAC).

This is a useful pattern for multi-tenant clusters where you want **namespace-level** authorization boundaries without giving teams a way to broaden access by editing network policies.

> [!IMPORTANT]
> This is **authorization** control (IAM). It does not replace network-level controls for reachability or egress restriction.

## What EKS Pod Identity tags you get

EKS Pod Identity session tags (examples):

- `kubernetes-namespace`
- `kubernetes-service-account`
- `eks-cluster-name`

Docs: `https://docs.aws.amazon.com/eks/latest/userguide/pod-id-abac.html`

## Trust policy: restrict which pods can assume the role

EKS Pod Identity uses:

- `Principal`: `pods.eks.amazonaws.com`
- `Action`: `sts:AssumeRole` and `sts:TagSession`

Docs: `https://docs.aws.amazon.com/eks/latest/userguide/pod-id-role.html`

Example trust policy condition (namespace + service account):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowEksAuthToAssumeRoleForPodIdentity",
      "Effect": "Allow",
      "Principal": { "Service": "pods.eks.amazonaws.com" },
      "Action": ["sts:AssumeRole", "sts:TagSession"],
      "Condition": {
        "StringEquals": {
          "aws:RequestTag/kubernetes-namespace": ["my-namespace"],
          "aws:RequestTag/kubernetes-service-account": ["my-service-account"]
        }
      }
    }
  ]
}
```

## VPC Lattice auth policy: restrict access based on principal tags

VPC Lattice auth policies support **principal tags** (including session tags) via `aws:PrincipalTag/...`.

Docs: `https://docs.aws.amazon.com/vpc-lattice/latest/ug/auth-policies.html`

### Correct invoke action name

VPC Lattice service invocation uses:

- `Action`: `vpc-lattice-svcs:Invoke`

AWS managed policy reference: `https://docs.aws.amazon.com/aws-managed-policy/latest/reference/VPCLatticeServicesInvokeAccess.html`

### Example policy: allow invoke only from a specific namespace

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowNamespace",
      "Effect": "Allow",
      "Principal": { "AWS": "arn:aws:iam::ACCOUNT:role/multi-tenant-lattice-role" },
      "Action": "vpc-lattice-svcs:Invoke",
      "Resource": "arn:aws:vpc-lattice:REGION:ACCOUNT:service/svc-0123456789abcdef0/*",
      "Condition": {
        "StringEquals": {
          "aws:PrincipalTag/kubernetes-namespace": "my-namespace"
        }
      }
    }
  ]
}
```

## Operational gotchas

- **AuthZ requires both sides**: for a request to succeed, the caller identity permissions and the Lattice auth policy must both allow access (resource policy + identity policy model).
- **SigV4**: if the service or service network auth type is `AWS_IAM`, requests must be signed (see the Lattice docs section on SigV4).
- **Policy formatting**: the Lattice docs note that the policy JSON must not contain newlines or blank lines. If you hit validation errors, try minifying:

```bash
jq -c . policy.json > policy.min.json
```
