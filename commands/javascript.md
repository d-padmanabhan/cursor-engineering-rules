---
description: Generate/modify/review JavaScript using 230-javascript.mdc
---

# JAVASCRIPT MODE ACTIVATED

You are now in **JAVASCRIPT MODE**. Any work on JavaScript MUST follow:

- `rules/230-javascript.mdc` (secure-by-default JS, @ts-check patterns)
- `rules/100-core.mdc` (minimal, production-ready changes)
- `rules/310-security.mdc` (no secrets, OWASP-minded)

Use this command when the user asks to:

- Create new JS modules/functions
- Modify existing JS code
- Review JS code for correctness/security/performance

## Guardrails (mandatory)

- Prefer `async/await`; avoid callbacks unless required.
- Validate external input; avoid injection in templating/queries/commands.
- Avoid adding dependencies unless necessary.
- Don’t log secrets; redact tokens/headers.

## Step 0: Determine intent (create vs modify vs review)

Infer intent from the user’s request. If ambiguous, ask **≤3** clarifying questions (runtime, module system, build tooling, Node/browser target).

## Create

Produce complete code with:

- Clear exports
- Error handling
- JSDoc + `@ts-check` when it improves safety (per `230-javascript.mdc`)

## Modify

- Minimal diffs
- Preserve behavior unless requested
- Keep API compatibility unless requested to break it

## Review

Prioritize:

- **Critical**: injection, SSRF, unsafe `child_process` usage, secrets in logs, auth/authz mistakes
- **Recommended**: performance hotspots, poor error handling, missing input validation
- **Optional**: style/readability

Verification (as applicable):

```bash
pre-commit run --all-files
```

## Done condition

End with:

- Files changed (or “no changes made”)
- How to validate (lint/tests/build) and expected behavior
