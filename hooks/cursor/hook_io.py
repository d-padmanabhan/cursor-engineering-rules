"""Shared JSON input and output helpers for Cursor guard hooks."""

import json
import sys
from typing import Any


def load_json_payload() -> dict[str, Any] | None:
    """Read and validate one JSON object from standard input.

    Returns:
        The decoded object, or ``None`` when input is absent or malformed.
    """
    try:
        raw_payload: str = sys.stdin.read()
    except OSError:
        return None
    if not raw_payload.strip():
        return None
    try:
        payload: Any = json.loads(raw_payload)
    except json.JSONDecodeError:
        return None
    return payload if isinstance(payload, dict) else None


def write_json_decision(decision: dict[str, Any]) -> None:
    """Write one JSON decision to standard output.

    Args:
        decision: Cursor hook response.
    """
    sys.stdout.write(json.dumps(decision) + "\n")
