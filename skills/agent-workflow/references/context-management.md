# Context Management & QA Validation

## Context File Management

Context files are workspace-specific and should be in an `extras/` directory:

> [!NOTE]
> For prompt packing, retrieval, and “frequent intentional compaction” patterns, see `agent-workflow/references/context-engineering.md`.

### Project Files

| File | Purpose |
|------|---------|
| `project-brief.md` | Project overview for stable, high-level grounding |
| `tasks.md` | Source of truth for current tasks |
| `active-context.md` | Current focus and working context |
| `progress.md` | Implementation status tracking |
| `reflect-*.md` | Review documents per significant task |
| `creative-*.md` | Design decisions for Level 3-4 tasks |

### Best Practices

1. Always check context files before starting work
2. Update context files as you progress
3. Don't skip phases for complex tasks
4. Preserve context between sessions using files
5. Be explicit about which phase you're in

## PRD-first development (North Star)

For non-trivial work, keep a single “north star” scope document and use it to drive small, sequential feature slices.

- `extras/` is intended for **workspace-local context and artifacts** and should be **gitignored by default**.
- Do **not** commit or push files under `extras/` unless explicitly requested.

- **Recommended file**: `extras/prd.md`
- **Design doc (recommended when architecture/approach matters)**: `extras/design.md`
- **Greenfield**: Define scope, non-goals, key flows, architecture, milestones
- **Brownfield**: Capture current state + next desired state + constraints
- **Rule**: Break work into features small enough for the agent to execute reliably (one feature per cycle)

**When to create `extras/design.md`:**

- Level 3–4 tasks (multi-module or architectural)
- Any time there are multiple valid approaches with meaningful tradeoffs
- Any time interfaces, data models, or operational behaviors might change

## Context reset between Plan → Build

When moving from planning to implementation, prefer a fresh context window so the agent has maximum room to reason.

- **Rule**: After the plan is approved, restart the chat/session before coding
- **Input**: Provide the approved plan doc (and only the minimum extra context needed)
- **Goal**: Keep implementation context lightweight; avoid carrying long planning threads into execution

## System evolution (make the agent better over time)

Treat recurring mistakes as a signal to improve the system, not just the code:

- **If a bug recurs**: update the relevant skill reference(s) so it doesn’t happen again
- **If validation was missed**: update templates/workflow guidance to force the check (tests, lint, security scan)
- **Capture learnings**: record patterns in a `reflect-*.md` doc and keep the guidance crisp

## QA Validation System

**Purpose:** Technical validation to prevent implementation failures.

**When Required:**

- Mandatory before Implementation for Level 2+ tasks
- Can be called explicitly with "QA" command
- After Creative Phase completion (Level 3-4)

### Four-Point Validation Process

#### 1. Dependency Verification

- All required packages/tools installed
- Versions compatible with requirements
- No missing dependencies

#### 2. Configuration Validation

- Configuration files exist and are valid
- Syntax is correct (JSON, YAML, TOML)
- Platform compatibility verified
- Required settings present

#### 3. Environment Validation

- Build tools available
- Permissions sufficient
- Environment variables set
- Required ports available

#### 4. Minimal Build Test

- Build process works
- Core functionality testable
- No blocking errors

### QA Report Format

**Success:**

```
✅ QA VALIDATION STATUS
✓ Dependencies        All required packages installed
✓ Configurations      Format verified for platform
✓ Environment         Suitable for implementation
✓ Build Test          Core functionality verified

✓ VERIFIED - Clear to proceed to Implementation phase
```

**Failure:**

```
❌ QA VALIDATION FAILED

The following issues must be resolved:

1️⃣ DEPENDENCY ISSUES:
- [Description]
- [Recommended fix]

❌ IMPLEMENTATION BLOCKED until resolved.
```

## Creative Phase (Level 3-4 Tasks)

**Mandatory for:**

- Level 3: Complex multi-module features
- Level 4: Architectural changes
- Design decisions affecting multiple components

**Process:**

1. Entry Gate Verification - task complexity confirmed
2. Design Exploration - 2-4 alternatives with pros/cons
3. Exit Gate Verification - all decisions documented
4. Documentation - create `creative-*.md`
5. Proceed to QA Validation

**Implementation Block:**

```
⛔ IMPLEMENTATION BLOCKED
Creative phases MUST be completed before implementation.

Required Creative Phases:
- [ ] [Creative Phase 1]
- [ ] [Creative Phase 2]

🚫 This is a HARD BLOCK
```

## Platform Awareness

**Automatic Detection:**

