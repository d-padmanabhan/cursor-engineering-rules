# Rules File Numbering Pattern - Revised Proposal

## Constraints

1. **No 5-ending numbers** unless related to prior 0 (e.g., 115 OK if 110 exists, but avoid standalone 5s)
2. **Keep Cloud & Infrastructure at 400+** (as they currently are)
3. **Fix duplicate numbers**
4. **Maintain logical grouping**

## Current State (from ls -1)

```
010-workflow.mdc
020-agent-audit.mdc
100-core.mdc
110-utilities.mdc
120-git.mdc
130-bash.mdc
140-makefile.mdc
150-github-actions.mdc
160-cloudformation.mdc
170-terraform.mdc
180-ansible.mdc
190-cli.mdc
200-python.mdc
210-go.mdc (DUPLICATE with 210-open-source.mdc)
210-open-source.mdc (DUPLICATE)
220.mdc (JavaScript - needs proper name)
220-documentation.mdc (DUPLICATE)
220-rust.mdc (DUPLICATE)
230-typescript.mdc
240-configuration.mdc
250-api-design.mdc (DUPLICATE with 250-docker.mdc)
250-docker.mdc (DUPLICATE)
260-kubernetes.mdc
270-postgresql.mdc
280-helm.mdc
290-security.mdc (DUPLICATE with 290-testing.mdc)
290-testing.mdc (DUPLICATE)
400-cloudflare.mdc (DUPLICATE with 400-observability.mdc - KEEP AT 400+)
400-observability.mdc (DUPLICATE - KEEP AT 400+)
410-aws.mdc (KEEP AT 400+)
420-gcp.mdc (KEEP AT 400+)
430-azure.mdc (KEEP AT 400+)
500-ai-ml.mdc
510-mcp-servers.mdc
900-markdown.mdc
999-local-overrides.mdc
```

## Proposed Numbering Scheme

### Number Ranges

- **000-099**: Core workflow and foundational rules
- **100-199**: Language and tool standards (no standalone 5s)
- **200-299**: Foundational patterns (configuration) and development tools (CLI)
- **300-399**: Testing, security, API design, observability
- **400-499**: Cloud & infrastructure (KEEP HERE - as currently)
- **500-599**: AI/ML and advanced tools
- **800-899**: Documentation standards
- **900-999**: Local overrides

## Renaming Plan

### Phase 1: Core Rules (000-099) - NO CHANGES

- 010-workflow.mdc ✓
- 020-agent-audit.mdc ✓
- 100-core.mdc ✓

### Phase 2: Language Standards & Foundational Patterns (100-199)

| Current | Target | Reason |
|---------|--------|--------|
| 110-utilities.mdc | 110-utilities.mdc | ✓ Keep |
| 120-git.mdc | 120-git.mdc | ✓ Keep |
| 130-bash.mdc | 130-bash.mdc | ✓ Keep |
| 140-makefile.mdc | 140-makefile.mdc | ✓ Keep |
| 150-github-actions.mdc | 150-github-actions.mdc | ✓ Keep |
| 160-cloudformation.mdc | 160-cloudformation.mdc | ✓ Keep |
| 170-terraform.mdc | 170-terraform.mdc | ✓ Keep |
| 180-ansible.mdc | 180-ansible.mdc | ✓ Keep |
| 200-python.mdc | 190-python.mdc | Move to 190s (language) |
| 240-configuration.mdc | 200-configuration.mdc | Move to 200s (foundational, always applied) |
| 210-go.mdc | 210-go.mdc | Move to 210s (language) |
| 220.mdc | 220-javascript.mdc | Rename and move to 220s |
| 220-rust.mdc | 230-rust.mdc | Move to 230s (fix duplicate) |
| 230-typescript.mdc | 240-typescript.mdc | Move to 240s |

### Phase 3: Development Tools (200-299)

| Current | Target | Reason |
|---------|--------|--------|
| 190-cli.mdc | 250-cli.mdc | Move to 250s (dev tools) |
| 250-docker.mdc | 441-docker.mdc | Move to 400s next to Kubernetes |

### Phase 4: Testing & Security (300-399)

| Current | Target | Reason |
|---------|--------|--------|
| 290-testing.mdc | 300-testing.mdc | Move to 300s |
| 290-security.mdc | 310-security.mdc | Move to 310s |
| 250-api-design.mdc | 320-api-design.mdc | Move to 320s |
| 400-observability.mdc | 330-observability.mdc | Move to 330s |

### Phase 5: Cloud & Infrastructure (400-499) - KEEP AS IS

