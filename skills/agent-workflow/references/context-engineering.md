# Context Engineering (Prompt Packing, Retrieval, Compaction)

This guide strengthens agent performance by making context **intentional**, **minimal**, and **reproducible**.

It complements:

- `agent-workflow/references/context-management.md` (context files + workflow phases)
- `core-engineering/references/code-review.md` (quality signals and review expectations)

---

## Goals

- Keep working context small and high-signal
- Make work resumable across sessions without reloading everything
- Prefer retrieval over memory: fetch exactly what you need, when you need it

---

## Mental Model: Three Layers of Context

- **Working context (volatile)**: what the model sees right now
- **Repo context (retrievable)**: files, diffs, logs, docs that can be re-read on demand
- **Durable context (portable)**: short summaries + decisions captured in `extras/`

> [!IMPORTANT]
> If it matters later, it must be captured in **durable context**.

---

## Prompt Packing (What to Carry vs. What to Fetch)

### Always carry

- **Goal**: one sentence
- **Non-goals**: 1–3 bullets
- **Constraints**: security, tooling, “don’t refactor”, etc.
- **Current plan**: 3–7 steps max
- **Current state**: what’s done / what’s blocked
- **Critical artifacts**: exact file paths, key identifiers, and error messages (verbatim)

### Never carry (fetch instead)

- Entire files or long logs “just in case”
- Repeated restatements of requirements
- Unbounded command output without a reason

---

## Retrieval Strategy (Search → Read Narrow → Cite)

Use a tight loop:

1. **Search** for the smallest set of candidate files/symbols
2. **Read** only the minimal sections needed to decide or implement
3. **Cite** exact file paths / relevant snippets in reasoning and updates

> [!TIP]
> “Retrieve just-in-time” beats “load everything up-front” for both speed and accuracy.

---

## Compaction Strategy (Frequent Intentional Compaction)

After any meaningful milestone (plan approved, module completed, bug fixed):

- Update `extras/active-context.md` with:
  - Current focus
  - Key decisions (what/why)
  - Blockers (and next action)
  - Context from previous sessions (only what must persist)
- Update `extras/progress.md` (if used) with “done/next”
- Add a **Handoff Bundle** for resuming work cleanly

### Handoff Bundle (copy/paste)

```text
Goal:
Non-goals:
Constraints:
Current state:
Next 3 actions:
Key files/paths:
Key commands + outputs (verbatim, minimal):
```

---

## Context Reset Triggers (Start Fresh on Purpose)

Prefer a fresh session when:

- Plan is approved and you’re moving into implementation
- The conversation has accumulated long tool output or multiple competing threads
- You are switching to a new, independent task

When restarting, bring only:

- The approved plan (or updated `extras/tasks.md`)
- The Handoff Bundle
- The minimal file references needed to continue

---

## Guardrails

- Keep changes minimal and behavior-preserving unless explicitly requested
- Do not paste secrets into context; redact tokens/keys/passwords
- Prefer deterministic artifacts: file paths, commands, exit codes, diffs
