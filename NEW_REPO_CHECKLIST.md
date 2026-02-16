---
title: New Repo Setup Checklist
description: Quick checklist to wire Cursor rules and context templates into a repository.
---

# New Repo Setup Checklist

## Setup rules

- [ ] Add the rules (recommended: submodule + symlink):

```bash
git submodule add https://github.com/d-padmanabhan/cursor-engineering-rules.git .cursor-rules
mkdir -p .cursor
ln -s ../.cursor-rules/rules .cursor/rules
```

- [ ] Confirm `.cursor/rules` points where you expect:

```bash
ls -la .cursor/rules
readlink .cursor/rules
```

## Setup workspace context files

- [ ] Create `tmp/` (workspace-local, gitignored)
- [ ] Create `tmp/tasks.md` (minimum)

```bash
mkdir -p tmp
cp .cursor/rules/templates/tasks.md.template tmp/tasks.md
```

Optional (for complex work):

- [ ] `tmp/project-brief.md`
- [ ] `tmp/active-context.md`
- [ ] `tmp/progress.md`

```bash
cp .cursor/rules/templates/project-brief.md.template tmp/project-brief.md
cp .cursor/rules/templates/active-context.md.template tmp/active-context.md
cp .cursor/rules/templates/progress.md.template tmp/progress.md
```

## Git hygiene (recommended)

- [ ] Ensure `tmp/` is ignored (add to your repo’s `.gitignore`):

```gitignore
# Private/local documentation
tmp/
```
