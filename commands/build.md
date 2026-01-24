---
description: Enter implementation phase - write code following the approved plan
---

# BUILD MODE ACTIVATED

You are now in **IMPLEMENTATION** phase.

## Prerequisites

Before building, confirm:

- [ ] Plan has been approved by user (**HITL / human-in-the-loop**)
- [ ] QA validation passed (for Level 2+ tasks)
- [ ] Creative phase completed (for Level 3-4 tasks)

If no plan exists, suggest running `/plan` first.

## Your Tasks

1. **Follow the Approved Plan**
   - Implement exactly what was discussed
   - Don't add unplanned features
   - Don't refactor unrelated code

2. **Make Incremental Changes**
   - Small, testable commits
   - One logical change at a time
   - Update context files as you progress

3. **Apply Standards**
   - Follow coding standards from rules (100-core.mdc, language-specific rules)
   - Include error handling
   - Add appropriate logging
   - Consider security implications

4. **Stop at Boundaries**
   - Complete the agreed scope, then STOP
   - Don't fix unrelated issues
   - Don't optimize prematurely
   - Note improvements for future work

## Constraints

- Implement ONLY what was planned
- Include error handling and logging
- Follow existing code patterns/conventions
- No TODO comments - complete the implementation
- No placeholders or incomplete sections

## If You Encounter Issues

- **Trivial fixes** (typos, obvious bugs): Fix immediately
- **Substantial changes needed**: STOP, document the issue, discuss before proceeding

## When Done

Say: "Implementation complete. Ready for `/review` when you are."

Summarize:

- What was implemented
- Any deviations from plan (and why)
- Files changed
