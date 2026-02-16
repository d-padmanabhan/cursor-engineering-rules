---
title: Setup Guide
description: Setup Cursor rules + workspace context templates using symlinks or submodules.
---

# Setup Guide

This repo is designed to be used across many projects via a **shared rules directory** (symlink/submodule). Workspace context files stay **workspace-local** under `tmp/` (gitignored).

## Recommended setup (team)

Use a git submodule in your project and symlink Cursor’s rules directory to it:

```bash
git submodule add https://github.com/d-padmanabhan/cursor-engineering-rules.git .cursor-rules
mkdir -p .cursor
ln -s ../.cursor-rules/rules .cursor/rules
```

## Recommended setup (personal)

Clone once somewhere stable and symlink `.cursor/rules` in each project:

```bash
git clone https://github.com/d-padmanabhan/cursor-engineering-rules.git ~/cursor-engineering-rules
mkdir -p .cursor
ln -s ~/cursor-engineering-rules/rules .cursor/rules
```

## Using the setup scripts

From your project root:

```bash
/path/to/cursor-engineering-rules/setup-workspace.sh -S -l .
```

Or for many repos at once:

```bash
/path/to/cursor-engineering-rules/setup-all-repos.sh -S -l ~/parent-workspace
```

## Context files and templates

Templates live at:

- `.cursor/rules/templates/` (when installed via symlink/submodule)
- `rules/templates/` (in this repo)

Workspace context files should live at:

- `tmp/tasks.md`
- `tmp/active-context.md`
- `tmp/progress.md`
- `tmp/project-brief.md`

See `rules/050-workflow.mdc` for the workflow and file meanings.
