# Workflow Command Patterns

While Claude Skills don't support explicit `/command` syntax like Cursor IDE, these workflow patterns can be triggered through natural language requests. Use these patterns to guide structured development workflows.

## Command Overview

| Command | Purpose | Trigger Phrase |
|---------|---------|----------------|
| **Init** | Initialize task, detect complexity | "Let's start working on...", "I need to...", "Can you help me..." |
| **Plan** | Design solution, document approach | "Plan how to...", "Design a solution for...", "How should we approach..." |
| **Creative** | Explore design options | "What are the options for...", "Compare approaches to...", "Design decision needed for..." |
| **QA** | Validate environment | "Check if we can proceed...", "Validate the environment...", "Are dependencies ready..." |
| **Build** | Implement approved plan | "Implement the plan...", "Build the solution...", "Write the code for..." |
| **Review** | Verify implementation | "Review the changes...", "Check the implementation...", "Verify the code..." |
| **Self-Review** | Comprehensive code review | "Review all changes...", "Do a full code review...", "Check everything before PR..." |
| **Quick-Review** | Fast critical issues check | "Quick check for issues...", "Find critical problems...", "Pre-commit validation..." |
| **Check-Progress** | Review work progress | "What's the status...", "Show progress...", "What have we done..." |
| **Archive** | Document lessons learned | "Document what we learned...", "Archive this task...", "Create a summary..." |

---

## Commandify repeated prompts (workflow patterns)

If you find yourself giving the same prompt more than twice, treat it as a workflow smell:

- Convert it into a reusable “command pattern” section in this doc (or a new reference doc)
- Keep the entrypoint short (what it does, when to use it, output format)
- Put verbose details in references so they’re only loaded when needed

## Init - Task Initialization

**Purpose:** Analyze project, detect complexity, set up context

**When to Use:**

- Starting new work
- Need to understand project structure
- Determining appropriate workflow

**Process:**

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
   | 1 | Quick Fix | Single file, obvious change, < 30 min | Build → Review |
   | 2 | Simple Task | Few files, clear scope, < 2 hours | Plan → QA → Build → Review |
   | 3 | Feature | Multiple files, design decisions needed | Plan → Creative → QA → Build → Review |
   | 4 | Complex | Architectural, cross-cutting, multi-day | Plan → Creative → QA → Build → Review → Archive |

4. **Set Up Context**
   - Create/update `tmp/tasks.md` if needed
   - Create/update `tmp/active-context.md` if needed
   - Note any existing progress

5. **Route to Next Phase**
   - Level 1: Recommend immediate Build
   - Level 2-4: Recommend Planning phase

**Output Format:**

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
[workflow path, e.g., Plan → Creative → QA → Build → Review]

### Next Step
Proceed to Planning phase (or Build for Level 1 tasks).
```

---

## Plan - Planning Phase

**Purpose:** Design solution, document approach before implementation

**When to Use:**

- Level 2+ tasks
- Need to design solution
- Multiple approaches possible

**Process:**

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
   - Update `tmp/tasks.md` or `tmp/active-context.md` if they exist
   - List files to be modified
   - Outline implementation steps

5. **Present and WAIT**
   - Show the plan clearly
   - Ask for explicit approval before proceeding
   - Answer any clarifying questions

**Output Format:**

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

### Security Considerations
- [Security implications]

### Dependencies
- [What needs to be installed/configured]
```

**Rules:**

- Ask max 3 clarifying questions if scope is ambiguous
- Do NOT start coding until user approves
- Keep plans concise but complete
- Consider security implications

---

## Creative - Design Exploration Phase

**Purpose:** Explore design options for complex tasks requiring design decisions

**When to Use:**

- Level 3-4 tasks
- Multiple valid approaches exist
- Design decisions affect multiple components

**Process:**

1. **Entry Gate Verification**
   - Task complexity is Level 3-4
   - Design decisions identified
   - Creative phase requirements documented

2. **Design Exploration**
   - Identify design options (2-4 alternatives)
   - Compare pros/cons in tabular format
   - Analyze against requirements and constraints
   - Document decision rationale

3. **Exit Gate Verification**
   - All decisions documented
   - Rationale provided for choices
   - Implementation plan outlined
   - Verification against requirements

4. **Documentation**
   - Create `tmp/creative-*.md` with chosen approach
   - Update `tmp/tasks.md` with design decisions
   - Mark creative phase complete

5. **Proceed to QA Validation** then Implementation

**Output Format:**

