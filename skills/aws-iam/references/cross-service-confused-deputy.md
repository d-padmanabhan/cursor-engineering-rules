# Cross-service confused deputy prevention (`aws:SourceAccount`, `aws:SourceArn`)

When a **resource-based policy** grants access to an **AWS service principal** (for example,
`cloudtrail.amazonaws.com`, `events.amazonaws.com`, `sns.amazonaws.com`), the policy authorizes the
service principal — not the actor that configured the calling service.

If the policy is missing constraints, an unauthorized actor can sometimes abuse that trust relationship
(the **confused deputy** problem).

## Recommended pattern

- **Always add conditions** when granting access to an AWS service principal in a resource policy
- Prefer using **both**:
  - `aws:SourceAccount` to scope the caller to an expected AWS account
  - `aws:SourceArn` to scope the caller to an expected AWS resource ARN
- Where appropriate (org-wide guardrails), consider:
  - `aws:SourceOrgID`
  - `aws:SourceOrgPaths`

## Example: S3 bucket policy for CloudTrail (scope by source account)

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "CloudTrailAclCheck",
      "Effect": "Allow",
      "Principal": { "Service": "cloudtrail.amazonaws.com" },
      "Action": "s3:GetBucketAcl",
      "Resource": "arn:aws:s3:::amzn-s3-demo-bucket1",
      "Condition": {
        "StringEquals": { "aws:SourceAccount": "111122223333" }
      }
    }
  ]
}
```

## Example: S3 bucket policy for an AWS service (scope by source ARN)

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": { "Service": "appstream.amazonaws.com" },
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::amzn-s3-demo-bucket2/examplefile.psh",
      "Condition": {
        "ArnEquals": {
          "aws:SourceArn": "arn:aws:appstream:us-east-1:111122223333:fleet/ExampleFleetName"
        }
      }
    }
  ]
}
```

## Notes

- Not every AWS service supports every key in every integration. Use the service docs as source of truth.
- For KMS specifically, key policies/grants often have additional service-specific controls.

## References

- Confused deputy (cross-account + cross-service): `https://docs.aws.amazon.com/IAM/latest/UserGuide/confused-deputy.html`
- Global condition keys (including `aws:SourceAccount`, `aws:SourceArn`): `https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_condition-keys.html`
