# Agent Audit Requirements

These rules apply to AI agents operating in workspaces. They are designed to make work **reversible**, **verifiable**, and **auditable**.

## 1. Remote Writes: Default Deny

By default, AI agents MUST NOT modify any remote state.

If (and only if) the user explicitly authorizes a specific remote write, the agent may execute only the authorized command(s) and MUST record:

- The exact authorization (who/when/what)
- The exact commands executed
- The results and exit codes

**Disallowed operations include:**

- `git push`, forced updates, tag pushes
- Creating/merging PRs, pushing branches
- `terraform apply`, `kubectl apply`, `helm upgrade`
- Database migrations against non-local DBs
- Any command that changes remote resources

**Commits are local-only** and allowed only after explicit user authorization.

## 2. Local Branch Discipline

All work MUST be performed on the **current branch**.

Requirements:

- Record the baseline branch name and `HEAD` SHA in the audit report
- Create a local backup branch before making changes:
  - `DTTM="$(date +%Y%m%d_%H%M%S)"`
  - `git branch "checkout-point/${DTTM}" HEAD`
- Do not fast-forward, rebase, or otherwise rewrite shared history unless explicitly authorized

## 3. Backups & Checkpoints (Mandatory)

Before making changes, create **identifiable, reversible checkpoints**:

**Minimum checkpoints:**

- **Baseline identifier:** Record `HEAD` SHA and current branch name
- **Working tree backup:** Create stash with untracked files: `git stash push -u -m "checkpoint/<id>"`
- **Rollback anchor:** Create local checkpoint: `git branch "checkout-point/<id>" <baseline-sha>`

**Checkpoint rules:**

- Each checkpoint MUST have a unique `<id>` (recommend `YYYYMMDD_HHMMSS`)
- Every checkpoint MUST be recorded with timestamp in the audit report

## 4. Local Verification Gate (Mandatory)

Before proposing any commit messages, run local verification as applicable:

- Unit/integration tests
- Lint
- Formatting
- Type checks
- Build/package step

If verification cannot run, state:

- The exact reason
- The closest substitute run instead
- What evidence was relied on

**Examples of verification commands (not exhaustive):**

- **Python:** `pytest`, `ruff check`, `ruff format --check`, `mypy`/`pyright`, `pylint`
- **JavaScript/TypeScript:** `npm test`, `npm run lint`, `npm run build`, `tsc --noEmit`
- **Go:** `go test ./...`, `golangci-lint run`, `gofmt -d .`
- **Rust:** `cargo test`, `cargo clippy`, `cargo fmt --check`
- **Shell:** `shellcheck *.sh`, `shfmt -d .`
- **General:** `pre-commit run --all-files` (if configured)

## 5. Verifiable Audit Report (Mandatory)

For every non-trivial task, write one report file:

**Repo root (required):**

- `export GIT_REPO_ROOT="$(git rev-parse --show-toplevel)"`

**Path rules:**

- If `<GIT_REPO_ROOT>/tmp/` exists and is gitignored: `<GIT_REPO_ROOT>/tmp/agent_reports/agent_report_<repo>_<branch>_<timestamp>.md`
- Otherwise: `/tmp/agent_report_<repo>_<branch>_<timestamp>.md`

> [!IMPORTANT]
> `tmp/` is intended to be **gitignored**. Do not commit or push audit artifacts (or other files under `tmp/`) unless explicitly requested.

**Required contents:**

- Start and end timestamps (local time and UTC)
- Repo name, branch name, HEAD SHA
- Every command executed (copy-pasteable) with exit codes
- Summary of changes: `git status`, `git diff --stat`, changed files
- Verification outputs
- Proposed commit messages
- Checkpoints/backups section with timestamps
- Any authorized remote-write operations

### Optional: Terminal Recordings (asciinema)

For complex debugging sessions or demos, agents MAY create terminal recordings using `asciinema`.

**When to record:**

- Complex debugging where timing/flow matters
- Sessions that would benefit from visual playback
- When user explicitly requests a recording

**Recording path:**

- Save to: `<GIT_REPO_ROOT>/tmp/agent_reports/recordings/<repo>_<branch>_<yyyymmdd_HHMMSS>.cast`
- Reference the recording path in the markdown audit report

**How to record:**

```bash
# Start recording
asciinema rec -q "<GIT_REPO_ROOT>/tmp/agent_reports/recordings/session.cast"

# ... perform commands ...

# Stop recording (Ctrl+D or exit)
```

**Important:**

- Recordings are a **supplement**, not a replacement for markdown reports
- The markdown report remains the **primary audit artifact** (searchable, structured)
- Recordings are for **understanding flow**, not for audit compliance

## 6. If Commits Are Authorized Later

Only after the user explicitly authorizes commits:

1. **Commit locally** with the agreed messages
2. **Append to the audit report:**
   - Commit SHAs and commit messages
   - Output from: `git log --date=iso-strict -n <N>` (where `<N>` covers the new commits)
   - Confirmation that commits match the proposed plan
3. **Do NOT push** to remote unless explicitly authorized separately
4. **Record the authorization** in the audit report with timestamp

## 7. GitHub CLI Read-Only Mode

**Allowed:**

- `gh repo view`
- `gh issue list` / `gh issue view`
- `gh pr list` / `gh pr view`
- `gh api` GET requests only

**Disallowed:**

- `gh pr create`, `gh pr merge`
- `gh repo fork`
- Any `gh api` mutation (POST/PATCH/PUT/DELETE)

## 8. Required Sequence

```
Understand task → propose plan → create minimal change set → take checkpoints →
run verification → produce audit report → propose commit(s) → wait for approval
```
