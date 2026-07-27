## Cursor Hooks Pack

This directory contains **optional** hook scripts and example `hooks.json` configs for Cursor.

Hooks are deterministic programs that run at defined points in the agent loop and can block, allow, or modify actions.

### Requirements

- [uv](https://docs.astral.sh/uv/) available on `PATH`
- Python 3.14 or newer, managed through `uv`
- Hook scripts copied with executable mode

The scripts use only the Python standard library at runtime. Repository development tools are declared in [`pyproject.toml`](../../pyproject.toml) and locked in [`uv.lock`](../../uv.lock).

### Files

- `guard_before_shell.py`: Intended for `beforeShellExecution`
  - Denies obviously catastrophic delete commands
  - Asks for approval on remote writes / high-blast-radius commands
- `guard_before_read_file.py`: Intended for `beforeReadFile`
  - Denies reading common secret files (for example `.env`, private keys)
- `audit_log.py`: Intended for `preToolUse` (or other events)
  - Writes a bounded, redacted JSONL audit record to `.cursor/hooks/state/hook-audit.jsonl` (project) or `~/.cursor/hooks/state/hook-audit.jsonl` (user)
- `hook_io.py`: Shared fail-safe JSON input/output helpers used by both guard scripts
- `hooks.project.example.json`: Example project config (paths like `.cursor/hooks/...`)
- `hooks.user.example.json`: Example user config (paths like `./hooks/...`)

### Quick start (project)

From your repo root:

```bash
mkdir -p .cursor/hooks
cp -R /path/to/agent-engineering-handbook/hooks/cursor/*.py .cursor/hooks/
cp /path/to/agent-engineering-handbook/hooks/cursor/hooks.project.example.json .cursor/hooks.json
chmod +x .cursor/hooks/*.py
```

The example configuration executes each script directly. Its `uv run` shebang selects the declared Python runtime without requiring a project-specific virtual environment.

### Security model

These hooks are defense-in-depth controls, not a sandbox:

- Guard scripts reject malformed input instead of silently allowing it.
- Audit records redact common secret keys and values, bound untrusted data, and use `0700` directory and `0600` file permissions.
- Example configurations retain `"failClosed": false` so a missing runtime or broken optional hook does not disable Cursor. Organizations that treat hooks as mandatory policy enforcement should test the scripts in their environment and deliberately change this setting.
- Shell parsing is conservative but cannot prove arbitrary shell code safe. Remote-write authorization and normal code review remain required.

### Development

```bash
uv sync --dev
uv run ruff check hooks/cursor
uv run ruff check hooks/cursor/*.py --select D --config "lint.pydocstyle.convention='google'"
uv run ruff format --check hooks/cursor
uv run pylint hooks/cursor/*.py
uv run python -m unittest discover -s hooks/cursor/tests -v
```
