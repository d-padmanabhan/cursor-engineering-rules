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
# Don't echo secrets
- run: |
    echo "::add-mask::${{ secrets.API_KEY }}"
    # Use without logging
    export API_KEY="${{ secrets.API_KEY }}"
    ./deploy.sh

# Use environment files
- run: |
    echo "API_KEY=${{ secrets.API_KEY }}" >> $GITHUB_ENV

# Never in artifact
- uses: actions/upload-artifact@v4
  with:
    name: build
    path: |
      dist/
      !dist/**/*.env  # Exclude env files
```

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
