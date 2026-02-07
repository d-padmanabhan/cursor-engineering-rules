# Workflow Patterns

## Pull Request Workflow

```yaml
name: PR Check

on:
  pull_request:
    branches: [main]

permissions:
  contents: read
  pull-requests: write

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
      - run: npm ci
      - run: npm run lint

  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
      - run: npm ci
      - run: npm test -- --coverage
      - uses: actions/upload-artifact@v4
        with:
          name: coverage
          path: coverage/
```

## Release Workflow

```yaml
name: Release

on:
  push:
    tags:
      - 'v*'

permissions:
  contents: write
  packages: write

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          registry-url: 'https://registry.npmjs.org'
      
      - run: npm ci
      - run: npm run build
      - run: npm publish
        env:
          NODE_AUTH_TOKEN: ${{ secrets.NPM_TOKEN }}
      
      - uses: softprops/action-gh-release@v1
        with:
          generate_release_notes: true
```

## Docker Build and Push

```yaml
name: Docker

on:
  push:
    branches: [main]
    tags: ['v*']

permissions:
  contents: read
  packages: write

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - uses: docker/setup-buildx-action@v3
      
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      - uses: docker/metadata-action@v5
        id: meta
        with:
          images: ghcr.io/${{ github.repository }}
          tags: |
            type=ref,event=branch
            type=semver,pattern={{version}}
      
      - uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

## Scheduled Workflow

```yaml
name: Scheduled Tasks

on:
  schedule:
    - cron: '0 0 * * *'  # Daily at midnight UTC
  workflow_dispatch:  # Manual trigger

jobs:
  cleanup:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: ./scripts/cleanup.sh
```

## Environment Deployments

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  staging:
    runs-on: ubuntu-latest
    environment: staging
    steps:
      - uses: actions/checkout@v4
      - run: ./deploy.sh staging

  production:
    needs: staging
    runs-on: ubuntu-latest
    environment:
      name: production
      url: https://app.acme.com
    steps:
      - uses: actions/checkout@v4
      - run: ./deploy.sh production
```

## Path Filters

```yaml
on:
  push:
    branches: [main]
    paths:
      - 'src/**'
      - 'package.json'
      - '.github/workflows/ci.yml'
    paths-ignore:
      - '**.md'
      - 'docs/**'
```

## Conditional Steps

```yaml
steps:
  - name: Only on main
    if: github.ref == 'refs/heads/main'
    run: echo "On main branch"

  - name: Only on tags
    if: startsWith(github.ref, 'refs/tags/')
    run: echo "On tag"

  - name: Only on failure
    if: failure()
    run: echo "Previous step failed"
```

## Common Anti-Patterns

### Hardcoding Runner OS Commands

```yaml
# ❌ Fragile - Breaks on Windows/macOS
- run: rm -rf dist/

# ✅ Portable - Use actions or shell-agnostic commands
- run: |
    if [ -d dist ]; then rm -rf dist; fi
  shell: bash
```

### Not Cleaning Up Artifacts

```yaml
# ❌ Artifacts kept for 90 days (GitHub default)
- uses: actions/upload-artifact@v4
  with:
    name: logs

# ✅ Set appropriate retention
- uses: actions/upload-artifact@v4
  with:
    name: logs
    retention-days: 7  # Adjust based on needs
```

### Missing Timeout Protection

```yaml
# ❌ Can run for 6 hours (GitHub default)
jobs:
  build:
    runs-on: ubuntu-latest

# ✅ Set reasonable timeout
jobs:
  build:
    runs-on: ubuntu-latest
    timeout-minutes: 30
```

## Dynamic Input Choices

Use `workflow_dispatch` with choice inputs for better UX:

```yaml
on:
  workflow_dispatch:
    inputs:
      environment:
        description: 'Target environment'
        type: choice
        options:
          - development
          - staging
          - production
      log-level:
        description: 'Log level'
        type: choice
        options:
          - debug
          - info
          - warning
          - error
        default: 'info'
      dry-run:
        description: 'Dry run mode'
        type: boolean
        default: false

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Deploy
        run: |
          echo "Deploying to ${{ inputs.environment }}"
          echo "Log level: ${{ inputs.log-level }}"
          echo "Dry run: ${{ inputs.dry-run }}"
```