```markdown
## Creative: [Component/Feature Name]

**Date:** [Date]
**Task:** [Related task reference]

### Design Challenge
[What design decision needs to be made]

### Options Considered

| Option | Pros | Cons | Complexity | Decision |
|--------|------|------|------------|----------|
| Option A | ... | ... | Low/Med/High | ✅ Chosen / ❌ Rejected |
| Option B | ... | ... | Low/Med/High | ✅ Chosen / ❌ Rejected |
| Option C | ... | ... | Low/Med/High | ✅ Chosen / ❌ Rejected |

### Rationale
[Why the chosen option was selected]

### Trade-offs Accepted
- [Trade-off 1]: [Why it's acceptable]
- [Trade-off 2]: [Why it's acceptable]

### Implementation Notes
[Key considerations for implementing the chosen option]

### References
- [Link to relevant docs/patterns]
- [Related decisions]
```

**Implementation Block:**

If Creative Phase is required but not completed:

```
⛔ IMPLEMENTATION BLOCKED
Creative phases MUST be completed before implementation.

Required Creative Phases:
- [ ] [Creative Phase 1]
- [ ] [Creative Phase 2]

🚫 This is a HARD BLOCK
Implementation CANNOT proceed until all creative phases are completed.
```

---

## QA - Quality Assurance Validation

**Purpose:** Technical validation to prevent implementation failures

**When to Use:**

- Mandatory before Implementation for Level 2+ tasks
- Can be called explicitly
- After Creative Phase completion (Level 3-4)

**Four-Point Validation Process:**

### 1. Dependency Verification

**Check:**

- All required packages/tools installed
- Versions compatible with requirements
- No missing dependencies

**Process:**

```bash
# Example checks:
- Check package.json / requirements.txt / pyproject.toml
- Verify Node.js/Python/other runtime versions
- Check if dependencies are installed (npm list, pip list, etc.)
- Verify version compatibility
```

**Output:**

- List of required dependencies
- List of installed dependencies
- Compatibility status
- Missing or incompatible dependencies (if any)

### 2. Configuration Validation

**Check:**

- Configuration files exist and are valid
- Syntax is correct (JSON, YAML, TOML, etc.)
- Platform compatibility (Windows/macOS/Linux)
- Required settings present

**Process:**

```bash
# Example checks:
- Validate JSON/YAML/TOML syntax
- Check for required configuration keys
- Verify platform-specific settings
- Test configuration loading
```

**Output:**

- Configuration files checked
- Syntax validation status
- Platform compatibility status
- Missing or invalid configurations (if any)

### 3. Environment Validation

**Check:**

- Build tools available (npm, pip, make, etc.)
- Permissions sufficient (write access, port availability)
- Environment variables set (if needed)
- Required ports available

**Process:**

```bash
# Example checks:
- Verify build tools installed (node, python, git, etc.)
- Check write permissions in project directory
- Verify port availability (if needed)
- Check environment variables
```

**Output:**

- Build tools status
- Permission status
- Environment readiness
- Missing tools or permission issues (if any)

### 4. Minimal Build Test

**Check:**

- Build process works
- Core functionality testable
- No blocking errors

**Process:**

```bash
# Example checks:
- Run minimal build/test command
- Verify core functionality
- Check for blocking errors
- Test basic operations
```

**Output:**

- Build process status
- Functionality test status
- Errors found (if any)

### QA Validation Report Format

**Success Report:**

```
✅ QA VALIDATION STATUS
✓ Dependencies        All required packages installed
✓ Configurations      Format verified for platform
✓ Environment         Suitable for implementation
✓ Build Test          Core functionality verified

✅ VERIFIED - Clear to proceed to Implementation phase
```

**Failure Report:**

```
❌ QA VALIDATION FAILED

The following issues must be resolved before proceeding:

1️⃣ DEPENDENCY ISSUES:
- [Detailed description]
- [Recommended fix]

2️⃣ CONFIGURATION ISSUES:
- [Detailed description]
- [Recommended fix]

3️⃣ ENVIRONMENT ISSUES:
- [Detailed description]
- [Recommended fix]

4️⃣ BUILD TEST ISSUES:
- [Detailed description]
- [Recommended fix]

⛔ IMPLEMENTATION BLOCKED until these issues are resolved.
```

---

## Build - Implementation Phase

**Purpose:** Write code following approved plan

**When to Use:**

- After plan is approved
- After QA validation passes (Level 2+)
- After Creative Phase completes (Level 3-4)

**Implementation Gate Checks:**

**You MUST NOT start implementation until:**

- [ ] Explicit user approval received in Planning phase
- [ ] QA Validation passed (for Level 2+ tasks)
- [ ] Creative Phase completed (for Level 3-4 tasks)
- [ ] All questions answered and scope agreed

**Process:**

1. **Follow the agreed plan** - Implement exactly what was discussed
2. **Make incremental changes** - Small, testable commits
3. **Update context files** - Track progress in `tmp/progress.md` or `tmp/tasks.md`
4. **Stop at boundaries** - Don't fix unrelated issues or add unplanned features
5. **Complete the agreed scope** - Then STOP and wait for review

