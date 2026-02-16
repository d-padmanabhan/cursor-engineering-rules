---
description: Enter creative phase - explore design options for complex tasks
---

# CREATIVE MODE ACTIVATED

You are now in **CREATIVE** phase for design exploration.

## When to Use

Required for:

- Level 3-4 complexity tasks
- Architectural decisions
- Multiple valid approaches exist
- Design choices affect multiple components

## Your Tasks

1. **Identify Design Decisions**
   - What choices need to be made?
   - What constraints exist?
   - What are the requirements?

2. **Explore Options**
   - Generate 2-4 viable alternatives
   - Don't pre-judge - explore thoroughly
   - Consider unconventional approaches

3. **Compare Options**
   - Create comparison table
   - Evaluate against requirements
   - Consider trade-offs

4. **Make Recommendation**
   - Choose best option with clear rationale
   - Document why others were rejected
   - Outline implementation approach

5. **Document Decision**
   - Create `creative-*.md` in tmp/ folder
   - Update `tasks.md` with design decisions

## Output Format

```markdown
## Design Decision: [Component/Feature Name]

### Context
[What problem are we solving? What constraints exist?]

### Requirements
1. [Requirement 1]
2. [Requirement 2]
3. [Requirement 3]

### Options Explored

#### Option A: [Name]
**Description:** [How it works]

**Pros:**
- [Pro 1]
- [Pro 2]

**Cons:**
- [Con 1]
- [Con 2]

#### Option B: [Name]
**Description:** [How it works]

**Pros:**
- [Pro 1]
- [Pro 2]

**Cons:**
- [Con 1]
- [Con 2]

### Comparison Matrix

| Criteria | Option A | Option B | Option C |
|----------|----------|----------|----------|
| Performance | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| Simplicity | ⭐⭐ | ⭐⭐⭐ | ⭐ |
| Maintainability | ⭐⭐⭐ | ⭐⭐ | ⭐⭐ |

### Recommendation

**Chosen:** Option [X]

**Rationale:** [Why this option best meets requirements]

**Trade-offs Accepted:** [What we're giving up]

### Implementation Outline
1. [Step 1]
2. [Step 2]
3. [Step 3]
```

## Rules

- Explore thoroughly before deciding
- Document ALL options considered
- Be explicit about trade-offs
- Get user approval before proceeding to `/build` (**HITL / human-in-the-loop**)
