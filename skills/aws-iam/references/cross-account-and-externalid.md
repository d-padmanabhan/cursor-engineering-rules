# Cross-account assume role + ExternalId (confused deputy)

## Cross-account access pattern

There are two common approaches:

- **Assume role into the target account** (STS): the target role trust policy allows the source principal to assume it
- **Resource policy allows the external principal**: the target resource policy names the external account/role as Principal

In both cases, the caller also needs the **permission** to perform the action on the resource.

## Trust policy vs permission policy

- **Trust policy**: who can assume the role (`sts:AssumeRole*`)
- **Permission policy**: what the role can do after it is assumed

## ExternalId - when to require it

Require `sts:ExternalId` in the trust policy when a third-party vendor assumes roles in your account and the vendor could otherwise be tricked into using their privileges against your account (the **confused deputy** problem).

Typical signal:

- A SaaS monitoring/tooling vendor provides you a role ARN and asks you to trust their principal

## Minimal trust policy snippet

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": { "AWS": "arn:aws:iam::111122223333:role/vendor-access" },
      "Action": "sts:AssumeRole",
      "Condition": {
        "StringEquals": { "sts:ExternalId": "REPLACE_WITH_CUSTOMER_GENERATED_ID" }
      }
    }
  ]
}
```
