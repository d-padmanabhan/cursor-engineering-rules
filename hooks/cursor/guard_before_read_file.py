#!/usr/bin/env python3
"""
Cursor hook script: guard before sending file contents to the model.

Designed for the `beforeReadFile` hook. It can deny reads of common secret files.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


DENY_BASENAMES = {
    ".env",
    ".env.local",
    ".env.development",
    ".env.test",
    ".env.production",
    "credentials",
    "credentials.json",
    "id_rsa",
    "id_ed25519",
    "config.json",
}

DENY_SUFFIXES = {
    ".pem",
    ".p12",
    ".pfx",
    ".key",
    ".keystore",
    ".kdb",
    ".mobileprovision",
}


def _load_payload() -> dict[str, Any]:
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    try:
        data = json.loads(raw)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _deny(user_message: str, agent_message: str) -> dict[str, Any]:
    return {
        "continue": True,
        "permission": "deny",
        "user_message": user_message,
        "agent_message": agent_message,
    }


def _allow() -> dict[str, Any]:
    return {"continue": True, "permission": "allow"}


def main() -> int:
    payload = _load_payload()
    file_path = str(payload.get("file_path") or "")
    basename = Path(file_path).name

    if basename in DENY_BASENAMES:
        out = _deny(
            user_message=f"Blocked reading sensitive file: {basename}",
            agent_message=(
                f"Do not read or exfiltrate `{basename}`. Ask the user to provide a redacted snippet or "
                "use a committed sample file (for example `.env.example`)."
            ),
        )
        sys.stdout.write(json.dumps(out) + "\n")
        return 0

    for suffix in DENY_SUFFIXES:
        if basename.endswith(suffix):
            out = _deny(
                user_message=f"Blocked reading sensitive file: *{suffix}",
                agent_message=(
                    f"Do not read private key / certificate material (`{basename}`). Ask for a redacted, "
                    "non-sensitive excerpt if needed."
                ),
            )
            sys.stdout.write(json.dumps(out) + "\n")
            return 0

    # Heuristic: block very large content payloads to avoid accidental binary-ish exfil.
    content = payload.get("content")
    if isinstance(content, str) and len(content) > 2_000_000:
        out = _deny(
            user_message="Blocked reading very large file content (likely binary or vendored)",
            agent_message=(
                "Avoid sending very large files to the model. Prefer narrow reads (specific ranges), "
                "or summarize structure without ingesting full content."
            ),
        )
        sys.stdout.write(json.dumps(out) + "\n")
        return 0

    sys.stdout.write(json.dumps(_allow()) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