**Constraints:**

- Implement only what was planned
- Follow all coding standards
- Include error handling, logging, and security considerations
- Don't refactor unrelated code
- Don't add features not in the plan
- Don't optimize prematurely

**If you encounter issues:**

- Trivial fixes (typos, obvious bugs): OK to fix immediately
- Substantial changes needed: STOP, document in Review phase, discuss in next Planning phase

---

## Review - Review Phase

**Purpose:** Verify implementation, suggest improvements

**When to Use:**

- After implementation is complete
- Before committing changes
- Before creating PR

**Process:**

1. **Review implemented changes** - Verify they match the plan
2. **Check for issues** - Security, bugs, edge cases, performance
3. **Suggest improvements** - But DON'T implement them yet
4. **Update context files** - Document findings in `tmp/reflect-*.md` or `tmp/tasks.md`
5. **Identify cleanup opportunities** - Can we remove/simplify existing code?
6. **Propose next steps** - What should happen next?

**Review Checklist:**

- [ ] Changes match the agreed plan
- [ ] Security considerations addressed
- [ ] Error handling appropriate
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] No unrelated changes
- [ ] Code follows all standards

**Output Format:**

```markdown
## Review: [Task Name]

**Date:** [Date]
**Task:** [Reference to original task]

### What Was Done
[Summary of what was implemented]

### Changes Made
- [Change 1]: [Description]
- [Change 2]: [Description]

### Issues Found
- **Critical:** [Critical issues]
- **Recommended:** [Recommended improvements]
- **Optional:** [Optional enhancements]

### Lessons Learned
- [Lesson 1]: [What we learned]
- [Lesson 2]: [What we learned]

### What Went Well
- [Success 1]
- [Success 2]

### Challenges Encountered
- [Challenge 1]: [How it was resolved]
- [Challenge 2]: [How it was resolved]

### Improvements for Next Time
- [Improvement 1]: [Why it would help]
- [Improvement 2]: [Why it would help]

### Follow-up Actions
- [ ] [Action item 1]
- [ ] [Action item 2]
```

---

## Self-Review - Comprehensive Code Review

**Purpose:** Full code review comparing branch to main - PR-ready analysis

**When to Use:**

- Before creating PR
- Need comprehensive analysis
- Want full audit trail

**Process:**

### Phase 1: Context Gathering & Audit Setup

1. **Branch Information:**
   - Current branch name (`git branch --show-current`)
   - Base branch (default: `main`)
   - Baseline SHA (`git rev-parse HEAD`)
   - Commits ahead of base (`git log --oneline main..HEAD`)
   - Files changed (`git diff main...HEAD --name-only`)

2. **Change Summary:**
   - Show staged changes (`git diff --cached --stat`)
   - Show unstaged changes (`git diff --stat`)
   - Ignore files/folders listed in `.gitignore`
   - Generate diff summary: `git diff main...HEAD --stat`

3. **Recent Commit History:**
   - Display last 3-5 commits: `git log --oneline -5 main..HEAD`
   - Show commit messages to understand change context

### Phase 2: Static Analysis

Run appropriate linters and analyzers based on project language:

**Python:**

- `ruff check .` (linting)
- `ruff format --check .` (format check)
- `mypy .` or `ty .` (type checking)
- `pylint` (aim for score ≥9.5)
- `bandit -r .` (security scanning)
- `pip-audit` (dependency vulnerabilities)

**Bash/Shell:**

- `shellcheck` on all `.sh` files
- `shfmt -d .` (format check)

**Go:**

- `gofmt -d .` (format check)
- `golangci-lint run`
- `govulncheck ./...`

**JavaScript/TypeScript:**

- `eslint . --max-warnings=0`
- `npm audit` (if `package.json` exists)
- `tsc --noEmit` (if TypeScript)

**Terraform:**

- `terraform fmt -check -recursive`
- `terraform validate`
- `tflint`

**General:**

- `pre-commit run --all-files` (if configured)
- `gitleaks detect --source .` (secrets scanning)

Report all findings with file/line references.

### Phase 3: Diff Analysis

Analyze `git diff main...HEAD` focusing on:

**Critical Issues (Must Fix)**

- Security vulnerabilities: Hardcoded secrets, injection risks, OWASP Top 10 violations
- Bugs: Logic errors, null pointer risks, data loss scenarios
- Breaking changes: API modifications without migration path

**Recommended Improvements**

- Performance: Inefficient algorithms, N+1 queries, missing caching
- Maintainability: Code duplication, unclear naming, missing error handling
- Observability: Missing logging, no metrics, poor error messages

**Optional Enhancements**

- Style: Formatting inconsistencies, minor naming improvements
- Documentation: Missing docstrings, unclear comments

