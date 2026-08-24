"""Tests for the Unicode dash normalizer pre-commit hook."""

import subprocess
import sys
from pathlib import Path

SCRIPT_PATH = Path(__file__).parents[1] / "normalize_dashes.py"


def run_normalizer(*paths: Path) -> subprocess.CompletedProcess[str]:
    """
    Run the normalizer against temporary files.

    Args:
        *paths (Path): Files to pass to the normalizer.

    Returns:
        subprocess.CompletedProcess[str]: Captured process result.
    """
    return subprocess.run(
        [sys.executable, str(SCRIPT_PATH), *(str(path) for path in paths)],
        check=False,
        capture_output=True,
        text=True,
    )


def test_replaces_en_and_em_dashes(tmp_path: Path) -> None:
    """Replace every supported Unicode dash while preserving line endings."""
    text_file = tmp_path / "content.md"
    text_file.write_bytes("before\u2013after\r\none\u2014two\n".encode())

    result = run_normalizer(text_file)

    assert result.returncode == 0
    assert text_file.read_bytes() == b"before-after\r\none-two\n"


def test_leaves_unchanged_content_untouched(tmp_path: Path) -> None:
    """Leave a file unchanged when it contains no supported dashes."""
    text_file = tmp_path / "content.txt"
    original = b"plain ASCII content\n"
    text_file.write_bytes(original)

    result = run_normalizer(text_file)

    assert result.returncode == 0
    assert text_file.read_bytes() == original


def test_normalizes_multiple_files(tmp_path: Path) -> None:
    """Normalize every file supplied in one invocation."""
    first_file = tmp_path / "first.txt"
    second_file = tmp_path / "second.txt"
    first_file.write_text("first\u2014value", encoding="utf-8")
    second_file.write_text("second\u2013value", encoding="utf-8")

    result = run_normalizer(first_file, second_file)

    assert result.returncode == 0
    assert first_file.read_text(encoding="utf-8") == "first-value"
    assert second_file.read_text(encoding="utf-8") == "second-value"


def test_reports_non_utf8_file_without_modifying_it(tmp_path: Path) -> None:
    """Fail safely when a file is not valid UTF-8."""
    text_file = tmp_path / "invalid.txt"
    original = b"\xff\xfe\x00"
    text_file.write_bytes(original)

    result = run_normalizer(text_file)

    assert result.returncode == 1
    assert str(text_file) in result.stderr
    assert text_file.read_bytes() == original


def test_reports_missing_file_and_continues(tmp_path: Path) -> None:
    """Return failure while still processing later valid paths."""
    missing_file = tmp_path / "missing.txt"
    valid_file = tmp_path / "valid.txt"
    valid_file.write_text("value\u2014value", encoding="utf-8")

    result = run_normalizer(missing_file, valid_file)

    assert result.returncode == 1
    assert str(missing_file) in result.stderr
    assert valid_file.read_text(encoding="utf-8") == "value-value"