- Operating system (Windows/macOS/Linux)
- Path separator format (`\` vs `/`)
- Shell environment (PowerShell/Bash/Zsh)

**Command Adaptation:**

- Windows: Use `dir`, `type`, backslash paths
- macOS/Linux: Use `ls`, `cat`, forward slash paths

## Context Management Templates

Use these templates to maintain persistent context across sessions. Create files in `extras/` directory.

> [!TIP]
> If you need a fuller “north star” doc, use `extras/prd.md`. If the task has real design tradeoffs, add `extras/design.md` too.

### tasks.md Template

```markdown
# Tasks & Planning

## Current Task
- **Status:** Not Started
- **Description:**
- **Complexity:** TBD (1-4)
- **Files Affected:**
- **Plan:**
- **Progress:**
- **Notes:**

## Task History

### Completed Tasks
-

### In Progress
-

### Planned
-

---

## Complexity Levels Reference

- **Level 1:** Simple fixes (typos, single-line changes)
- **Level 2:** Single feature/module changes
- **Level 3:** Multi-module changes, significant features
- **Level 4:** Architectural changes, major refactoring

---

## Notes
[Any project-specific notes or context]
```

### active-context.md Template

```markdown
# Active Context

## Current Phase
Not Started

**Phases:**
- Planning: Designing solution, waiting for approval
- Implementing: Actively coding
- Reviewing: Reviewing completed work
- Complete: Task finished

## Current Focus
[What we're working on right now]

## Key Decisions
- [Decision]: [Rationale]

## Blockers/Issues
- [Issue]: [Status/Resolution]

## Context from Previous Sessions
[Any important context that needs to be remembered]

## Handoff Bundle (copy/paste)

Goal:
Non-goals:
Constraints:
Current state:
Next 3 actions:
Key files/paths:
Key commands + outputs (verbatim, minimal):
```

### progress.md Template

```markdown
# Progress Tracking

## Completed
- [Task]: [Date] - [Brief summary]

## In Progress
- [Current task]: [Status update]

## Next Steps
- [Next task 1]
- [Next task 2]

## Blocked/Waiting
- [Blocked task]: [Reason]

---

## Metrics (Optional)
- Tasks completed this week:
- Average task duration:
- Current velocity:
```

### project-brief.md Template

```markdown
# Project Brief

## Purpose
[What this project does, its main goal]

## Tech Stack
- **Languages:**
- **Frameworks:**
- **Infrastructure:**
- **Tools:**

## Architecture Overview
[High-level architecture description]

## Key Patterns & Conventions
- [Pattern 1]: [Description]
- [Pattern 2]: [Description]

## Important Notes
- [Note 1]
- [Note 2]

## Team/Contact
- [Team members or contact info]

## Related Documentation
- [Links to other docs]
```

### creative-template.md Template

```markdown
# Creative: [Component/Feature Name]

**Date:** [Date]
**Task:** [Related task reference]

## Design Challenge
[What design decision needs to be made]

## Options Considered

| Option | Pros | Cons | Complexity | Decision |
|--------|------|------|------------|----------|
| Option A | ... | ... | Low/Med/High | ✅ Chosen / ❌ Rejected |
| Option B | ... | ... | Low/Med/High | ✅ Chosen / ❌ Rejected |
| Option C | ... | ... | Low/Med/High | ✅ Chosen / ❌ Rejected |

## Rationale
[Why the chosen option was selected]

## Trade-offs Accepted
- [Trade-off 1]: [Why it's acceptable]
- [Trade-off 2]: [Why it's acceptable]

## Implementation Notes
[Key considerations for implementing the chosen option]

## References
- [Link to relevant docs/patterns]
- [Related decisions]
```

### reflect-template.md Template

```markdown
# Review: [Task Name]

**Date:** [Date]
**Task:** [Reference to original task]

## What Was Done
[Summary of what was implemented]

## Changes Made
- [Change 1]: [Description]
- [Change 2]: [Description]

## Lessons Learned
- [Lesson 1]: [What we learned]
- [Lesson 2]: [What we learned]

## What Went Well
- [Success 1]
- [Success 2]

## Challenges Encountered
- [Challenge 1]: [How it was resolved]
- [Challenge 2]: [How it was resolved]

## Improvements for Next Time
- [Improvement 1]: [Why it would help]
- [Improvement 2]: [Why it would help]

## Code Quality Notes
- [Quality observation 1]
- [Quality observation 2]

## Security Considerations
- [Security note 1]
- [Security note 2]

## Performance Impact
- [Performance note 1]
- [Performance note 2]

## Follow-up Actions
- [ ] [Action item 1]
- [ ] [Action item 2]
```

## Template Usage Guidelines

1. **Create templates in `extras/` directory** - Keep them workspace-specific
2. **Copy templates when starting new work** - Don't modify originals
3. **Update templates as you progress** - Keep them current
4. **Archive completed work** - Move to `extras/archive/` when done
5. **Use consistent naming** - `tasks.md`, `active-context.md`, `progress.md`, `creative-<feature>.md`, `reflect-<task>.md`

## Common Workflow Violations

### Violation 1: Starting Without Planning

```diff
- BAD: User asks to refactor auth → AI immediately rewrites code
+ GOOD: AI analyzes current system, proposes options, waits for approval
```

### Violation 2: Adding Unplanned Features

```diff
- BAD: User asks for search bar → AI adds autocomplete, history, filters
+ GOOD: AI adds only basic search bar, suggests enhancements for next phase
```

### Violation 3: Not Stopping at Agreed Scope

```diff
- BAD: User asks to fix button → AI refactors entire CSS
+ GOOD: AI fixes only the button, notes other issues for discussion
```
