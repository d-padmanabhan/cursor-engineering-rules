# GitHub Actions Troubleshooting

## Common Issues

### Permissions Denied

```yaml
# Issue: Resource not accessible by integration
# Solution: Add required permissions
permissions:
  contents: read
  pull-requests: write
```

### Cache Not Restoring

```yaml
# Check cache key matches exactly
- uses: actions/cache@v4
  with:
    path: ~/.npm
    key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}
    # Add restore-keys for partial matches
    restore-keys: |
      ${{ runner.os }}-node-
```

### Secrets Not Available

```yaml
# Secrets not available in:
# - fork PRs (security)
# - workflow_dispatch from forks
# - scheduled runs without proper context

# Solution: Use environment secrets
jobs:
  deploy:
    environment: production
    steps:
      - run: echo ${{ secrets.PROD_KEY }}
```

## Debugging

### Enable Debug Logging

```yaml
# Repository secret
ACTIONS_STEP_DEBUG: true
ACTIONS_RUNNER_DEBUG: true

# Or in workflow
- run: echo "Debug info"
  env:
    ACTIONS_STEP_DEBUG: true
```

### Print Context

```yaml
- name: Dump context
  run: |
    echo "Event: ${{ github.event_name }}"
    echo "Ref: ${{ github.ref }}"
    echo "SHA: ${{ github.sha }}"
    echo "Actor: ${{ github.actor }}"
    echo "::group::GitHub Context"
    echo '${{ toJSON(github) }}'
    echo "::endgroup::"
```

### SSH Debug Session

```yaml
- name: Setup tmate session
  if: failure()
  uses: mxschmitt/action-tmate@v3
  timeout-minutes: 15
```

## Performance

### Slow Checkout

```yaml
# Use shallow clone
- uses: actions/checkout@v4
  with:
    fetch-depth: 1
```

### Large Artifacts

```yaml
# Compress before upload
- run: tar -czf build.tar.gz dist/
- uses: actions/upload-artifact@v4
  with:
    name: build
    path: build.tar.gz
    compression-level: 0  # Already compressed
```

### Parallel Jobs

```yaml
jobs:
  test:
    strategy:
      matrix:
        shard: [1, 2, 3, 4]
    steps:
      - run: npm test -- --shard=${{ matrix.shard }}/4
```

## Error Handling

### Continue on Error

```yaml
- name: Non-critical step
  continue-on-error: true
  run: ./optional-check.sh

- name: Check result
  if: steps.previous.outcome == 'failure'
  run: echo "Previous step failed but continuing"
```

### Retry Logic

```yaml
- name: Retry on failure
  uses: nick-fields/retry@v2
  with:
    timeout_minutes: 10
    max_attempts: 3
    command: npm test
```

### Timeout

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    timeout-minutes: 30
    steps:
      - name: Long step
        timeout-minutes: 10
        run: ./long-running.sh
```

## Common Gotchas

1. **`pull_request_target`**: Has write access, dangerous for forks
2. **Expression syntax**: `${{ }}` vs `${ }` in shell
3. **Multiline strings**: Use `|` for run commands
4. **Environment variables**: Quote values with special chars
5. **Path context**: `working-directory` doesn't affect `uses`

```yaml
# Correct multiline
- run: |
    echo "Line 1"
    echo "Line 2"

# Correct quoting
- run: |
    echo "Value: ${{ env.MY_VAR }}"
```
