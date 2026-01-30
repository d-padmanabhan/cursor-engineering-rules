---
description: Generate/modify/review GitHub Actions workflows using 160-github-actions.mdc
---

# GITHUB ACTIONS MODE ACTIVATED

You are now in **GITHUB ACTIONS MODE**. Any work on GitHub Actions MUST follow:

- `rules/160-github-actions.mdc` (secure, least-privilege workflows)
- `rules/100-core.mdc` (minimal, maintainable changes)
- `rules/310-security.mdc` (no secrets, supply-chain aware)

Use this command when the user asks to:

- Create a new workflow under `.github/workflows/`
- Modify an existing workflow
- Review a workflow for security/correctness

## Guardrails (mandatory)

- **Least privilege**: prefer job-level `permissions:` with minimal scopes.
- **No secrets in code**: never paste tokens/keys; reference `${{ secrets.* }}` only.
- **Pin actions safely**: use stable major tags (e.g., `actions/checkout@v4`) unless policy requires SHA pinning.
- **Avoid remote writes** unless explicitly requested (PR creation/merge, releases, etc.).

## Step 0: Determine intent (create vs modify vs review)

Infer intent from the user’s request. If ambiguous, ask **≤3** clarifying questions (trigger events, required permissions, target runners, required secrets/vars).

## Create

Produce a complete workflow that is:

- Minimal and readable
- Uses least-privilege permissions
- Uses caches only when justified
- Has clear job names, step names, and failure modes

## Modify

- Keep changes localized to the requested behavior
- Preserve existing triggers and permissions unless the user asked to change them
- Prefer tightening permissions over broadening

## Review

Prioritize:

- **Critical**: overbroad permissions, untrusted `pull_request_target` misuse, secrets exposure, unsafe checkout of PR code with secrets, running arbitrary scripts from forks
- **Recommended**: caching correctness, pinned tool versions, concurrency controls
- **Optional**: readability and naming

Verification (as applicable):

```bash
pre-commit run --all-files
```

## Done condition

End with:

- Files changed (or “no changes made”)
- How to validate (lint/checks) and expected workflow behavior