| Current | Target | Reason |
|---------|--------|--------|
| 400-cloudflare.mdc | 400-cloudflare.mdc | ✓ Keep |
| 410-aws.mdc | 410-aws.mdc | ✓ Keep |
| 420-gcp.mdc | 420-gcp.mdc | ✓ Keep |
| 430-azure.mdc | 430-azure.mdc | ✓ Keep |
| 250-docker.mdc | 440-docker.mdc | Move to 400s (container runtime) |
| 260-kubernetes.mdc | 450-kubernetes.mdc | Move to 400s (orchestration) |
| 280-helm.mdc | 460-helm.mdc | Move to 400s (K8s package manager) |
| 270-postgresql.mdc | 470-postgresql.mdc | Move to 400s (database/infra) |

**Note**: Configuration moved to 200s (foundational, always applied) instead of staying in 200s dev tools section.

### Phase 6: AI/ML (500-599)

| Current | Target | Reason |
|---------|--------|--------|
| 500-ai-ml.mdc | 500-ai-ml.mdc | ✓ Keep |
| 510-mcp-servers.mdc | 510-mcp-servers.mdc | ✓ Keep (AI/ML tooling) |

### Phase 7: Documentation (800-899)

| Current | Target | Reason |
|---------|--------|--------|
| 900-markdown.mdc | 800-markdown.mdc | Move to 800s |
| 220-documentation.mdc | 810-documentation.mdc | Move to 800s (documentation) |
| 210-open-source.mdc | 820-open-source.mdc | Move to 800s (includes contribution docs) |

### Phase 8: Local Overrides (900-999)

| Current | Target | Reason |
|---------|--------|--------|
| 999-local-overrides.mdc | 999-local-overrides.mdc | ✓ Keep |

## Final Numbering Structure

```
010-workflow.mdc
020-agent-audit.mdc
100-core.mdc
110-utilities.mdc
120-git.mdc
130-bash.mdc
140-makefile.mdc
150-github-actions.mdc
160-cloudformation.mdc
170-terraform.mdc
180-ansible.mdc
190-python.mdc
200-configuration.mdc
210-go.mdc
220-javascript.mdc
230-rust.mdc
240-typescript.mdc
250-cli.mdc
300-testing.mdc
310-security.mdc
320-api-design.mdc
330-observability.mdc
400-cloudflare.mdc
410-aws.mdc
420-gcp.mdc
430-azure.mdc
440-docker.mdc
450-kubernetes.mdc
460-helm.mdc
470-postgresql.mdc
500-ai-ml.mdc
510-mcp-servers.mdc
800-markdown.mdc
810-documentation.mdc
820-open-source.mdc
999-local-overrides.mdc
```

**Note**: No 5-ending numbers used (avoiding 115, 145, 155, 165, 185, 195, etc.)

## Summary of Changes

### Files to Rename (17 total)

1. `200-python.mdc` → `190-python.mdc`
2. `240-configuration.mdc` → `200-configuration.mdc` (move to foundational 200s)
3. `210-go.mdc` → `210-go.mdc` (adjust for configuration)
4. `220.mdc` → `220-javascript.mdc` (rename and adjust)
5. `220-rust.mdc` → `230-rust.mdc` (fix duplicate, adjust)
6. `230-typescript.mdc` → `240-typescript.mdc` (adjust)
7. `190-cli.mdc` → `250-cli.mdc` (move to dev tools 200s)
8. `220-documentation.mdc` → `810-documentation.mdc`
9. `210-open-source.mdc` → `820-open-source.mdc`
10. `250-docker.mdc` → `440-docker.mdc`
11. `250-api-design.mdc` → `320-api-design.mdc`
12. `260-kubernetes.mdc` → `450-kubernetes.mdc`
13. `280-helm.mdc` → `460-helm.mdc`
14. `270-postgresql.mdc` → `470-postgresql.mdc`
15. `290-testing.mdc` → `300-testing.mdc`
16. `290-security.mdc` → `310-security.mdc`
17. `400-observability.mdc` → `330-observability.mdc`
18. `900-markdown.mdc` → `800-markdown.mdc`
19. `510-mcp-servers.mdc` → `510-mcp-servers.mdc` (no change - already correct)

### Priority Updates Required

After renaming, update `priority:` in frontmatter to match filename number.

## Verification Checklist

After renaming:

- [ ] No duplicate numbers
- [ ] No standalone 5-ending numbers (only 110→115 if needed, but we're avoiding it)
- [ ] Cloud & Infrastructure stays at 400+
- [ ] Logical grouping maintained
- [ ] Priority values match filename numbers
- [ ] All files properly named
