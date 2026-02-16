---
description: Initialize task - analyze project, detect complexity, set up context
---

# INITIALIZATION MODE ACTIVATED

You are now in **INIT** (initialization) phase.

## Purpose

Initialize a new task by analyzing the project and determining the appropriate workflow.

## Your Tasks

1. **Analyze the Project**
   - Scan project structure
   - Identify tech stack and patterns
   - Note existing conventions
   - Check for existing context files (`tmp/prd.md`, `tmp/design.md`, `tmp/project-brief.md`, `tmp/tasks.md`, `tmp/active-context.md`)

2. **Understand the Request**
   - What is the user asking for?
   - What is the scope?
   - Are there ambiguities to clarify?

3. **Determine Complexity Level**

   | Level | Type | Characteristics | Workflow |
   |-------|------|-----------------|----------|
   | 1 | Quick Fix | Single file, obvious change, < 30 min | `/build` -> `/review` |
   | 2 | Simple Task | Few files, clear scope, < 2 hours | `/plan` -> `/qa` -> `/build` -> `/review` |
   | 3 | Feature | Multiple files, design decisions needed | `/plan` -> `/creative` -> `/qa` -> `/build` -> `/review` |
   | 4 | Complex | Architectural, cross-cutting, multi-day | `/plan` -> `/creative` -> `/qa` -> `/build` -> `/review` -> `/archive` |

4. **Set Up Context**
   - Create/update `tmp/tasks.md` if needed
   - Create/update `tmp/active-context.md` if needed
   - Note any existing progress

5. **Route to Next Command**
   - Level 1: Recommend `/build`
   - Level 2-4: Recommend `/plan`

## Output Format

```markdown
## Task Initialization

### Project Analysis
- **Tech Stack:** [languages, frameworks]
- **Structure:** [monorepo, single app, etc.]
- **Conventions:** [patterns observed]

### Request Understanding
- **Task:** [what user wants]
- **Scope:** [files/modules affected]
- **Ambiguities:** [questions if any]

### Complexity Assessment

**Level: [1-4]**

**Reasoning:**
- [Why this level]
- [Key factors]

### Recommended Workflow
```

[workflow path, e.g., /plan -> /creative -> /qa -> /build -> /review]

```

### Next Step
Run `/plan` to begin planning (or `/build` for Level 1 tasks).
```

## When to Skip

For trivial tasks (typo fixes, obvious one-liners), you can skip `/van` and go directly to `/build`.
