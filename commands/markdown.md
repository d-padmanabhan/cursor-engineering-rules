---
description: Write/review Markdown using 800-markdown.mdc and related docs rules
---

# MARKDOWN MODE ACTIVATED

You are now in **MARKDOWN MODE**. Any work on Markdown MUST follow:

- `rules/800-markdown.mdc` (alerts, Mermaid, structure)
- `rules/100-core.mdc` (concise, non-sloppy, useful docs)
- (When relevant) `rules/810-documentation.mdc`

Use this command when the user asks to:

- Write new Markdown docs (README, guides, runbooks)
- Modify existing Markdown
- Review Markdown for structure and clarity

## Guardrails (mandatory)

- Prefer clarity and structure; avoid filler.
- Use GitHub alerts (`[!NOTE]`, `[!TIP]`, etc.) where they add value.
- Use Mermaid for flows/diagrams when it improves understanding.
- Avoid emojis in professional docs unless explicitly requested.

## Step 0: Determine intent (create vs modify vs review)

Infer intent from the user’s request. If ambiguous, ask **≤3** clarifying questions (target audience, required sections, depth).

## Create

Produce Markdown that:

- Has a clear title and logical headings
- Includes ToC when multi-section
- Uses consistent formatting and examples

## Modify

- Minimal diffs
- Preserve existing doc style unless asked to change it

## Review

Prioritize:

- **Critical**: incorrect instructions, unsafe guidance, missing warnings for destructive actions
- **Recommended**: structure, navigation, missing examples, unclear steps
- **Optional**: wording and minor formatting polish

Verification (as applicable):

```bash
pre-commit run --all-files
```

## Done condition

End with:

- Files changed (or “no changes made”)
- How to validate/preview (rendering, lint) and what the doc now supports
