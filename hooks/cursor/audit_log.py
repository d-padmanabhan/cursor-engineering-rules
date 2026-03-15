#!/usr/bin/env python3
"""
Cursor hook script: write a redacted JSONL audit record for hook events.

This script is designed to be called by Cursor hooks (e.g., preToolUse) and is:
- dependency-free (stdlib only)
- safe-by-default (redacts common secret-like fields)
- resilient (always prints a JSON response)
"""

from __future__ import annotations

import json
import os
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REDACT_KEY_RE = re.compile(
    r"(token|secret|password|passwd|authorization|api[_-]?key|private[_-]?key)",
    re.IGNORECASE,
)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_load_stdin() -> dict[str, Any]:
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    try:
        data = json.loads(raw)
        if isinstance(data, dict):
            return data
    except Exception:
        pass
    return {"_raw": raw[:4096]}


def _redact(value: Any) -> Any:
    if isinstance(value, dict):
        redacted: dict[str, Any] = {}
        for k, v in value.items():
            if REDACT_KEY_RE.search(str(k)):
                redacted[k] = "***REDACTED***"
            else:
                redacted[k] = _redact(v)
        return redacted
    if isinstance(value, list):
        return [_redact(v) for v in value]
    if isinstance(value, str):
        if len(value) > 20000:
            return value[:20000] + "...<truncated>"
        return value
    return value


@dataclass(frozen=True)
class Output:
    # Cursor accepts a minimal output object. Returning {} is also OK.
    # We keep a stable shape to avoid accidental blocking.
    continue_: bool = True

    def to_json(self) -> str:
        return json.dumps({"continue": self.continue_})


def _default_log_path() -> Path:
    # User hooks run from ~/.cursor; project hooks run from repo root.
    # Prefer a local state directory if present, otherwise write under ~/.cursor.
    cwd = Path(os.getcwd())
    local_state = cwd / ".cursor" / "hooks" / "state"
    if (cwd / ".cursor").exists():
        return local_state / "hook-audit.jsonl"

    home = Path.home()
    return home / ".cursor" / "hooks" / "state" / "hook-audit.jsonl"


def main() -> int:
    payload = _safe_load_stdin()
    record = {
        "ts_utc": _now_iso(),
        "hook_event_name": payload.get("hook_event_name"),
        "tool_name": payload.get("tool_name"),
        "file_path": payload.get("file_path") or (payload.get("tool_input") or {}).get("file_path"),
        "cwd": payload.get("cwd"),
        "conversation_id": payload.get("conversation_id"),
        "generation_id": payload.get("generation_id"),
        "model": payload.get("model"),
        "payload": _redact(payload),
    }

    log_path = _default_log_path()
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

    sys.stdout.write(Output().to_json() + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
