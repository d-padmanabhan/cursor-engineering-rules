---
description: Archive completed task - document lessons learned and update knowledge base
---

# ARCHIVE MODE ACTIVATED

You are now in **ARCHIVE** phase.

## Purpose

Document the completed task, capture lessons learned, and update the knowledge base for future reference.

## When to Use

- After `/review` phase for Level 3-4 tasks
- When significant learnings should be preserved
- After completing a multi-session task
- When patterns emerged that should be documented

## Your Tasks

1. **Summarize What Was Done**
   - What was the original request?
   - What was actually implemented?
   - Were there any deviations from the plan? Why?

2. **Document Key Decisions**
   - What design decisions were made?
   - What alternatives were considered?
   - Why were certain approaches chosen?

3. **Capture Lessons Learned**
   - What went well?
   - What was challenging?
   - What would you do differently?
   - Any gotchas or surprises?

4. **Update Context Files**
   - Update `tmp/progress.md` with completion status
   - Create `tmp/reflect-<task>.md` if significant learnings
   - Update `tmp/tasks.md` to mark task complete

5. **Identify Reusable Patterns**
   - Any patterns that should be standardized?
   - Code that could become a utility?
   - Documentation that should be added?

## Output Format

```markdown
## Task Archive: [Task Name]

### Summary
- **Original Request:** [what was asked]
- **Completed:** [date]
- **Duration:** [time spent]
- **Complexity:** Level [1-4]

### What Was Implemented
- [Key change 1]
- [Key change 2]
- [Key change 3]

### Files Changed
- `path/to/file1.py` - [what changed]
- `path/to/file2.py` - [what changed]

### Key Decisions
| Decision | Options Considered | Choice | Rationale |
|----------|-------------------|--------|-----------|
| [Decision 1] | A, B, C | B | [why] |
| [Decision 2] | X, Y | X | [why] |

### Lessons Learned

**What Went Well:**
- [positive 1]
- [positive 2]

**Challenges:**
- [challenge 1] - [how resolved]
- [challenge 2] - [how resolved]

**For Next Time:**
- [improvement 1]
- [improvement 2]

### Reusable Patterns
- [Pattern that could be extracted]
- [Utility that could be created]

### Related Tasks
- [Link to related future work]
- [Technical debt to address]
```

## Archive Location

Save archives to:

- `tmp/reflect-<task-name>.md` - For significant tasks
- Or update `tmp/progress.md` - For simpler summaries

## Skip When

- Level 1 tasks (quick fixes)
- No significant learnings to capture
- Task was straightforward with no surprises
