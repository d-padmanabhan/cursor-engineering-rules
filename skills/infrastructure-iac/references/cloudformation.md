# CloudFormation patterns (AWS-native IaC)

CloudFormation is AWS-native Infrastructure as Code. It is extremely powerful, but easy to make changes that are hard to roll back if you do not plan update/replace behavior.

> [!IMPORTANT]
> Treat CloudFormation like production code: reviewed, tested in staging, and deployed with change sets.

---

## Safe workflow

1. Validate template syntax and lint:
   - `cfn-lint template.yaml`
   - `aws cloudformation validate-template --template-body file://template.yaml`
2. Preview changes:
   - `aws cloudformation create-change-set ...`
3. Review the change set (especially replacements)
4. Execute only after approval

---

## Naming conventions

- Parameters: `pEnvironment`, `pVpcId`
- Resources: `rVpc`, `rAppBucket`
- Conditions: `cIsProd`
- Outputs: `oVpcId`

---

## Common footguns

### Update replacements

Some updates cause **replacement** (new physical resource), which can be disruptive or destructive.

- Always check whether a change will replace a stateful resource (DBs, buckets)
- Use `DeletionPolicy` / `UpdateReplacePolicy` deliberately on stateful resources

### Drift

- Console changes cause drift and surprise during updates
- Prefer “no manual changes” and enable drift detection for critical stacks

### Parameters and secrets

- Do not hardcode secrets in templates
- Prefer references to secret managers (SSM/Secrets Manager) with least privilege

---

## Minimal patterns

### Parameters and conditions

```yaml
Parameters:
  pEnvironment:
    Type: String
    AllowedValues: ["dev", "staging", "prod"]

Conditions:
  cIsProd: !Equals [!Ref pEnvironment, "prod"]
```

### Guardrails for stateful resources

```yaml
Resources:
  rAppBucket:
    Type: AWS::S3::Bucket
    DeletionPolicy: Retain
    UpdateReplacePolicy: Retain
```
