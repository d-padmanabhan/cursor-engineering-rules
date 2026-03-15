#!/usr/bin/env python3
"""
Cursor hook script: gate shell execution before it runs.

Designed for `beforeShellExecution`.
Policy is intentionally conservative:
- Deny only clearly catastrophic operations.
- Ask for approval on remote writes / high-blast-radius operations.
- Allow everything else.
"""

from __future__ import annotations

import json
import re
import shlex
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ASK_PATTERNS = [
    # git remote writes / history rewrites
    r"\bgit\s+push\b",
    r"\bgit\s+reset\s+--hard\b",
    r"\bgit\s+clean\s+-f",
    r"\bgit\s+rebase\b",
    # gh remote mutations
    r"\bgh\s+pr\s+create\b",
    r"\bgh\s+pr\s+merge\b",
    r"\bgh\s+repo\s+sync\b",
    r"\bgh\s+api\s+(post|patch|put|delete)\b",
    # infra mutations
    r"\bterraform\s+apply\b",
    r"\bterraform\s+destroy\b",
    r"\bterragrunt\s+apply\b",
    r"\bterragrunt\s+destroy\b",
    r"\bkubectl\s+apply\b",
    r"\bkubectl\s+delete\b",
    r"\bhelm\s+upgrade\b",
    r"\bhelm\s+uninstall\b",
    # cloud mutations (best-effort)
    r"\baws\s+cloudformation\s+deploy\b",
    r"\baws\s+cloudformation\s+delete-stack\b",
    r"\baws\s+s3\s+rm\b",
    r"\baws\s+s3api\s+delete-",
]

DENY_PATTERNS = [
    r"(^|\s)rm\s+-rf\s+/$",
    r"(^|\s)rm\s+-rf\s+/\*$",
    r"(^|\s)rm\s+-rf\s+~\s*$",
    r"(^|\s)rm\s+-rf\s+\$\{?HOME\}?\s*$",
]


def _load_payload() -> dict[str, Any]:
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    try:
        data = json.loads(raw)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


@dataclass(frozen=True)
class Decision:
    permission: str
    user_message: str | None = None
    agent_message: str | None = None
    continue_: bool = True

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {"continue": self.continue_, "permission": self.permission}
        if self.user_message:
            out["user_message"] = self.user_message
        if self.agent_message:
            out["agent_message"] = self.agent_message
        return out


def _normalize_command(command: str) -> str:
    return " ".join(command.strip().split())


def _looks_catastrophic_rm(command: str) -> bool:
    # Prefer a stricter parse than regex when possible.
    try:
        argv = shlex.split(command)
    except ValueError:
        argv = []

    if not argv or argv[0] != "rm":
        return False

    flags = {a for a in argv[1:] if a.startswith("-")}
    paths = [a for a in argv[1:] if not a.startswith("-")]
    if not paths:
        return False

    has_recursive = any("r" in f for f in flags) or "--recursive" in flags
    has_force = any("f" in f for f in flags) or "--force" in flags
    if not (has_recursive and has_force):
        return False

    catastrophic = {"/", "/*", "~", "${HOME}", "$HOME", str(Path.home())}
    return any(p in catastrophic for p in paths)


def main() -> int:
    payload = _load_payload()
    command = _normalize_command(str(payload.get("command") or ""))

    if not command:
        sys.stdout.write(json.dumps(Decision(permission="allow").to_dict()) + "\n")
        return 0

    if _looks_catastrophic_rm(command) or any(re.search(p, command) for p in DENY_PATTERNS):
        decision = Decision(
            permission="deny",
            user_message="Blocked catastrophic delete command",
            agent_message=(
                "This command looks like it could delete critical filesystem paths. "
                "Refuse to run it and propose a safer alternative with explicit, narrow paths."
            ),
        )
        sys.stdout.write(json.dumps(decision.to_dict()) + "\n")
        return 0

    for pattern in ASK_PATTERNS:
        if re.search(pattern, command):
            decision = Decision(
                permission="ask",
                user_message=f"Approval required for: {command}",
                agent_message=(
                    "This command is a remote write / destructive / high-blast-radius operation. "
                    "Explain impact, show a safer dry-run if available, and wait for explicit approval."
                ),
            )
            sys.stdout.write(json.dumps(decision.to_dict()) + "\n")
            return 0

    sys.stdout.write(json.dumps(Decision(permission="allow").to_dict()) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
