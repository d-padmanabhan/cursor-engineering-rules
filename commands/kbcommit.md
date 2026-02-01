---
description: Commit + push all kb repo changes with formatting, pre-commit, and conventional commit message file
---

# KBCOMMIT MODE ACTIVATED

You are running the **`/kbcommit`** workflow for the `~/code/labs/kb` repository.

> [!IMPORTANT]
> **Scope guard:** If the current repo root is not `~/code/labs/kb`, STOP and do not run any commit/push steps.

---

## Step 1: Review all changes (kb repo)

- Show repo/branch context:
  - `git rev-parse --show-toplevel`
  - `git branch --show-current`
  - `git rev-parse HEAD`
- Review working tree:
  - `git status`
  - `git diff`
  - `git diff --cached`

---

## Step 2: Format and clean up (language-aware)

Detect the project language/framework based on **modified files** and run the appropriate formatter/linter:

### Bash

- `shfmt -w -i 2 -ci -sr -bn <changed_shell_files>`

### GitHub Actions

- `actionlint .github/workflows/*.yaml .github/workflows/*.yml`

### Terraform

- `terraform fmt -recursive`
- `terraform validate`
- `tflint`

### Python

Run (as applicable in this repo):

- `isort <changed_python_files>`
- `ty <changed_python_files>` (or `mypy <changed_python_files>`)
- `pylint <changed_python_files>` (aim for **≥ 9.5**)
- `ruff check <changed_python_files> --fix`
- `black --line-length 140 <changed_python_files>`
- `tox` (if applicable / configured)

### Go

- `gofmt -w -s <changed_go_files>`
- `go vet ./...`
- `staticcheck ./...`
- `golangci-lint run ./...`
- `govulncheck ./...`

### Rust

- `cargo fmt`

### Markdown

- `markdownlint --fix <changed_markdown_files>`

> [!NOTE]
> If a tool is not installed or a project file is missing (e.g., no `tox.ini`), report the reason and continue with the closest substitute.

---

## Step 3: Run pre-commit (before staging/committing)

If pre-commit is configured, run:

- `pre-commit autoupdate && pre-commit run --all-files`

---

## Step 4: Stage all modified and previously unstaged files (no `git add .`)

Stage **explicitly** by file name:

- `git add <file1> <file2> ...`

Constraints:

- **DO NOT** use `git add .`
- **DO NOT** ask Y/N questions unless there are **serious bugs or security threats**

---

## Step 5: Generate a Conventional Commit message

Requirements:

- Follow Conventional Commits (`feat:`, `fix:`, `docs:`, `chore:`, etc.)
- Clearly describe what changed and **why**

Show the full commit message and files to be committed. Do not proceed until the user explicitly approves the message.

Timestamp:

- Generate an ET timestamp (for a trailer):

```bash
set -euo pipefail
LONG_DTTM="$(TZ=America/New_York date "+%A, %B %d, %Y @ %l:%M %p ET" | sed 's/  / /g')"
```

---

## Step 6: Write commit message file under `kb/extras/commit_messages`

Create the commit message file:

- Directory: `extras/commit_messages`
- Filename format:
  - `YYYYMMDD_HHMMSS_kb_<branch>_<last7sha>.md`
  - Example: `20251228_154700_kb_main_abcd123.md`

Notes:

- Use branch name from `git branch --show-current`
- Use last 7 of current HEAD via `git rev-parse --short=7 HEAD`

---

## Step 7: Commit using the commit message file

Commit using the file, and add the timestamp trailer:

```bash
set -euo pipefail
LONG_DTTM="$(TZ=America/New_York date "+%A, %B %d, %Y @ %l:%M %p ET" | sed 's/  / /g')"
git commit -F "extras/commit_messages/<filename>.md" --trailer "commit generated at ${LONG_DTTM}"
```

---

## Step 8: Confirm commit and show details

- Display:
  - Commit hash
  - Full commit message

---

## Step 9: Push to `origin` on current branch

- `git push origin <current-branch>`

---

## Step 10: Confirm push succeeded

- Display:
  - Remote branch name
  - Confirmation that local is in sync with remote
