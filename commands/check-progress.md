---
description: Fix issues, summarize progress, run pre-commit, propose commit message (no staging/commit)
---

# CHECK PROGRESS MODE ACTIVATED

Review current work progress without staging or committing. Fix issues, run quality checks, and propose commit messages following `100-core.mdc` and `110-git.mdc` standards.

> [!IMPORTANT]
> **Fix mode.** Fix errors and formatting issues, then report what was fixed.
>
> No staging, committing, or pushing will be performed.

## Phase 1: Change Detection

1. **Identify Modified Files:**
   - Show staged changes (`git diff --cached --name-only`)
   - Show unstaged changes (`git diff --name-only`)
   - Ignore files/folders listed in `.gitignore`
   - Count files by type (Python, Bash, Go, JS/TS, Terraform, etc.)

2. **Branch Context:**
   - Current branch name (`git branch --show-current`)
   - Extract Jira ticket from branch name (if present, e.g., `feat/OCFN-1443-fix-auth`)
   - Commits ahead of base (`git log --oneline main..HEAD`)

## Phase 2: Quality Checks

Run appropriate formatters and linters based on **modified files only**.

> [!IMPORTANT]
> Do not stage anything. Do not run commands that modify the git index.

### Python Files

Fix, then validate:

- `ruff format <files>` (format)
- `ruff check <files> --fix` (lint autofix where safe)
- `black <files>` (format, if used in repo)
- `isort <files>` (imports, if used in repo)
- `mypy <files>` or `ty <files>` (type checking)
- `pylint <files>` (aim for score ≥9.0, prefer ≥9.5)
- `bandit -r <files> -ll` (security scanning - high/low severity)

### Bash/Shell Files

Fix, then validate:

- `shfmt -w -i 2 -ci -sr -bn <files>` (format)
- `shellcheck <files>` (lint)

### Go Files

Fix, then validate:

- `gofmt -w -s <files>` (format)
- `go vet ./...`
- `staticcheck ./...`
- `golangci-lint run ./...`
- `govulncheck ./...`

### JavaScript/TypeScript Files

Fix, then validate:

- `eslint <files> --fix` (if configured)
- `eslint <files> --max-warnings=0`
- `tsc --noEmit` (if TypeScript)
- `npm audit` (if `package.json` exists)

### Terraform Files

Fix, then validate:

- `terraform fmt -recursive`
- `terraform validate`
- `tflint`

### General Checks

- `gitleaks detect --source .` (secrets scanning)
- `pre-commit autoupdate && pre-commit run --all-files` (if `.pre-commit-config.yaml` exists)

> [!NOTE]
> If pre-commit hooks fail, fix what you can and re-run. Block progress only for Critical security issues or correctness bugs.

## Phase 3: Change Analysis

Review `git diff` (staged + unstaged) and categorize findings using Priority Framework from `100-core.mdc`:

### Critical Issues (Must Fix Before Commit)

- **Security vulnerabilities:** Hardcoded secrets, injection risks, OWASP Top 10 violations
- **Bugs:** Logic errors, null pointer risks, data loss scenarios
- **Breaking changes:** API modifications without migration path

### Recommended Improvements

- **Performance:** Inefficient algorithms, N+1 queries, missing caching
- **Maintainability:** Code duplication, unclear naming, missing error handling
- **Type safety:** Missing type hints, `Any` types, untyped functions

### Optional Enhancements

- **Style:** Formatting inconsistencies, minor naming improvements
- **Documentation:** Missing docstrings, unclear comments

## Phase 4: Change Summary

Provide a structured summary:

```markdown
## Change Summary

### Files Modified
- [Count] Python files
- [Count] Bash files
- [Count] Other files

### Intent & Changes
[Clear explanation of what changed and why, grouped by logical changes]

### Quality Check Results
- **Linters:** [Pass/Fail with key issues]
- **Formatters:** [Pass/Fail]
- **Type Checkers:** [Pass/Fail]
- **Security Scanners:** [Pass/Fail]
- **Pylint Score:** [X.XX/10] (target: ≥9.5)

### Issues Found
**Critical:**
- [File:line] Issue description

**Recommended:**
- [File:line] Issue description

**Optional:**
- [File:line] Issue description
```

## Phase 5: Commit Message Proposal

**Only if no Critical issues found after fixes:**

Propose **one primary commit message** following `110-git.mdc` format:

```
<type>(<scope>): <short summary>

- <change 1>
- <change 2>
- <change 3>

<optional explanatory paragraph>
```

**Requirements:**

- First line ≤72 chars, imperative mood
- Include Jira ticket in scope if present in branch name (e.g., `feat(OCFN-1443): ...`)
- Bullets start with capital letter, no period
- Add rationale paragraph if change is non-obvious

**If Critical issues found:**

- **Do NOT propose commit messages**
- List Critical issues clearly with file/line references
- Recommend fixing Critical issues before committing

**Optionally provide 1-2 alternative commit messages** if multiple valid interpretations exist.

## Phase 6: Task Management

1. Create or update `<repo-root>/tmp/TODO.md` with:
   - Remaining tasks
   - Edge cases
   - Follow-ups and future improvements

2. Ensure `tmp/` is present in `.gitignore`. Add it if missing.

## Constraints

⚠️ **DO NOT:**

- Stage files (`git add`)
- Commit changes (`git commit`)
- Push to remote (`git push`)
- Run commands that would stage or commit

✅ **DO:**

- Analyze only modified files
- Fix errors and formatting issues on changed code
- Re-run checks after fixes
- Provide actionable feedback
- Follow Priority Framework (Critical → Recommended → Optional)
- Use Conventional Commits format
- Extract Jira ticket from branch name for commit scope

## Output Format

```markdown
## Work Progress Review

### Change Detection
[Summary of modified files and branch context]

### Quality Checks
[Results of all applicable linters/formatters]

### Change Analysis
[Structured summary with Priority Framework categorization]

### Commit Message Proposal
[Primary message + alternatives, or Critical issues list]

### Next Steps
- [ ] Fix Critical issues (if any)
- [ ] Apply formatters if needed
- [ ] Review and approve commit message
- [ ] Stage and commit when ready
```

## After Review

- **If Critical issues found:** Document clearly, recommend fixes before committing
- **If only Recommended/Optional issues:** Summarize, user can decide to fix or proceed
- **If clean:** Propose commit message, user can stage/commit when ready

**Optional: CodeRabbit Integration**

If CodeRabbit is available and configured:

- CodeRabbit can provide automated PR reviews after local validation
- Use as secondary layer for team consistency across PRs
- Always complete local review first for audit compliance
- CodeRabbit complements but does not replace local review commands

---

**Integration:** This workflow aligns with:

- `100-core.mdc` Coding standards and Priority Framework
- `110-git.mdc` Commit message standards
- `050-workflow.mdc` Review phase patterns
- Tooling baseline for all supported languages
