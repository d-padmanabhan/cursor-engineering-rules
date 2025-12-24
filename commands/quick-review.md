---
description: Fast local code review - quick analysis for rapid iteration
---

# QUICK REVIEW MODE ACTIVATED

You are now in **QUICK REVIEW** phase - a streamlined review for rapid iteration cycles.

> [!NOTE]
> For comprehensive analysis, use `/self-review` instead. This command focuses on critical issues only.

## Phase 1: Quick Context

1. **Branch Status:**
   - Current branch (`git branch --show-current`)
   - Files changed (`git diff main...HEAD --name-only | wc -l`)
   - Diff summary (`git diff main...HEAD --stat`)

2. **Recent Commits:**
   - Last 3 commits (`git log --oneline -3 main..HEAD`)

## Phase 2: Critical Checks Only

Run only the most critical checks:

**Python:**

- `ruff check .` (critical errors only)
- `mypy .` or `ty .` (type errors)
- `bandit -r . -ll` (high severity security issues)

**Bash/Shell:**

- `shellcheck` (errors only, no warnings)

**Go:**

- `golangci-lint run --fast` (critical issues)
- `govulncheck ./...` (vulnerabilities)

**JavaScript/TypeScript:**

- `eslint . --max-warnings=0` (errors only)

**Terraform:**

- `terraform validate`
- `tflint` (errors only)

**General:**

- `gitleaks detect --source .` (secrets)

## Phase 3: Critical Issues Only

Analyze `git diff main...HEAD` for:

### Critical Issues (Must Fix)

- **Security:** Hardcoded secrets, injection risks, OWASP Top 10 violations
- **Bugs:** Logic errors, null pointer risks, data loss scenarios
- **Breaking changes:** API modifications without migration path

Skip Recommended/Optional issues for speed.

## Phase 4: Quick Report

```
## Quick Review Summary

**Files Changed:** [count]
**Commits:** [count]

## Critical Issues Found
[File:line] Issue description
- Fix: [Brief suggestion]

## Status
✅ Ready for PR / ⚠️ Critical issues found
```

## Phase 5: Quick Fixes (Optional)

If user requests fixes:

- Apply formatters only (`ruff format`, `gofmt`, `terraform fmt`)
- Re-stage formatted files
- Re-run critical checks

## Constraints

⚠️ **DO NOT:**

- Modify files outside the current diff
- Perform unrelated Git operations
- Commit or push without explicit authorization
- Run comprehensive analysis (use `/self-review` for that)

✅ **DO:**

- Focus on Critical issues only
- Provide quick, actionable feedback
- Skip style/documentation improvements

## After Quick Review

If Critical issues found: Document and wait for user direction.
If clean: Confirm ready for PR.

---

**Use Cases:**

- Pre-commit checks before pushing
- Quick validation during development
- Fast feedback loop for small changes

**For comprehensive analysis:** Use `/self-review` command instead.
