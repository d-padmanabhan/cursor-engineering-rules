---
description: Enter planning phase - analyze, design, and document approach before implementation
---

# PLANNING MODE ACTIVATED

You are now in **PLANNING** phase. Do NOT write code yet.

## Your Tasks

1. **Analyze the Request**
   - Understand scope, constraints, and requirements
   - Identify what's essential vs nice-to-have
   - Note any ambiguities

2. **Check Existing Code**
   - Look for patterns, conventions, and reusable components
   - Understand the current architecture
   - Identify files/modules that will be affected

3. **Design the Solution**
   - Propose approach with rationale
   - Consider 2-3 alternatives with pros/cons
   - Identify dependencies and risks
   - Plan testing strategy

4. **Document the Plan**
   - Update `tasks.md` or `active-context.md` if they exist
   - List files to be modified
   - Outline implementation steps

5. **Present and WAIT**
   - Show the plan clearly
   - Ask for explicit approval before proceeding (**HITL / human-in-the-loop**)
   - Answer any clarifying questions

## Output Format

```markdown
## Plan: [Brief Title]

### Problem
[What we're solving]

### Proposed Solution
[Your approach]

### Alternatives Considered
1. [Alternative 1] - [Why not chosen]
2. [Alternative 2] - [Why not chosen]

### Files Affected
- `path/to/file1.py` - [What changes]
- `path/to/file2.py` - [What changes]

### Implementation Steps
1. [Step 1]
2. [Step 2]
3. [Step 3]

### Risks
- [Risk 1]
- [Risk 2]

### Testing Strategy
- [How to test]
```

## Rules

- Ask max 3 clarifying questions if scope is ambiguous
- Do NOT start coding until user approves
- Keep plans concise but complete
- Consider security implications
