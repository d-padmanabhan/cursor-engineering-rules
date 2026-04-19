---
description: Enter review phase - verify implementation and suggest improvements
---

# REVIEW MODE ACTIVATED

You are now in **REVIEW** phase.

## Your Tasks

1. **Verify Implementation**
   - Check that changes match the approved plan
   - Ensure all planned items are complete
   - Confirm no unrelated changes were made

2. **Check for Issues**
   - Security vulnerabilities
   - Bugs or edge cases
   - Performance concerns
   - Error handling gaps

3. **Review Against Standards**
   - Code follows 100-core.mdc guidelines
   - Language-specific rules applied
   - Tests added/updated
   - Documentation updated

4. **Suggest Improvements**
   - Note potential improvements but DON'T implement them
   - These are for future work, not this PR
   - Prioritize by impact

5. **Update Context Files**
   - Document findings in `reflect-*.md` or `tasks.md`
   - Note lessons learned

## Review Checklist

### Correctness

- [ ] Changes match the agreed plan
- [ ] All edge cases handled
- [ ] Error handling appropriate
- [ ] No regressions introduced

### Security

- [ ] No hardcoded secrets
- [ ] Input validation present
- [ ] No injection vulnerabilities
- [ ] Principle of least privilege followed

### Quality

- [ ] Code follows existing patterns
- [ ] Naming is clear and consistent
- [ ] No unnecessary complexity
- [ ] DRY principle followed

### Testing

- [ ] Tests added/updated
- [ ] Edge cases covered
- [ ] Tests pass locally

### Documentation

- [ ] Code comments where needed
- [ ] README updated if applicable
- [ ] API docs updated if applicable

## Output Format

```markdown
## Review Summary

### What Was Implemented
- [Summary of changes]

### Verification
- [x] Matches approved plan
- [x] All items complete
- [ ] Issue found: [description]

### Issues Found
1. **[Critical/Recommended/Optional]**: [Issue description]
   - Location: `file.py:123`
   - Suggestion: [How to fix]

### Suggested Improvements (Future Work)
- [Improvement 1]
- [Improvement 2]

### Ready to Commit?
[Yes/No - with reasoning]
```

## After Review

If ready to commit, prepare commit message following 130-git.mdc standards.
