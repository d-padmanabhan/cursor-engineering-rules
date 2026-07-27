#!/usr/bin/env -S uv run
"""Write a bounded, redacted JSONL audit record for Cursor hook events.

The hook is intended for ``preToolUse`` and related events. It uses only the
standard library, bounds untrusted payload traversal, redacts key- and
value-based secret patterns, creates private audit files, and always emits a
stable non-blocking Cursor response even when persistence fails.
"""

import json
import os
import re
import sys
from datetime import UTC, datetime
from itertools import islice
from pathlib import Path
from typing import Any

MAX_COLLECTION_ITEMS: int = 100
MAX_DEPTH: int = 8
MAX_RAW_INPUT_CHARACTERS: int = 4_096
MAX_RECORD_BYTES: int = 131_072
MAX_STRING_CHARACTERS: int = 20_000
REDACTED_VALUE: str = "***REDACTED***"
REDACT_KEY_PATTERN = re.compile(
    r"(?:token|secret|password|passwd|authorization|api[_-]?key|private[_-]?key)",
    re.IGNORECASE,
)
REDACT_VALUE_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"(?i)\b(bearer)\s+[A-Za-z0-9._~+/=-]+"),
    re.compile(
        r"(?i)\b(authorization)[\"']?(\s*[:=]\s*)(?:bearer\s+)?"
        r"(?:\"[^\"]*(?:\"|$)|'[^']*(?:'|$)|[^\s,;]+)"
    ),
    re.compile(
        r"(?i)\b("
        r"api[_-]?key|access[_-]?(?:key|token)|client[_-]?secret|"
        r"password|passwd|[A-Z][A-Z0-9_]*(?:KEY|TOKEN|SECRET|PASSWORD|PASSWD)"
        r")[\"']?(\s*[:=]\s*)"
        r"(?:\"[^\"]*(?:\"|$)|'[^']*(?:'|$)|[^\s,;]+)"
    ),
    re.compile(
        r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?"
        r"-----END [A-Z ]*PRIVATE KEY-----",
        re.DOTALL,
    ),
)


def current_time_iso() -> str:
    """Return the current UTC timestamp in ISO 8601 format."""
    return datetime.now(UTC).isoformat()


def load_payload() -> dict[str, Any]:
    """Read a JSON object while preserving bounded malformed input evidence.

    Returns:
        The decoded object, or a bounded marker for absent or malformed input.
    """
    try:
        raw_payload: str = sys.stdin.read(MAX_RECORD_BYTES + 1)
    except OSError as error:
        return {"input_error": type(error).__name__}
    if not raw_payload.strip():
        return {"input_error": "empty_input"}
    if len(raw_payload) > MAX_RECORD_BYTES:
        return {
            "input_error": "input_too_large",
            "input_characters_at_least": len(raw_payload),
        }
    try:
        payload: Any = json.loads(raw_payload)
    except json.JSONDecodeError:
        return {
            "input_error": "invalid_json",
            "raw_excerpt": redact_string(raw_payload[:MAX_RAW_INPUT_CHARACTERS]),
        }
    if not isinstance(payload, dict):
        return {"input_error": "root_not_object"}
    return payload


def redact_string(value: str) -> str:
    """Redact common credential shapes and bound string length.

    Args:
        value: Untrusted string from a hook payload.

    Returns:
        A redacted and length-bounded string.
    """
    redacted_value: str = value
    for pattern in REDACT_VALUE_PATTERNS:
        if "PRIVATE KEY" in pattern.pattern:
            redacted_value = pattern.sub("[REDACTED PRIVATE KEY]", redacted_value)
        else:
            redacted_value = pattern.sub(
                lambda match: (
                    f"{match.group(1)}{match.group(2)}{REDACTED_VALUE}"
                    if match.lastindex and match.lastindex >= 2
                    else f"{match.group(1)} {REDACTED_VALUE}"
                ),
                redacted_value,
            )
    if len(redacted_value) > MAX_STRING_CHARACTERS:
        return redacted_value[:MAX_STRING_CHARACTERS] + "...<truncated>"
    return redacted_value


def redact_value(value: Any, depth: int = 0) -> Any:
    """Recursively redact and bound untrusted JSON-compatible data.

    Args:
        value: Payload value to sanitize.
        depth: Current traversal depth.

    Returns:
        A JSON-compatible bounded and redacted value.
    """
    if depth >= MAX_DEPTH:
        return "<max-depth-reached>"
    if isinstance(value, dict):
        redacted_mapping: dict[str, Any] = {}
        items: list[tuple[Any, Any]] = list(islice(value.items(), MAX_COLLECTION_ITEMS))
        for raw_key, item in items:
            key: str = redact_string(str(raw_key))
            redacted_mapping[key] = REDACTED_VALUE if REDACT_KEY_PATTERN.search(key) else redact_value(item, depth + 1)
        if len(value) > MAX_COLLECTION_ITEMS:
            redacted_mapping["<truncated-items>"] = len(value) - MAX_COLLECTION_ITEMS
        return redacted_mapping
    if isinstance(value, list):
        redacted_items: list[Any] = [redact_value(item, depth + 1) for item in value[:MAX_COLLECTION_ITEMS]]
        if len(value) > MAX_COLLECTION_ITEMS:
            redacted_items.append({"<truncated-items>": len(value) - MAX_COLLECTION_ITEMS})
        return redacted_items
    if isinstance(value, str):
        return redact_string(value)
    if value is None or isinstance(value, (bool, float, int)):
        return value
    return redact_string(repr(value))