### Phase 4: Security Review

**OWASP Top 10 Checks:**

- A01: Broken Access Control
- A02: Cryptographic Failures
- A03: Injection
- A04: Insecure Design
- A05: Security Misconfiguration
- A06: Vulnerable Components
- A07: Authentication Failures
- A08: Software Integrity Failures
- A09: Logging Failures
- A10: SSRF

**Secrets Scanning:**

- Check for hardcoded credentials
- Verify secrets are not logged
- Check for exposed API keys

### Phase 5: Automated Fixes (Optional)

If user approves:

- Apply formatters (`ruff format`, `black`, `gofmt`, etc.)
- Re-stage formatted files
- Report what was fixed

### Phase 6: Summary Report

Generate PR-ready report:

```markdown
## Code Review Summary

### Files Changed
- [Count] files modified
- [Count] files added
- [Count] files deleted

### Critical Issues (Must Fix)
1. [Issue]: [File:Line] - [Description] - [Fix]

### Recommended Improvements
1. [Issue]: [File:Line] - [Description] - [Suggestion]

### Optional Enhancements
1. [Issue]: [File:Line] - [Description] - [Suggestion]

### Security Findings
- [Finding 1]
- [Finding 2]

### Test Coverage
- [Coverage summary]

### Overall Assessment
[Summary and recommendation]
```

---

## Quick-Review - Fast Critical Issues Check

**Purpose:** Streamlined review for rapid iteration

**When to Use:**

- Pre-commit validation
- Rapid development cycles
- Small changes

**Process:**

1. **Run Essential Linters Only**
   - Errors only (not warnings)
   - Critical security checks
   - Breaking change detection

2. **Focus on Critical Issues**
   - Security vulnerabilities
   - Bugs that break functionality
   - Breaking changes

3. **Minimal Report**
   - List only must-fix issues
   - Skip style/documentation improvements
   - Quick feedback

**Output Format:**

```markdown
## Quick Review

### Critical Issues Found
1. [Issue]: [File:Line] - [Description] - [Fix]

### Status
✅ Ready to commit (if no critical issues)
❌ Fix critical issues first (if issues found)
```

---

## Check-Progress - Progress Review

**Purpose:** Review work progress without staging/committing

**When to Use:**

- Want to see what's been done
- Need commit message suggestions
- Checking status before committing

**Process:**

1. **Change Detection**
   - Identify modified files
   - Count files by type
   - Extract Jira ticket from branch name (if present)

2. **Quality Checks**
   - Run linters on modified files only
   - Check formatting
   - Security scan

3. **Change Analysis**
   - Review `git diff` (staged + unstaged)
   - Categorize findings (Critical/Recommended/Optional)

4. **Propose Commit Message**
   - Follow Conventional Commits format
   - Include Jira ticket if present
   - List key changes

**Output Format:**

```markdown
## Progress Check

### Files Modified
- [Count] Python files
- [Count] Bash files
- [Count] Other files

### Quality Checks
✅ Linting: Pass
✅ Formatting: Pass
✅ Security: Pass

### Proposed Commit Message
```

<type>(<scope>): <short summary>

- <change 1>
- <change 2>
- <change 3>

<optional explanatory paragraph>
```

### Issues Found

- [Critical/Recommended/Optional issues]

```

---

## Archive - Document Lessons Learned

**Purpose:** Document lessons learned for completed tasks

**When to Use:**
- Level 3-4 tasks completed
- Significant work finished
- Want to capture knowledge

**Process:**

1. **Create Archive Document**
   - Use `tmp/reflect-*.md` template
   - Document what was done
   - Capture lessons learned

2. **Update Knowledge Base**
   - Add patterns to relevant skill references
   - Update documentation if needed
   - Note reusable solutions

3. **Clean Up**
   - Archive context files
   - Remove temporary files
   - Update project status

**Output Format:**

See Review phase output format - Archive uses similar structure but focuses on knowledge capture rather than code review.

---

## Workflow Integration

### For Simple Tasks (Level 1)
```

Init → Build → Review

```

### For Moderate Tasks (Level 2)
```

Init → Plan → QA → Build → Review

```

### For Complex Tasks (Level 3-4)
```

Init → Plan → Creative → QA → Build → Review → Archive

```

---

## Best Practices

1. **Always check context files** before starting work
2. **Update context files** as you progress
3. **Don't skip phases** for complex tasks
4. **Wait for approval** before moving from Planning to Implementation
5. **Run QA Validation** before Implementation for Level 2+ tasks
6. **Complete Creative Phase** before Implementation for Level 3-4 tasks
7. **Block Implementation** if QA fails or Creative Phase incomplete
8. **Document decisions** in context files
9. **Review before committing** - use Self-Review or Quick-Review
10. **Archive significant work** to capture knowledge
