# GitHub Actions Security

## Permissions

```yaml
# Minimal permissions by default
permissions: {}

# Or explicitly set what's needed
permissions:
  contents: read
  pull-requests: write
  issues: read

# Job-level overrides
jobs:
  build:
    permissions:
      contents: read
  deploy:
    permissions:
      contents: read
      id-token: write  # For OIDC
```

## OIDC for Cloud Authentication

```yaml
# AWS
- uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: arn:aws:iam::123456789:role/github-actions
    aws-region: us-east-1

# GCP
- uses: google-github-actions/auth@v2
  with:
    workload_identity_provider: projects/123/locations/global/workloadIdentityPools/github/providers/github
    service_account: github-actions@project.iam.gserviceaccount.com

# Azure
- uses: azure/login@v1
  with:
    client-id: ${{ secrets.AZURE_CLIENT_ID }}
    tenant-id: ${{ secrets.AZURE_TENANT_ID }}
    subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
```

## Secrets Best Practices

```yaml
# Pass a secret through the step environment, not script interpolation
- name: Deploy
  env:
    API_KEY: ${{ secrets.API_KEY }}
  run: |
    set -euo pipefail
    ./deploy.sh

# Never in artifact
- uses: actions/upload-artifact@v4
  with:
    name: build
    path: |
      dist/
      !dist/**/*.env  # Exclude env files
```

Prefer step-level secret scope. Do not persist secrets through `GITHUB_ENV` unless later steps genuinely need them, and never print a secret merely to mask it.

## Untrusted Contexts and Inputs

GitHub expressions are expanded before the shell parses a `run:` script. Shell quoting around `${{ ... }}` does not prevent command injection.

```yaml
# Unsafe: pull request titles can contain shell syntax
- run: echo "${{ github.event.pull_request.title }}"

# Safe: keep untrusted data out of the generated script
- name: Print pull request title
  env:
    PR_TITLE: ${{ github.event.pull_request.title }}
  run: printf '%s\n' "$PR_TITLE"
```

Apply the same pattern to issue bodies, commit messages, branch names, dispatch inputs, matrix values, and third-party action outputs. For constrained inputs such as environments or versions, validate against an allowlist or strict format before using them in paths, commands, or deployment decisions.

## Third-Party Actions

```yaml
# Pin to specific SHA (most secure)
- uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11

# Or pin to major version (reasonable balance)
- uses: actions/checkout@v4

# Never use @master or @main
# - uses: some-action@main  # BAD
```

## Branch Protection

```yaml
# Only trigger on protected branches
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

# Use pull_request not pull_request_target for PRs
# pull_request_target has write access - dangerous for forks
```

## Protected Deployment Environments

Use a GitHub Environment for each deployment boundary, especially production. Configure required reviewers and deployment-branch restrictions in repository settings, and keep production credentials environment-scoped.

```yaml
jobs:
  deploy:
    environment:
      name: production
      url: https://app.acme.com
    permissions:
      contents: read
      id-token: write
```

Environment approval is the authorization gate. Do not implement production authorization by comparing `github.actor` to a username in workflow code.

## Self-Hosted Runner Trust Boundary

Treat a self-hosted runner as privileged infrastructure:

- Do not run untrusted fork or pull-request code on runners with internal network or credential access
- Prefer ephemeral, single-job runners with clean state
- Isolate runner groups by environment and restrict which workflows may target them
- Allowlist required egress and avoid exposing broad internal networks
- Keep the runner, base image, and preinstalled tools patched and monitored

Use GitHub-hosted runners by default when the workload does not require private networking, specialized hardware, or a controlled execution environment.

## Dependency Review

```yaml
name: Dependency Review

on: pull_request

permissions:
  contents: read
  pull-requests: write

jobs:
  dependency-review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/dependency-review-action@v4
        with:
          fail-on-severity: moderate
```

## Secret Scanning

```yaml
name: Security Scan

on:
  push:
    branches: [main]
  pull_request:

jobs:
  secrets:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## Supply Chain Security

```yaml
- name: Generate SBOM
  uses: anchore/sbom-action@v0
  with:
    path: .
    format: spdx-json
    output-file: sbom.json

- name: Scan for vulnerabilities
  uses: anchore/scan-action@v3
  with:
    sbom: sbom.json
    fail-build: true
    severity-cutoff: high
```