def bounded_string(value: Any) -> str | None:
    """Return a bounded scalar string for an audit index field.

    Args:
        value: Candidate field value.

    Returns:
        A sanitized string, or ``None`` for unsupported values.
    """
    if value is None:
        return None
    if isinstance(value, (bool, float, int, str)):
        return redact_string(str(value))
    return None


def default_log_path() -> Path:
    """Resolve the project or user audit-log path.

    Returns:
        Project-local state when ``.cursor`` exists, otherwise user state.
    """
    override: str | None = os.environ.get("CURSOR_HOOK_AUDIT_LOG")
    if override:
        return Path(override).expanduser()

    working_directory: Path = Path.cwd()
    if (working_directory / ".cursor").exists():
        return working_directory / ".cursor" / "hooks" / "state" / "hook-audit.jsonl"
    return Path.home() / ".cursor" / "hooks" / "state" / "hook-audit.jsonl"


def build_record(payload: dict[str, Any]) -> dict[str, Any]:
    """Build a bounded audit record from a validated payload.

    Args:
        payload: Parsed hook payload.

    Returns:
        Sanitized audit record.
    """
    tool_input_value: Any = payload.get("tool_input")
    tool_input: dict[str, Any] = tool_input_value if isinstance(tool_input_value, dict) else {}
    file_path: Any = payload.get("file_path") or tool_input.get("file_path")
    return {
        "ts_utc": current_time_iso(),
        "hook_event_name": bounded_string(payload.get("hook_event_name")),
        "tool_name": bounded_string(payload.get("tool_name")),
        "file_path": bounded_string(file_path),
        "cwd": bounded_string(payload.get("cwd")),
        "conversation_id": bounded_string(payload.get("conversation_id")),
        "generation_id": bounded_string(payload.get("generation_id")),
        "model": bounded_string(payload.get("model")),
        "payload": redact_value(payload),
    }


def serialize_record(record: dict[str, Any]) -> bytes:
    """Serialize an audit record within the configured byte limit.

    Args:
        record: Sanitized audit record.

    Returns:
        One UTF-8 JSONL record.
    """
    serialized_record: bytes = json.dumps(record, ensure_ascii=False, separators=(",", ":")).encode("utf-8") + b"\n"
    if len(serialized_record) <= MAX_RECORD_BYTES:
        return serialized_record

    fallback_record: dict[str, Any] = {
        "ts_utc": record["ts_utc"],
        "hook_event_name": record["hook_event_name"],
        "tool_name": record["tool_name"],
        "file_path": record["file_path"],
        "payload": {
            "input_error": "redacted_record_exceeded_limit",
            "record_bytes": len(serialized_record),
        },
    }
    return json.dumps(fallback_record, ensure_ascii=False, separators=(",", ":")).encode("utf-8") + b"\n"


def append_record(log_path: Path, serialized_record: bytes) -> None:
    """Append one record using private directory and file permissions.

    Args:
        log_path: Destination JSONL path.
        serialized_record: Fully serialized single-line record.
    """
    log_path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    os.chmod(log_path.parent, 0o700)
    file_descriptor: int = os.open(
        log_path,
        os.O_APPEND | os.O_CREAT | os.O_WRONLY,
        0o600,
    )
    try:
        os.chmod(log_path, 0o600)
        remaining_record: memoryview = memoryview(serialized_record)
        while remaining_record:
            bytes_written: int = os.write(file_descriptor, remaining_record)
            if bytes_written == 0:
                raise OSError("audit log write made no progress")
            remaining_record = remaining_record[bytes_written:]
    finally:
        os.close(file_descriptor)


def write_response() -> None:
    """Write the stable non-blocking Cursor response."""
    sys.stdout.write('{"continue":true}\n')


def main() -> int:
    """Read, sanitize, and persist one audit event.

    Returns:
        Process exit code. Persistence failures are reported on standard error
        while the hook response remains non-blocking.
    """
    payload: dict[str, Any] = load_payload()
    record: dict[str, Any] = build_record(payload)
    try:
        append_record(default_log_path(), serialize_record(record))
    except OSError as error:
        sys.stderr.write(f"Cursor hook audit write failed: {type(error).__name__}\n")
    write_response()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
