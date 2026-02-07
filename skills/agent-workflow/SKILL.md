---
name: agent-workflow
description: Structured development workflow with Plan/Implement/Review phases, QA validation, context management, and audit requirements. Enforces no remote writes, mandatory checkpoints, and verifiable audit reports. Use when working on complex tasks, multi-file changes, or when the user mentions planning, workflow, implementing features, or needs structured development guidance.
---

# Agent Workflow

## Golden Rules

**Follow this three-phase approach for all non-trivial work:**

1. **PLAN** → Design solution → Document approach → **WAIT FOR EXPLICIT APPROVAL**
2. **IMPLEMENT** → Code ONLY what was approved → **STOP** when agreed scope is complete
3. **REVIEW** → Verify results → Suggest improvements → Return to PLAN phase

## Critical Violations to Avoid

```diff
- DON'T DO THIS:
User: "Can you add authentication?"
AI: [Immediately starts coding without discussion]

+ DO THIS INSTEAD:
User: "Can you add authentication?"
AI: "Let me design a solution first. Key decisions needed:
     - OAuth 2.0 vs local authentication?
     - JWT tokens vs session-based?
     - User data storage location?
     
     Let's agree on the approach before I write any code."
```

**Why This Matters:**

- Skipping planning → Wasted time, wrong solutions, scope creep
- Implementing unplanned features → Breaking existing code, technical debt
- Not stopping after agreed scope → Confusion, frustration, rework

## Complexity Levels

| Level | Type | Workflow | Example |
|-------|------|----------|---------|
| **1** | Simple | Direct implementation → Quick review | Fix typo, simple bug fix |
| **2** | Moderate | Brief plan → QA → Implement → Review | Add new function |
| **3** | Complex | Full Plan → Creative → QA → Implement → Review | Multi-file feature |
| **4** | Architectural | Detailed Plan → Creative (mandatory) → QA → Implement → Review | Major refactoring |

## Phase 1: Planning

**You MUST NOT begin implementation until:**

- [ ] User has explicitly approved the plan
- [ ] All clarifying questions have been answered
- [ ] The scope is clearly defined and agreed upon

**Process:**

1. Analyze the request - understand scope, constraints, requirements
2. Check existing code - look for patterns and reusable components
3. Design the solution - propose approach with alternatives
4. **WAIT FOR APPROVAL** - present plan and await confirmation

**Key Questions:**

- What is the simplest solution that meets requirements?
- Can we reuse existing code or patterns?
- What are the security implications?
- How will this be tested?

## Phase 2: Implementation

**Implementation Gate Checks:**

- [ ] Explicit user approval received
- [ ] QA Validation passed (Level 2+ tasks)
- [ ] Creative Phase completed (Level 3-4 tasks)

**Constraints:**

- Implement only what was planned
- Make incremental changes
- Don't refactor unrelated code
- Don't add features not in the plan

## Phase 3: Review

**Process:**

1. Review implemented changes - verify they match the plan
2. Check for issues - security, bugs, edge cases
3. Suggest improvements - but DON'T implement them yet
4. Identify cleanup opportunities
5. Propose next steps

## Quick Commands

- **"Plan this:"** → Enter Planning phase
- **"QA"** → Run QA Validation (interrupts any process)
- **"Implement:"** → Enter Implementation phase
- **"Review:"** → Enter Review phase
- **"What's the status?"** → Check current phase

## Audit Requirements

For audit requirements including no remote writes, checkpoint management, and audit reports, see [references/audit-requirements.md](references/audit-requirements.md).

For detailed context management and QA validation, see [references/context-management.md](references/context-management.md).
