# Code Review Patterns

## What to Evaluate

### Security

- Input validation, injection risks, secure defaults, principle of least privilege
- Check for: hardcoded secrets, secret exposure in logs, dependency CVEs
- OWASP Top 10: Injection, Authentication, Sensitive Data Exposure, SSRF, XXE, Deserialization

### Error Handling

- Graceful failures, retry mechanisms, meaningful error messages

### Testing

- Testability design, coverage gaps, edge cases

### Observability

- Logging, metrics, debugging support
- **Instrumentation:** Add enough instrumentation (logs/metrics/traces) to make it easier for engineers supporting the product/app to debug.
- **Logging Policy:** Default to `INFO` in prod; enable `DEBUG` behind a flag/env
- **Never** log secrets; mask keys containing `token`, `secret`, `password`, `key`, `authorization`

### Accessibility (a11y)

- Semantic HTML (`<button>` for buttons)
- ARIA attributes for dynamic components
- Keyboard navigability
- Sufficient color contrast

### Resource Management

- Memory leaks, connection cleanup, file handles

### Concurrency

- Thread safety, race conditions, async patterns

### Performance

- Algorithmic efficiency, database queries, caching opportunities

> [!IMPORTANT]
> **Performance rewrite requirement (when reviewing existing code):**
>
> If you find clearly inefficient logic (e.g., \(O(n^2)\) loops, N+1 queries, repeated expensive work, unnecessary allocations/parsing), you MUST:
>
> - Provide a **concrete improved implementation** (minimal diff) that preserves behavior
> - State the **expected impact** (time/space/calls) and a **measurement plan** (benchmark/metric)
> - Prefer the **smallest safe change**; do not “optimize everything” without evidence

## PR Review Formats

### Standard PR Review

```
Provide minimal, actionable feedback suitable for PR comments.
Focus on critical issues first, frame suggestions constructively,
group related issues, and explain the "why" behind each suggestion.
When possible, include file/line hints or code hunks suitable for
direct PR comments. Provide minimal diffs instead of paraphrase.
```

### Security-Focused Review

```
Prioritize security vulnerabilities by severity: injection risks,
improper data handling, auth/authz issues, common exploits,
hardcoded secrets, logging leaks, dependency CVEs, OWASP Top 10.
```

### Performance Review

```
Analyze production bottlenecks: inefficient algorithms, unnecessary
queries, memory leaks, scalability concerns. Tie each suggestion to
an expected metric (e.g., p95 latency, CPU %, memory, I/O) and
provide a simple measurement plan.
```

### Structural Review

```
Focus on code structure, readability, and maintainability.
Prioritize high-impact changes that don't require major refactoring.
```

## Anti-slop guardrails (write less, say more)

**Default behavior:** Prefer the smallest change that solves the stated problem. If a change, paragraph, or refactor doesn’t clearly earn its keep, don’t add it.

### Banned patterns (AI slop)

- Generic filler (e.g., “Great question”, “Hope this helps”, long restatements of the prompt)
- Un-grounded “best practices” lists not tied to this repo/PR
- Speculative features, refactors, or “nice-to-haves” not requested
- Placeholder code, TODO-only stubs, or incomplete sections
- Repeating the same point in multiple sections

### Required behaviors

- **Be anchored:** Tie recommendations to concrete evidence (file/line references, errors, command output, or a specific risk)
- **Be minimal:** Provide the smallest diff that fixes the issue; avoid big-bang rewrites
- **Be specific:** Replace vague advice with an actionable change (“Change X to Y because Z”)
- **Be honest about uncertainty:** Mark assumptions explicitly; do not invent details
- **Prefer deletion over addition** when it improves clarity without breaking behavior

### Slop check (run before replying)

- Can I delete 30% of this response and keep the value?
- Did I propose any unrequested work? If yes, move it to “Next ideas” or drop it
- Did I provide at least one concrete action (diff, command, file/line)?
- Did I avoid generic “best practices” unless they directly apply here?
- Did I keep examples to the minimum needed to be runnable?

## Response Format for Code Reviews

```markdown
## Summary
[Brief overview of findings]

## Critical Issues
[List with code examples, fixes, and file/line references when possible]

## Recommended Improvements
[List with code examples, explanations, and expected impact]

## Optional Enhancements
[List with brief suggestions]
```

Provide minimal diffs:

```diff
- old_code()
+ new_code()
```

## Reviewer Checklist

- [ ] Correct type(scope) in title
- [ ] Summary ≤72 chars, imperative mood
- [ ] Bulleted change list included
- [ ] Rationale paragraph provided if non-obvious change
- [ ] Security reviewed; no secrets exposed
- [ ] Tests updated/added

## Performance Suggestions Format

When suggesting performance improvements:

- **State the expected impact:** e.g., "Reduce p95 latency from X→Y", "Cut memory ~Z%"
- **Provide a measurement plan:** benchmark method/tool; production metric to watch
- **Justify the change:** tie to workload characteristics (hot paths, call frequency, I/O)

Example:

```
Cache database query results
Expected impact: Reduce average response from 200ms to 50ms
Measurement: Compare p95/p99 latency pre/post using app metrics
Justification: Query runs ~1000/min against mostly-static data
```
