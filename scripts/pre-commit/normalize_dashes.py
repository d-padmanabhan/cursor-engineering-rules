#!/usr/bin/env -S uv run
"""
Normalize Unicode en and em dashes in text files.

The script reads each path supplied by pre-commit, validates that its content is
UTF-8, replaces en and em dashes with ASCII hyphens, and writes changed content
back without altering other bytes or line endings.

Workflow:
1. Read each supplied file as bytes.
2. Validate and decode the content as UTF-8.
3. Replace en and em dashes with ASCII hyphens.
4. Write only files whose content changed.

Usage:
    python scripts/pre-commit/normalize_dashes.py FILE [FILE ...]
"""

import sys
from pathlib import Path

DASH_TRANSLATION = str.maketrans({"\u2013": "-", "\u2014": "-"})


def normalize_file(path: Path) -> bool:
    """
    Replace en and em dashes in one UTF-8 file.

    Args:
        path (Path): File to normalize.

    Returns:
        bool: True when the file was changed; otherwise False.

    Raises:
        OSError: If the file cannot be read or written.
        UnicodeError: If the file is not valid UTF-8.
    """
    original = path.read_bytes()
    normalized = original.decode("utf-8").translate(DASH_TRANSLATION).encode("utf-8")

    if normalized == original:
        return False

    path.write_bytes(normalized)
    return True


def main(arguments: list[str] | None = None) -> int:
    """
    Normalize all supplied files.

    Args:
        arguments (list[str] | None): File paths. Defaults to command-line arguments.

    Returns:
        int: Zero on success or one when a file cannot be processed.
    """
    paths = sys.argv[1:] if arguments is None else arguments
    failed = False

    for filename in paths:
        path = Path(filename)
        try:
            if normalize_file(path):
                # pre-commit fails the run on its own when a hook edits a file;
                # naming the file tells the author what to review before staging.
                print(f"{path}: replaced Unicode dashes with ASCII hyphens", file=sys.stderr)
        except (OSError, UnicodeError) as error:
            print(f"{path}: {error}", file=sys.stderr)
            failed = True

    return int(failed)


if __name__ == "__main__":
    sys.exit(main())
