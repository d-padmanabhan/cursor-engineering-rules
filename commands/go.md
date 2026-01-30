---
description: Generate/modify/review Go code using 210-go.mdc
---

# GO MODE ACTIVATED

You are now in **GO MODE**. Any work on Go code MUST follow:

- `rules/210-go.mdc` (idiomatic, secure Go)
- `rules/100-core.mdc` (minimal, production-ready changes)
- `rules/310-security.mdc` (no secrets, OWASP-minded)

Use this command when the user asks to:

- Create new Go packages/types/functions
- Modify existing Go code
- Review Go code for correctness/security/performance

## Guardrails (mandatory)

- Handle all errors explicitly.
- Keep interfaces small; prefer dependency injection where it improves testability.
- Avoid logging secrets; redact tokens/headers.
- Minimal diffs; no unrelated refactors.

## Step 0: Determine intent (create vs modify vs review)

Infer intent from the user’s request. If ambiguous, ask **≤3** clarifying questions (Go version, package boundaries, API expectations).

## Create

Produce complete, buildable code with:

- Clear package structure
- Context-aware APIs where appropriate (`context.Context`)
- Meaningful errors (`fmt.Errorf("...: %w", err)`)

## Modify

- Preserve behavior unless requested otherwise
- Prefer minimal diffs
- Update tests only if needed/asked

## Review

Prioritize:

- **Critical**: error handling omissions, unsafe concurrency, insecure network defaults, injection/SSRF patterns
- **Recommended**: allocations/perf hot spots, poor cancellation/timeouts, observability gaps
- **Optional**: style and minor simplifications

Verification (as applicable):

```bash
gofmt -w .
go test ./...
pre-commit run --all-files
```

## Done condition

End with:

- Files changed (or “no changes made”)
- How to validate (build/test/lint) and expected behavior
