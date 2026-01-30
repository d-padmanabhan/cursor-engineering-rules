---
description: Generate/modify/review Bash scripts using 140-bash.mdc
---

# BASH MODE ACTIVATED

You are now in **BASH MODE**. Any work on Bash scripts MUST follow:

- `rules/140-bash.mdc` (Bash Engineering Ruleset)
- `rules/100-core.mdc` (minimal, secure, production-ready)
- `rules/310-security.mdc` (no secrets, OWASP-minded)

This command is used when the user asks Cursor to:

- Generate a **new** Bash script
- Modify an **existing** Bash script
- Review an **existing** Bash script

## Guardrails (mandatory)

- **No secrets**: never add tokens/keys/passwords to scripts or examples.
- **Quoting**: quote variables and paths (`"${var}"`), unless word splitting is explicitly intended.
- **No `eval`** with user input.
- **No parsing `ls` output**.
- **Safe temp files**: prefer `mktemp` + `trap` cleanup.
- **Network calls**: if using `curl`, apply the `140-bash.mdc` “Curl in scripts” baseline (timeouts + retries).
- **Examples**: use `acme.com` domains for examples.

## Step 0: Determine intent (create vs modify vs review)

Infer intent from the user’s request. If ambiguous, ask **≤3** clarifying questions that materially change the implementation (e.g., target OS, required inputs/outputs, whether retries are expected).

## Create: generate a new script

Produce a complete, runnable script (no TODO stubs) with:

- Shebang: `#!/usr/bin/env bash` (default)
- Safety mode: choose and justify `set -euo pipefail` vs `set -uo pipefail`
- `main()` entrypoint + `usage()` (when args are non-trivial)
- Dependency checks: `command -v`
- Logging helper (UTC timestamps) to stderr
- Structured error handling (traps) when warranted
- `shellcheck`-clean, `shfmt`-formatted output

If the script talks to an HTTP API:

- Use the `curl` baseline options pattern from `rules/140-bash.mdc`
- Do not log auth headers/tokens

## Modify: change an existing script

Follow “minimal diff” discipline:

- Preserve behavior unless the user asked to change it
- Don’t refactor unrelated parts
- Keep changes localized and reversible
- If changing error-handling mode, explain why

Before editing:

- Read the target script fully (or the relevant functions/sections)
- Identify the smallest safe change set

After editing:

- Ensure formatting and lint expectations remain satisfied

## Review: review an existing script

Provide a structured review using the priority framework:

- **Critical**: security issues, data loss risks, unsafe quoting, `eval`, unsafe temp files, missing timeouts for curl, dangerous `rm` patterns
- **Recommended**: maintainability, logging/observability, portability issues (macOS Bash 3.2), error handling clarity
- **Optional**: style and minor ergonomics

Include a verification command list (as applicable):

```bash
shellcheck path/to/script.sh
shfmt -d -i 2 -ci -sr -bn path/to/script.sh
```

## Done condition

End with:

- Files changed (or “no changes made”)
- How to validate (`shellcheck`, `shfmt`, and any runtime smoke test)
