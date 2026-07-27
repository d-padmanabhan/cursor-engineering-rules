#!/usr/bin/env -S uv run
"""Guard file contents before Cursor sends them to the model.

The hook is designed for ``beforeReadFile``. It denies common secret and
private-key files, rejects malformed hook input, and prevents very large
content payloads from entering model context.
"""

from pathlib import Path
from typing import Any

from hook_io import load_json_payload, write_json_decision

MAX_CONTENT_CHARACTERS: int = 2_000_000
SAFE_ENVIRONMENT_BASENAMES: frozenset[str] = frozenset({".env.example", ".env.sample", ".env.template"})
SENSITIVE_BASENAMES: frozenset[str] = frozenset(
    {
        "config.json",
        "credentials",
        "credentials.json",
        "id_ed25519",
        "id_rsa",
    }
)
SENSITIVE_SUFFIXES: frozenset[str] = frozenset(
    {
        ".kdb",
        ".key",
        ".keystore",
        ".mobileprovision",
        ".p12",
        ".pem",
        ".pfx",
    }
)


def deny_decision(user_message: str, agent_message: str) -> dict[str, Any]:
    """Create a deny response.

    Args:
        user_message: Concise reason shown to the user.
        agent_message: Remediation guidance returned to the agent.

    Returns:
        A JSON-serializable Cursor hook response.
    """
    return {
        "continue": True,
        "permission": "deny",
        "user_message": user_message,
        "agent_message": agent_message,
    }


def allow_decision() -> dict[str, Any]:
    """Create an allow response.

    Returns:
        A JSON-serializable Cursor hook response.
    """
    return {"continue": True, "permission": "allow"}


def sensitive_filename(basename: str) -> bool:
    """Return whether a case-normalized filename is sensitive.

    Args:
        basename: File basename normalized with :meth:`str.casefold`.

    Returns:
        ``True`` for secret-file families, private keys, and credential stores.
    """
    is_environment_file: bool = (
        basename == ".env" or basename.startswith(".env.")
    ) and basename not in SAFE_ENVIRONMENT_BASENAMES
    has_sensitive_suffix: bool = any(basename.endswith(suffix) for suffix in SENSITIVE_SUFFIXES)
    return is_environment_file or basename in SENSITIVE_BASENAMES or has_sensitive_suffix


def evaluate_read(payload: dict[str, Any]) -> dict[str, Any]:
    """Evaluate one file-read event.

    Args:
        payload: Validated Cursor hook payload.

    Returns:
        An allow or deny decision.
    """
    file_path_value: Any = payload.get("file_path")
    if not isinstance(file_path_value, str) or not file_path_value.strip():
        return deny_decision(
            user_message="Blocked file read because the path was missing or malformed",
            agent_message="Provide a valid file path before requesting a read.",
        )

    basename: str = Path(file_path_value).name
    normalized_basename: str = basename.casefold()
    if sensitive_filename(normalized_basename):
        return deny_decision(
            user_message=f"Blocked reading sensitive file: {basename}",
            agent_message=(
                f"Do not read or exfiltrate `{basename}`. Ask for a redacted "
                "snippet or use a committed sample such as `.env.example`."
            ),
        )

    content: Any = payload.get("content")
    if content is not None and not isinstance(content, str):
        return deny_decision(
            user_message="Blocked file read because content was malformed",
            agent_message="Retry with text content or a narrow text range.",
        )
    if isinstance(content, str) and len(content) > MAX_CONTENT_CHARACTERS:
        return deny_decision(
            user_message="Blocked reading very large file content",
            agent_message=(
                "Avoid sending very large or binary-like files to the model. "
                "Prefer specific ranges or summarize the file structure."
            ),
        )

    return allow_decision()


def main() -> int:
    """Read a file hook event, evaluate it, and emit a decision.

    Returns:
        Process exit code. Hook decisions use JSON and therefore return zero.
    """
    payload: dict[str, Any] | None = load_json_payload()
    if payload is None:
        write_json_decision(
            deny_decision(
                user_message="Blocked file read because hook input was malformed",
                agent_message="Retry with a valid beforeReadFile payload.",
            )
        )
        return 0

    write_json_decision(evaluate_read(payload))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
