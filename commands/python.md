---
description: Generate/modify/review Python code using 200-python.mdc
---

# PYTHON MODE ACTIVATED

You are now in **PYTHON MODE**. Any work on Python code MUST follow:

- `rules/200-python.mdc` (opinionated Python guidance)
- `rules/100-core.mdc` (minimal, production-ready changes)
- `rules/310-security.mdc` (no secrets, OWASP-minded)

Use this command when the user asks to:

- Create new Python modules/functions/classes
- Modify existing Python code
- Review Python code for correctness/security/performance

## Guardrails (mandatory)

- Prefer stdlib over new dependencies unless explicitly justified.
- Validate inputs and fail fast with clear errors.
- Don’t log secrets (mask sensitive fields).
- Keep changes minimal; don’t refactor unrelated code.

## Step 0: Determine intent (create vs modify vs review)

Infer intent from the user’s request. If ambiguous, ask **≤3** clarifying questions (runtime version, interface expectations, performance constraints).

## Create

Produce complete, runnable code with:

- Type hints
- Clear docstrings where appropriate
- Error handling for expected failures

## Modify

- Preserve existing behavior unless requested otherwise
- Prefer minimal diffs
- Add tests only if requested (or if needed to prevent regression)

## Review

Prioritize:

- **Critical**: injection risks, insecure subprocess usage, secret leakage, broken authz, unsafe deserialization
- **Recommended**: performance hot spots, poor error handling, observability gaps
- **Optional**: style and small readability tweaks

Verification (as applicable):

```bash
pre-commit run --all-files
```

## Done condition

End with:

- Files changed (or “no changes made”)
- How to validate (tests/lint/type-check) and expected behavior
