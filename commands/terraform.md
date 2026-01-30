---
description: Generate/modify/review Terraform using 180-terraform.mdc
---

# TERRAFORM MODE ACTIVATED

You are now in **TERRAFORM MODE**. Any work on Terraform MUST follow:

- `rules/180-terraform.mdc` (module structure, validation, security)
- `rules/100-core.mdc` (minimal, maintainable changes)
- `rules/310-security.mdc` (no secrets, least privilege)

Use this command when the user asks to:

- Create a new Terraform module
- Modify existing `.tf` code
- Review Terraform for correctness/security

## Guardrails (mandatory)

- Use `snake_case` for variables/outputs/resources.
- Prefer modules and clear inputs/outputs; avoid hardcoding.
- Never commit state files, plan artifacts, or secrets.
- Keep changes minimal and scoped.

## Step 0: Determine intent (create vs modify vs review)

Infer intent from the user’s request. If ambiguous, ask **≤3** clarifying questions (target provider, environment, module boundaries).

## Create

Produce module-shaped output:

- `main.tf`, `variables.tf`, `outputs.tf`, `README.md` (+ `examples/` when appropriate)
- Include validation blocks for inputs where helpful

## Modify

- Prefer minimal diffs
- Preserve module interface unless explicitly asked to change it

## Review

Prioritize:

- **Critical**: secrets in variables, overly-permissive IAM, public access exposure, missing encryption, unsafe defaults
- **Recommended**: missing validation/docs, inconsistent naming, missing tags/labels
- **Optional**: style and readability

Verification (as applicable):

```bash
terraform fmt -check -recursive
terraform validate
pre-commit run --all-files
```

## Done condition

End with:

- Files changed (or “no changes made”)
- How to validate (fmt/validate/lint) and expected behavior
