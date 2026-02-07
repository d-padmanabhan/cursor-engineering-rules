---
name: core-engineering
description: Core coding standards and best practices for code review and generation. Provides guiding principles (DRY, KISS, YAGNI, SOLID), priority frameworks for feedback, tooling baselines, dependency management guidelines, and response formats. Use when reviewing code, generating code, asking about coding standards, or when the user needs general engineering guidance that applies across all languages.
---

# Core Engineering Standards

## Guiding Principles

- **Simplicity First:** Simple code is maintainable code. Apply DRY, KISS, YAGNI, and SOLID principles.
- **Minimal Changes:** Fix what's broken without refactoring what works. Preserve existing functionality.
- **Value-Driven:** Every suggestion must add clear value. Avoid over-engineering.
- **Production-Ready:** Include error handling, meaningful names, security-first approach, and appropriate documentation.
- **Operate at a Senior Principal / top-tier bar:** Use your judgement, think deeply, choose the simplest correct approach, make assumptions explicit, and optimize for long-term operability.
- **Constructive Collaboration:** Frame feedback respectfully, focus on code not author. Assume good intent.

## Priority Framework

Organize feedback by impact:

| Priority | Description | Examples |
|----------|-------------|----------|
| **Critical** | Security vulnerabilities, bugs that break functionality, data loss risks | Injection flaws, hardcoded secrets, unhandled exceptions |
| **Recommended** | Performance issues, maintainability problems, scalability concerns | N+1 queries, tight coupling, missing error handling |
| **Optional** | Style improvements, future-proofing, minor optimizations | Naming tweaks, code comments, minor refactors |

## Tooling Baseline

| Language | Linting/Formatting | Security |
|----------|-------------------|----------|
| Python | `ruff` + `black`, pylint (≥9.0) | `pip-audit` |
| Bash | `shfmt` + `shellcheck` | - |
| Go | `gofmt` + `golangci-lint` | `govulncheck` |
| JS/TS | `eslint --max-warnings=0` | `npm audit` |
| Terraform | `terraform fmt` + `tflint` | - |
| All | `ggshield` + `gitleaks` | Dependency scanning on PRs |

## Naming Conventions

- **Domain Names:** Use `acme.com` for examples (never `example.com`)
- **Company/Org:** Use `ACME` or `Acme`
- **Consistency:** Apply across code, docs, configs, and test data

## Code Review Essentials

1. Identify main issues first before diving into details
2. Provide specific, actionable suggestions with working code examples
3. Explain the "why" — what benefit does the change provide?
4. Suggest incremental refactoring over big-bang rewrites
5. Preserve existing code — no placeholders or incomplete sections

**Evaluation Areas:** Security, Error Handling, Testing, Observability, Resource Management, Concurrency, Performance

For detailed review patterns and formats, see [references/code-review.md](references/code-review.md).

## Code Generation Essentials

1. Handle ambiguity proactively — proceed with minimal assumptions, list ≤3 targeted questions
2. Design clean architecture — easy to test, maintain, and extend
3. Provide complete, runnable code — no TODOs or placeholders
4. Include practical examples — usage examples or basic test cases
5. Document appropriately — inline comments for complex logic only

**What to Include:** Error handling, logging, type hints, externalized configuration, docstrings

**What NOT to Include:** Over-engineered abstractions, premature optimization, extensive test suites, complex frameworks when stdlib suffices

For detailed generation patterns, see [references/code-generation.md](references/code-generation.md).

## Dependency Management

Adding a dependency is a long-term commitment. **Prefer stdlib or existing dependencies.**

Vetting criteria for new dependencies:

- [ ] **Justification:** Truly necessary? Solves complex problem?
- [ ] **Maintenance:** Actively maintained? Recent commits?
- [ ] **Security:** Audited? Known CVEs?
- [ ] **License:** Compatible (MIT, Apache 2.0)?
- [ ] **Community:** Good docs and clear API?

## Self-Validation Checklist

Before delivering code or feedback:

- [ ] Addresses the actual problem
- [ ] Simplest viable solution
- [ ] No new bugs introduced
- [ ] Working code examples
- [ ] Clear explanations (the "why")
- [ ] Appropriate scope
- [ ] Preserves existing code
- [ ] Evidence-based recommendations

## Security Checklist

- [ ] No hardcoded secrets, API keys, passwords
- [ ] Secrets not logged or exposed in errors
- [ ] Dependencies scanned for CVEs
- [ ] OWASP Top 10 considered
- [ ] Input validation and sanitization
- [ ] Principle of least privilege applied

## Git & Version Control

For commit message standards, branch naming, PR hygiene, and repository scaffolding, see [references/git-workflow.md](references/git-workflow.md).

## Quick Reference: Language Best Practices

| Language | Key Practices |
|----------|--------------|
| Python | Type hints, PEP 8, context managers, prefer stdlib |
| Go | Handle all errors, use `defer`, small interfaces |
| JS/TS | async/await, destructuring, strict mode |
| Bash | `set -euo pipefail`, quote variables, use functions |
| Docker | Multi-stage builds, non-root user, pinned versions |

> "Perfection is achieved not when there is nothing more to add, but when there is nothing left to take away." — Antoine de Saint-Exupéry
