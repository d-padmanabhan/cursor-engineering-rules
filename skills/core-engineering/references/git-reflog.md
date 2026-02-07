# The Reflog: Git's Safety Net

## What is the Reflog?

The **reflog** (reference log) is Git's time machine. While `git log` shows only commits reachable from branches/tags, the reflog records **every movement of HEAD** — every checkout, reset, commit, rebase, branch switch, and even "lost" commits.

**Key insight:** The reflog remembers everything, even commits that appear "lost" from your branch history. This makes Git operations reversible and gives you confidence to experiment.

## Why Reflog Matters

**Reflog enables:**

- **Recovery** - Restore deleted branches, undo resets, find lost commits
- **Confidence** - Use advanced features (rebase, reset) without fear
- **Debugging** - Track "what commit was I on 20 minutes ago?"
- **Learning** - Understand Git internals by watching HEAD movements

**Reflog is your safety net** — it makes "dangerous" operations safe because you can always undo them.

## Basic Reflog Usage

**View reflog:**

```bash
git reflog                    # Show all HEAD movements
git reflog --date=relative    # Show with relative timestamps
git reflog --date=iso         # Show with ISO timestamps
git reflog main               # Show reflog for specific branch
```

**Example output:**

```
e4f3c1d HEAD@{0}: reset: moving to HEAD~1
8a17f0e HEAD@{1}: commit: add missing validation
c113d92 HEAD@{2}: checkout: moving from feature/login to main
abc1234 HEAD@{3}: commit: implement login feature
```

**Understanding `HEAD@{n}`:**

- `HEAD@{0}` - Current position
- `HEAD@{1}` - One step ago
- `HEAD@{5}` - Five steps ago
- `HEAD@{2.hours.ago}` - Two hours ago (relative time)

## Common Recovery Patterns

### 1. Undo a Reset (Go Back One Step)

```bash
# You just did: git reset --hard HEAD~1
# Oops! You need that commit back

git reflog                    # Find the commit
git reset --hard HEAD@{1}     # Go back to before the reset
```

### 2. Recover a Deleted Branch

```bash
# You deleted: git branch -D feature/payment
# Recover it:

git reflog                    # Find the last commit on the branch
# Look for: abc1234 HEAD@{5}: checkout: moving from feature/payment to main

git checkout -b feature/payment abc1234  # Recreate branch from that commit
```

### 3. Find a Lost Commit

```bash
# You committed something but can't find it
git reflog                    # Search through all HEAD movements
git show HEAD@{10}           # Inspect a specific point in history
git checkout HEAD@{10}       # Checkout that commit to verify
```

### 4. Recover from a Bad Rebase

```bash
# Rebase went wrong
git reflog                    # Find the commit before rebase started
git reset --hard HEAD@{10}    # Go back to before rebase
```

### 5. Recover Stashed Changes

```bash
# Stash didn't apply cleanly, or you lost track of it
git reflog                    # Find stash commit
# Look for: def5678 HEAD@{3}: WIP on main: abc1234 previous commit

git stash show -p def5678     # See what was stashed
git checkout -b recover-stash def5678  # Recover to new branch
```

## Advanced Reflog Patterns

**Filter reflog by operation:**

```bash
git reflog show --all | grep checkout    # Show only checkouts
git reflog show --all | grep reset       # Show only resets
git reflog show --all | grep commit       # Show only commits
```

**Find commits by time:**

```bash
git reflog --since="2 hours ago"         # Last 2 hours
git reflog --until="1 day ago"          # Up to 1 day ago
git reflog --date=relative              # Human-readable times
```

**Reflog for specific refs:**

```bash
git reflog show main                    # Reflog for main branch
git reflog show origin/main             # Reflog for remote-tracking branch
git reflog show stash                   # Reflog for stashes
```

## Reflog Expiration & Garbage Collection

**Important:** Reflog entries expire after 90 days by default (configurable).

**Check expiration settings:**

```bash
git config gc.reflogExpire              # Default: 90 days
git config gc.reflogExpireUnreachable   # Unreachable commits: 30 days
```

**Prevent expiration (for important repos):**

```bash
# Keep reflog forever
git config gc.reflogExpire never
git config gc.reflogExpireUnreachable never
```

**Manual cleanup (if needed):**

```bash
git reflog expire --expire=now --all    # Expire all entries
git gc --prune=now                      # Garbage collect expired entries
```

> [!WARNING]
> Expiring reflog entries makes recovery impossible. Only do this if you're certain you don't need to recover anything.

## Reflog as a Learning Tool

**Watch Git operations in real-time:**

```bash
# Before operation
git reflog --date=relative | head -5

# Perform operation (rebase, reset, etc.)
git rebase main

# After operation
git reflog --date=relative | head -10   # See what happened
```

**Patterns you'll notice:**

- **Rebases** create multiple HEAD movements as commits are replayed
- **Resets** jump HEAD to different commits
- **Merges** move HEAD forward
- **Checkouts** change which commit HEAD points to
- **Stashes** are commits too (they appear in reflog)

## When Reflog Can't Help

**Reflog limitations:**

- **Only local** - Reflog exists only on your machine (not on remote)
- **Expires** - Entries expire after 90 days (configurable)
- **Garbage collected** - Expired entries are removed by `git gc`
- **Not for remote recovery** - Can't recover from force-push disasters on remote

**For remote recovery:**

- Use branch protection rules
- Require PR reviews
- Use `git revert` instead of `git reset` for shared branches
- Keep backups of important branches

## Reflog Best Practices

**1. Use reflog before panicking:**

```bash
# Something went wrong? Check reflog first
git reflog
# Find the "before" state
git reset --hard HEAD@{n}
```

**2. Make reflog part of your workflow:**

```bash
# After major operations, check reflog
git rebase main
git reflog --date=relative | head -10   # Verify what happened
```

**3. Use relative time for easier navigation:**

```bash
git reflog --date=relative              # "2 hours ago" vs "2024-12-25 10:30:00"
```

**4. Document important commits:**

```bash
# If you're about to do something risky, note the current position
git reflog | head -1                    # Save this output
# Now you can always get back: git reset --hard <saved-commit>
```

**5. Enable reflog for all refs (if needed):**

```bash
git config core.logAllRefUpdates true   # Track reflog for all refs
```

## Real-World Example: Complete Recovery Workflow

**Scenario:** You accidentally reset your feature branch and lost commits.

```bash
# Step 1: Don't panic, check reflog
git reflog --date=relative

# Output:
# abc1234 HEAD@{0}: reset: moving to HEAD~3
# def5678 HEAD@{1}: commit: add feature X
# ghi9012 HEAD@{2}: commit: add feature Y
# jkl3456 HEAD@{3}: commit: add feature Z
# mno7890 HEAD@{4}: checkout: moving from main to feature/new

# Step 2: Find the commit before the reset
# HEAD@{1} is the last commit before reset

# Step 3: Recover
git reset --hard HEAD@{1}     # Or use commit hash: git reset --hard def5678

# Step 4: Verify
git log --oneline             # Your commits are back!
```

## Psychological Impact

**Reflog changes your relationship with Git:**

**Before reflog:**

- "I hope I don't break anything"
- Avoid rebase, reset, force-push
- Fear of losing work
- Stuck with messy history

**After reflog:**

- "I can always fix it if I do"
- Confident use of advanced features
- Experiment freely
- Clean up history without fear

**This confidence enables:**

- Better commit hygiene (clean up with rebase)
- Faster workflows (reset when needed)
- Learning advanced features (safe to experiment)
- Professional Git practices (polish history before sharing)
