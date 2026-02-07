# Syncing folders between Git repos (rsync)

Use `rsync` to copy a sub-tree from one repo to another while preserving permissions and minimizing churn.

> [!IMPORTANT]
> Use `--dry-run` first. Be very careful with `--delete`.

---

## Safe default command

```bash
rsync -a --human-readable --itemize-changes --dry-run \
  --exclude '.git/' \
  /path/to/source-repo/subdir/ \
  /path/to/dest-repo/subdir/
```

Notes:

- Trailing slash on the source (`subdir/`) means “copy contents”
- Omit trailing slash (`subdir`) means “copy the directory itself”

---

## Make it real (after review)

Remove `--dry-run`:

```bash
rsync -a --human-readable --itemize-changes \
  --exclude '.git/' \
  /path/to/source-repo/subdir/ \
  /path/to/dest-repo/subdir/
```

---

## Mirror mode (dangerous)

Mirror destination to match source:

```bash
rsync -a --human-readable --itemize-changes --delete --dry-run \
  --exclude '.git/' \
  /path/to/source-repo/subdir/ \
  /path/to/dest-repo/subdir/
```

> [!WARNING]
> `--delete` removes files in the destination that are not present in the source. Always dry-run and inspect output.
