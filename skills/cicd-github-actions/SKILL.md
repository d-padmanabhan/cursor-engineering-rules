---
name: cicd-github-actions
description: GitHub Actions best practices for CI/CD workflows. Covers security (permissions, secrets), performance (caching, matrix builds), reusable workflows, and common patterns for testing, building, and deploying. Use when working with .github/workflows/*.yml files, GitHub Actions, or when asking about CI/CD pipelines and automation.
---

# GitHub Actions CI/CD

## Core Objectives

- **Security**: Minimal permissions, secrets handling, OIDC
- **Performance**: Caching, matrix builds, parallelization
- **Maintainability**: Reusable workflows, composite actions
- **Reliability**: Concurrency control, retry logic

## Essential Checklist

- [ ] Workflows use minimal permissions (`permissions: {}` at root)
- [ ] Secrets never logged or exposed in artifacts
- [ ] Concurrency control configured
- [ ] Timeout values set on all jobs
- [ ] Caching implemented for dependencies
- [ ] PR workflows use `pull_request`, not `pull_request_target`
- [ ] A concise purpose comment follows the workflow `name:`
- [ ] Untrusted contexts and inputs reach shell commands through step-level `env`
- [ ] Production deploys use protected GitHub Environments
- [ ] Changed workflows pass `actionlint`

## Workflow Authoring Contract

Put a short operational description immediately after the workflow name. Document only what an operator or reviewer needs: purpose, triggers, required credentials, external dependencies, and approval gates.

```yaml
name: Deploy Application

# Deploys a tested release to the selected GitHub Environment.
# Triggers: manual dispatch.
# Authentication: cloud OIDC; no static cloud credentials.
# Approval: the production environment requires reviewers.
```

Treat `${{ github.event.* }}`, `${{ inputs.* }}`, issue text, branch names, and action outputs as untrusted data. Do not interpolate them directly into a `run:` script. Assign them to step-level `env`, quote the shell variable, and validate constrained values before use. See [Security](references/security.md).

For a complete starting point and local validation commands, use the [minimum viable workflow](references/minimum-viable-workflow.md).

## Minimal Permissions

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:

# Default: no permissions
permissions: {}

jobs:
  test:
    runs-on: ubuntu-latest
    # Job-level permissions
    permissions:
      contents: read
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - run: npm ci
      - run: npm test
```

## Caching

```yaml
- uses: actions/setup-node@v4
  with:
    node-version: '20'
    cache: 'npm'

# Or explicit caching
- uses: actions/cache@v4
  with:
    path: ~/.npm
    key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}
    restore-keys: |
      ${{ runner.os }}-node-
```

## Matrix Builds

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        node-version: [18, 20, 22]
        os: [ubuntu-latest, macos-latest]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
      - run: npm ci
      - run: npm test
```

## Concurrency Control

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

## Secrets Handling

```yaml
steps:
  - name: Use secret safely
    env:
      API_KEY: ${{ secrets.API_KEY }}
    run: |
      set -euo pipefail
      curl --fail --silent --show-error \
        -H "Authorization: Bearer ${API_KEY}" \
        https://api.acme.com
```

## Reusable Workflows

```yaml
# .github/workflows/reusable-build.yml
name: Reusable Build

on:
  workflow_call:
    inputs:
      node-version:
        required: false
        type: string
        default: '20'
    secrets:
      NPM_TOKEN:
        required: false

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ inputs.node-version }}
      - run: npm ci
      - run: npm run build
```

```yaml
# Calling workflow
jobs:
  build:
    uses: ./.github/workflows/reusable-build.yml
    with:
      node-version: '20'
    secrets:
      NPM_TOKEN: ${{ secrets.NPM_TOKEN }}
```

## Job Outputs

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    outputs:
      version: ${{ steps.version.outputs.value }}
    steps:
      - id: version
        run: echo "value=$(cat VERSION)" >> $GITHUB_OUTPUT

  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - name: Report version
        env:
          VERSION: ${{ needs.build.outputs.version }}
        run: printf 'Deploying %s\n' "$VERSION"
```

## Action-Version Audit

Before changing workflow logic, audit every `uses:` reference. Verify the exact release and ref; never derive `vN` from `vN.x.y` and assume the moving major tag exists.

```bash
action="OWNER/REPO"
latest_tag="$(gh api "repos/${action}/releases/latest" --jq '.tag_name')"
latest_sha="$(gh api "repos/${action}/commits/${latest_tag}" --jq '.sha')"
printf "tag=%s sha=%s\n" "${latest_tag}" "${latest_sha}"
```

Decision matrix per finding:

| Pin state | Action |
|---|---|
| SHA-pinned `@<40-character-sha>` | Preserve SHA posture; use the verified release commit and add `# vN.x.y` |
| Exact release tag | Use the verified latest stable tag after compatibility review |
| Moving major tag | Verify `git/ref/tags/vN` exists before use |
| `@main`, `@master`, `@latest`, unpinned, or invented alias | Replace with a verified ref |
| Archived, missing, or prerelease-only | Stop and report; do not silently downgrade or replace |
| Frozen pin | Retain and report the available update |

Read release notes, preserve independently revertible upgrades, run `actionlint`, and let Dependabot or Renovate propose future updates. Follow the GitHub Actions rule (`${HANDBOOK_ROOT}/rules/160-github-actions.mdc`) and dependency currency workflow (`${HANDBOOK_ROOT}/skills/core-engineering/references/dependency-and-toolchain-currency.md`).

## Detailed References

- **Minimum Viable Workflow**: See [references/minimum-viable-workflow.md](references/minimum-viable-workflow.md)
- **Workflow Patterns**: See [references/workflow-patterns.md](references/workflow-patterns.md)
- **Security**: See [references/security.md](references/security.md)
- **Troubleshooting**: See [references/troubleshooting.md](references/troubleshooting.md)
