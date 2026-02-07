# Modern Git Commands

Git 2.23+ split the multi-purpose `checkout` into focused commands for clarity and safety.

## `git switch` vs `git checkout`

| Old Command | New Command | Purpose |
|-------------|-------------|---------|
| `git checkout branch` | `git switch branch` | Switch branches |
| `git checkout -b new` | `git switch -c new` | Create and switch to new branch |
| `git checkout -- file` | `git restore file` | Restore file from index |
| `git checkout HEAD -- file` | `git restore -s HEAD file` | Restore file from commit |

**Why prefer `switch`?**

`checkout` is a multi-purpose tool that does many different things: switch branches, create branches, restore files, detach HEAD. When you see `git checkout somename`, you cannot immediately tell if it is switching to a branch, restoring a file, or going to a specific commit.

`switch` has one job: work with branches only. The intent is clear when you read it.

```bash
# Ambiguous - what does this do?
git checkout main.py

# Clear - restores the file
git restore main.py

# Clear - switches to branch (would error on file name collision)
git switch main
```

**Recommendation:** Use `git switch` and `git restore` for new work. Use `git checkout` only for older Git versions or compatibility scripts.

## `git restore` Examples

**Restore file from index (unstage):**

```bash
git restore --staged file.py    # Unstage file
git restore file.py              # Discard changes in working directory
```

**Restore file from specific commit:**

```bash
git restore -s HEAD~1 file.py    # Restore from previous commit
git restore -s abc1234 file.py    # Restore from specific commit
```

**Restore multiple files:**

```bash
git restore --staged *.py        # Unstage all Python files
git restore src/                  # Discard all changes in src/
```

## `git mv` vs `mv`

| Command | What Happens | Git Awareness |
|---------|--------------|---------------|
| `mv old new` | Filesystem move only | Git sees delete + new file |
| `git mv old new` | Move + stage in one step | Git tracks as rename |

**Using `mv` (three commands):**

```bash
mv src/utils.js src/helpers.js
git add src/helpers.js
git rm src/utils.js
```

**Using `git mv` (one command):**

```bash
git mv src/utils.js src/helpers.js
```

Both end up in the same place, but `git mv` is cleaner and preserves rename history more reliably.

> [!TIP]
> If you `mv` a file and heavily modify it before committing, Git might not recognize it as a rename (it uses content similarity heuristics). Use `git mv` when you want history tracking preserved.

## Git Worktrees & Parallel Development

Git worktrees allow you to work on multiple branches simultaneously in separate directories. This is especially useful for:

- AI agents working on multiple features in parallel
- Reviewing PRs while continuing development
- Running long tests on one branch while coding on another
- Comparing implementations side-by-side

### Basic Worktree Usage

```bash
# Create a worktree for a feature branch
git worktree add ../myproject-feature-auth feature/auth

# List all worktrees
git worktree list

# Remove worktree when done
git worktree remove ../myproject-feature-auth
```

### Phantom (Recommended Tool)

**Phantom** simplifies Git worktree management with intuitive commands and AI agent integration.

**Installation:**

```bash
brew install phantom
# or
npm install -g @aku11i/phantom
```

**Basic Usage:**

```bash
# Create a worktree for a new feature
phantom create feature-auth

# List all worktrees
phantom list

# Open shell in worktree
phantom shell feature-auth

# Run command in any worktree
phantom exec feature-auth npm test

# Open editor in worktree
phantom edit feature-auth

# Delete when done
phantom delete feature-auth
```

**GitHub Integration:**

```bash
# Create worktree from PR
phantom create --pr 123

# Create worktree from issue
phantom create --issue 456
```

> [!TIP]
> For parallel AI development, configure the Phantom MCP server in your editor. AI agents can then create isolated worktrees for each feature, enabling true parallel development without branch conflicts.
