"""Validate and evaluate Agent Skills with deterministic, portable checks.

The module provides two commands:

1. ``validate`` checks skill metadata and every discovered ``evals/evals.json``.
2. ``run`` executes pilot cases with and without a skill through an external
   adapter, scores deterministic checks, and writes benchmark artifacts.

The adapter is an executable that accepts one JSON request on standard input
and returns one JSON response on standard output. It is invoked without a
shell so command text cannot be interpreted as shell syntax.

Usage:
    uv run python -m evals.skill_eval validate
    uv run python -m evals.skill_eval run --adapter /path/to/adapter
"""

import argparse
import dataclasses
import datetime
import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any

PROTOCOL_VERSION = 1
ALLOWED_CHECK_TYPES = frozenset(
    {
        "contains",
        "contains_all",
        "contains_any",
        "not_contains",
        "not_regex",
        "regex",
        "file_exists",
        "loaded_skill",
    }
)
SAFE_IDENTIFIER_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]*$")
SAFE_RUN_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
SENSITIVE_KEY_PATTERN = re.compile(
    r"(?i)(?:api[_-]?key|authorization|access[_-]?token|client[_-]?secret|"
    r"password|private[_-]?key|refresh[_-]?token)"
)
SECRET_PATTERNS = (
    re.compile(r"(?i)\b(bearer)\s+[A-Za-z0-9._~+/=-]+"),
    re.compile(
        r"(?i)\b(api[_-]?key|access[_-]?token|client[_-]?secret|password)"
        r"(\s*[:=]\s*)[^\s,\"']+"
    ),
    re.compile(
        r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?"
        r"-----END [A-Z ]*PRIVATE KEY-----",
        re.DOTALL,
    ),
)


class ValidationFailure(ValueError):
    """Raised when repository or eval data violates the local contract."""


class AdapterFailure(RuntimeError):
    """Raised when an agent adapter cannot produce a valid response."""


@dataclasses.dataclass(frozen=True)
class EvalCase:
    """One normalized eval case loaded from ``evals.json``."""

    identifier: int
    prompt: str
    expected_output: str
    assertions: tuple[str, ...]
    files: tuple[Path, ...]
    checks: tuple[dict[str, Any], ...]


@dataclasses.dataclass(frozen=True)
class EvalSuite:
    """A skill and its normalized eval cases."""

    skill_name: str
    skill_directory: Path
    eval_directory: Path
    cases: tuple[EvalCase, ...]


@dataclasses.dataclass(frozen=True)
class AdapterResponse:
    """Normalized response returned by an external agent adapter."""

    output: str
    events: tuple[dict[str, Any], ...]
    usage: dict[str, int | float]
    raw: dict[str, Any]


@dataclasses.dataclass(frozen=True)
class CheckResult:
    """Result of one deterministic assertion."""

    identifier: str
    check_type: str
    required: bool
    passed: bool
    message: str


@dataclasses.dataclass(frozen=True)
class ModeResult:
    """Scored result for one eval case and execution mode."""

    mode: str
    response: AdapterResponse
    checks: tuple[CheckResult, ...]
    duration_seconds: float
    workspace_files: tuple[str, ...]

    @property
    def passed(self) -> bool:
        """Return whether every required check passed."""

        return all(check.passed for check in self.checks if check.required)


def repository_root(start: Path | None = None) -> Path:
    """Resolve the handbook root from this module or a caller-provided path."""

    candidate = (start or Path(__file__).resolve().parent.parent).resolve()
    if not (candidate / "skills").is_dir():
        raise ValidationFailure(f"Repository root has no skills directory: {candidate}")
    return candidate


def parse_frontmatter(skill_file: Path) -> dict[str, str]:
    """Parse the small YAML subset used by Agent Skills frontmatter."""

    try:
        lines = skill_file.read_text(encoding="utf-8").splitlines()
    except OSError as error:
        raise ValidationFailure(f"Cannot read {skill_file}: {error}") from error

    if not lines or lines[0].strip() != "---":
        raise ValidationFailure(f"{skill_file}: missing opening frontmatter delimiter")

    try:
        closing_index = next(index for index, line in enumerate(lines[1:], start=1) if line.strip() == "---")
    except StopIteration as error:
        raise ValidationFailure(f"{skill_file}: missing closing frontmatter delimiter") from error

    metadata: dict[str, str] = {}
    current_key: str | None = None
    folded_values: list[str] = []

    def commit_folded_value() -> None:
        nonlocal current_key, folded_values
        if current_key is not None:
            metadata[current_key] = " ".join(folded_values).strip()
        current_key = None
        folded_values = []

    for line in lines[1:closing_index]:
        if line.startswith((" ", "\t")):
            if current_key is not None:
                folded_values.append(line.strip())
            # Other nested YAML fields are outside the metadata subset needed here.
            continue

        commit_folded_value()
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            raise ValidationFailure(f"{skill_file}: unsupported frontmatter line: {line!r}")

        key, raw_value = line.split(":", 1)
        key = key.strip()
        value = raw_value.strip()
        if value in {">", ">-", "|", "|-"}:
            current_key = key
            continue
        metadata[key] = value.strip("\"'")

    commit_folded_value()
    return metadata


def validate_skill_metadata(skills_directory: Path) -> list[str]:
    """Validate every immediate child skill and return discovered names."""

    errors: list[str] = []
    names: list[str] = []
    for skill_directory in sorted(path for path in skills_directory.iterdir() if path.is_dir()):
        if skill_directory.is_symlink():
            errors.append(f"{skill_directory}: skill directories cannot be symlinks")
            continue
        skill_file = skill_directory / "SKILL.md"
        if not skill_file.is_file():
            errors.append(f"{skill_directory}: missing SKILL.md")
            continue
        symlinks = sorted(path for path in skill_directory.rglob("*") if path.is_symlink())
        if symlinks:
            errors.extend(f"{path}: symlinks are not allowed in skill packages" for path in symlinks)
            continue

        try:
            metadata = parse_frontmatter(skill_file)
        except ValidationFailure as error:
            errors.append(str(error))
            continue

        name = metadata.get("name", "")
        description = metadata.get("description", "")
        if not name:
            errors.append(f"{skill_file}: frontmatter name is required")
        elif not SAFE_IDENTIFIER_PATTERN.fullmatch(name):
            errors.append(f"{skill_file}: invalid skill name {name!r}")
        elif len(name) > 64:
            errors.append(f"{skill_file}: skill name exceeds 64 characters")
        elif "--" in name:
            errors.append(f"{skill_file}: skill name cannot contain consecutive hyphens")
        elif name != skill_directory.name:
            errors.append(f"{skill_file}: name {name!r} does not match directory {skill_directory.name!r}")
        else:
            names.append(name)

        if not description:
            errors.append(f"{skill_file}: frontmatter description is required")
        elif len(description) > 1024:
            errors.append(f"{skill_file}: description exceeds 1024 characters")

    if errors:
        raise ValidationFailure("\n".join(errors))
    return names


def load_eval_suite(skill_directory: Path) -> EvalSuite | None:
    """Load and validate a skill's optional ``evals/evals.json``."""

    eval_directory = skill_directory / "evals"
    eval_file = eval_directory / "evals.json"
    if not eval_file.exists():
        return None

    try:
        payload = json.loads(eval_file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValidationFailure(f"{eval_file}: invalid JSON: {error}") from error

    if not isinstance(payload, dict):
        raise ValidationFailure(f"{eval_file}: root must be an object")

    skill_name = payload.get("skill_name")
    if skill_name != skill_directory.name:
        raise ValidationFailure(f"{eval_file}: skill_name {skill_name!r} must match {skill_directory.name!r}")

    raw_cases = payload.get("evals")
    if not isinstance(raw_cases, list) or not raw_cases:
        raise ValidationFailure(f"{eval_file}: evals must be a non-empty array")

    cases: list[EvalCase] = []
    identifiers: set[int] = set()
    for index, raw_case in enumerate(raw_cases):
        case_location = f"{eval_file}: evals[{index}]"
        if not isinstance(raw_case, dict):
            raise ValidationFailure(f"{case_location} must be an object")

        identifier = raw_case.get("id")
        if not isinstance(identifier, int) or isinstance(identifier, bool) or identifier < 1:
            raise ValidationFailure(f"{case_location}.id must be a positive integer")
        if identifier in identifiers:
            raise ValidationFailure(f"{case_location}.id duplicates {identifier}")
        identifiers.add(identifier)

        prompt = require_nonempty_string(raw_case, "prompt", case_location)
        expected_output = require_nonempty_string(raw_case, "expected_output", case_location)
        raw_assertions = raw_case.get("assertions", [])
        if not isinstance(raw_assertions, list) or any(
            not isinstance(assertion, str) or not assertion.strip() for assertion in raw_assertions
        ):
            raise ValidationFailure(f"{case_location}.assertions must be an array of non-empty strings")
        files = validate_fixture_paths(raw_case.get("files", []), skill_directory, case_location)
        checks = validate_checks(raw_case.get("checks", []), case_location)

        cases.append(
            EvalCase(
                identifier=identifier,
                prompt=prompt,
                expected_output=expected_output,
                assertions=tuple(raw_assertions),
                files=tuple(files),
                checks=tuple(checks),
            )
        )

    return EvalSuite(
        skill_name=skill_directory.name,
        skill_directory=skill_directory,
        eval_directory=eval_directory,
        cases=tuple(cases),
    )


def require_nonempty_string(payload: Mapping[str, Any], key: str, location: str) -> str:
    """Read a required non-empty string field."""

    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValidationFailure(f"{location}.{key} must be a non-empty string")
    return value


def validate_fixture_paths(raw_files: Any, skill_directory: Path, location: str) -> list[Path]:
    """Validate skill-root-relative fixture paths and prevent traversal."""

    if not isinstance(raw_files, list) or any(not isinstance(item, str) or not item for item in raw_files):
        raise ValidationFailure(f"{location}.files must be an array of paths")

    skill_root = skill_directory.resolve()
    files: list[Path] = []
    for raw_path in raw_files:
        candidate = (skill_directory / raw_path).resolve()
        if not candidate.is_relative_to(skill_root):
            raise ValidationFailure(f"{location}.files path escapes skill directory: {raw_path}")
        if not candidate.is_file():
            raise ValidationFailure(f"{location}.files path does not exist: {raw_path}")
        files.append(candidate)
    return files


def validate_checks(raw_checks: Any, location: str) -> list[dict[str, Any]]:
    """Validate deterministic check definitions."""

    if not isinstance(raw_checks, list):
        raise ValidationFailure(f"{location}.checks must be an array")

    checks: list[dict[str, Any]] = []
    identifiers: set[str] = set()
    for index, raw_check in enumerate(raw_checks):
        check_location = f"{location}.checks[{index}]"
        if not isinstance(raw_check, dict):
            raise ValidationFailure(f"{check_location} must be an object")

        identifier = require_nonempty_string(raw_check, "id", check_location)
        if identifier in identifiers:
            raise ValidationFailure(f"{check_location}.id duplicates {identifier!r}")
        identifiers.add(identifier)

        check_type = require_nonempty_string(raw_check, "type", check_location)
        if check_type not in ALLOWED_CHECK_TYPES:
            raise ValidationFailure(f"{check_location}.type {check_type!r} is unsupported")

        required = raw_check.get("required", True)
        if not isinstance(required, bool):
            raise ValidationFailure(f"{check_location}.required must be a boolean")
        case_sensitive = raw_check.get("case_sensitive", False)
        if not isinstance(case_sensitive, bool):
            raise ValidationFailure(f"{check_location}.case_sensitive must be a boolean")

        normalized = dict(raw_check)
        normalized["required"] = required
        normalized["case_sensitive"] = case_sensitive
        if check_type in {"contains", "not_contains"}:
            require_nonempty_string(raw_check, "value", check_location)
        elif check_type in {"contains_all", "contains_any"}:
            values = raw_check.get("values")
            if (
                not isinstance(values, list)
                or not values
                or any(not isinstance(value, str) or not value for value in values)
            ):
                raise ValidationFailure(f"{check_location}.values must be a non-empty string array")
        elif check_type in {"regex", "not_regex"}:
            pattern = require_nonempty_string(raw_check, "pattern", check_location)
            try:
                re.compile(pattern)
            except re.error as error:
                raise ValidationFailure(f"{check_location}.pattern is invalid: {error}") from error
        elif check_type == "file_exists":
            path = require_nonempty_string(raw_check, "path", check_location)
            if Path(path).is_absolute() or ".." in Path(path).parts:
                raise ValidationFailure(f"{check_location}.path must stay inside the workspace")
        elif check_type == "loaded_skill":
            skill = raw_check.get("skill")
            if skill is not None and (not isinstance(skill, str) or not SAFE_IDENTIFIER_PATTERN.fullmatch(skill)):
                raise ValidationFailure(f"{check_location}.skill must be a valid skill name")

        checks.append(normalized)
    return checks


def validate_repository(root: Path) -> list[EvalSuite]:
    """Validate all skills and discovered eval suites."""

    skills_directory = root / "skills"
    validate_skill_metadata(skills_directory)
    suites = [
        suite
        for skill_directory in sorted(path for path in skills_directory.iterdir() if path.is_dir())
        if (suite := load_eval_suite(skill_directory)) is not None
    ]
    return suites


def copy_case_workspace(
    suite: EvalSuite, case: EvalCase, workspace: Path, mode: str
) -> tuple[list[dict[str, str]], Path | None]:
    """Create an isolated workspace with equal fixtures for both modes."""

    input_directory = workspace / "inputs"
    input_directory.mkdir(parents=True)
    copied_files: list[dict[str, str]] = []
    for fixture in case.files:
        relative_path = fixture.relative_to(suite.skill_directory)
        destination = input_directory / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(fixture, destination)
        copied_files.append(
            {
                "path": str(destination.relative_to(workspace)),
                "sha256": hashlib.sha256(destination.read_bytes()).hexdigest(),
            }
        )

    installed_skill: Path | None = None
    if mode == "with_skill":
        symlinks = [path for path in suite.skill_directory.rglob("*") if path.is_symlink()]
        if symlinks:
            raise ValidationFailure(f"Skill package contains prohibited symlink: {symlinks[0]}")
        installed_skill = workspace / "skills" / suite.skill_name
        shutil.copytree(
            suite.skill_directory,
            installed_skill,
            ignore=shutil.ignore_patterns("evals", "__pycache__"),
        )

    return copied_files, installed_skill


def run_adapter(
    command: Sequence[str],
    request: Mapping[str, Any],
    timeout_seconds: float,
    max_output_bytes: int,
    working_directory: Path | None = None,
) -> AdapterResponse:
    """Invoke an adapter without a shell and validate its response envelope."""

    if not command:
        raise AdapterFailure("Adapter command cannot be empty")

    started_at = time.monotonic()
    with (
        tempfile.TemporaryFile() as stdin_file,
        tempfile.TemporaryFile() as stdout_file,
        tempfile.TemporaryFile() as stderr_file,
    ):
        stdin_file.write(json.dumps(request).encode("utf-8"))
        stdin_file.seek(0)
        try:
            process = subprocess.Popen(
                list(command),
                stdin=stdin_file,
                stdout=stdout_file,
                stderr=stderr_file,
                cwd=working_directory,
                shell=False,
                env=os.environ.copy(),
                start_new_session=os.name == "posix",
            )
        except OSError as error:
            raise AdapterFailure(f"Cannot execute adapter {command[0]!r}: {error}") from error

        deadline = started_at + timeout_seconds
        while process.poll() is None:
            stdout_size = stream_size(stdout_file)
            stderr_size = stream_size(stderr_file)
            if stdout_size > max_output_bytes or stderr_size > max_output_bytes:
                terminate_adapter_process(process)
                raise AdapterFailure(
                    f"Adapter output exceeded {max_output_bytes} bytes (stdout={stdout_size}, stderr={stderr_size})"
                )
            if time.monotonic() >= deadline:
                terminate_adapter_process(process)
                raise AdapterFailure(f"Adapter timed out after {timeout_seconds:.1f} seconds")
            time.sleep(0.01)

        stdout_size = stream_size(stdout_file)
        stderr_size = stream_size(stderr_file)
        if stdout_size > max_output_bytes or stderr_size > max_output_bytes:
            raise AdapterFailure(
                f"Adapter output exceeded {max_output_bytes} bytes (stdout={stdout_size}, stderr={stderr_size})"
            )
        stdout = read_stream(stdout_file)
        stderr = read_stream(stderr_file)

    if process.returncode != 0:
        raise AdapterFailure(
            f"Adapter exited with {process.returncode} after "
            f"{time.monotonic() - started_at:.3f}s: {redact_text(stderr.strip())}"
        )

    try:
        payload = json.loads(stdout)
    except json.JSONDecodeError as error:
        raise AdapterFailure(f"Adapter stdout is not valid JSON: {error}") from error
    if not isinstance(payload, dict):
        raise AdapterFailure("Adapter response must be a JSON object")
    unknown_fields = sorted(payload.keys() - {"output", "events", "usage"})
    if unknown_fields:
        raise AdapterFailure(
            "Adapter response contains unsupported fields: " + ", ".join(str(field) for field in unknown_fields)
        )

    output = payload.get("output")
    events = payload.get("events", [])
    usage = payload.get("usage", {})
    if not isinstance(output, str):
        raise AdapterFailure("Adapter response output must be a string")
    if not isinstance(events, list) or any(not isinstance(event, dict) for event in events):
        raise AdapterFailure("Adapter response events must be an array of objects")
    normalized_events: list[dict[str, Any]] = []
    for event in events:
        unknown_event_fields = sorted(event.keys() - {"type", "name"})
        if unknown_event_fields:
            raise AdapterFailure(
                "Adapter event contains unsupported fields: " + ", ".join(str(field) for field in unknown_event_fields)
            )
        event_type = event.get("type")
        event_name = event.get("name")
        if not isinstance(event_type, str) or not event_type:
            raise AdapterFailure("Adapter event type must be a non-empty string")
        if event_name is not None and not isinstance(event_name, str):
            raise AdapterFailure("Adapter event name must be a string when present")
        normalized_event = {"type": event_type}
        if event_name is not None:
            normalized_event["name"] = event_name
        normalized_events.append(normalized_event)
    if not isinstance(usage, dict) or any(
        not isinstance(key, str) or not isinstance(value, (int, float)) or isinstance(value, bool)
        for key, value in usage.items()
    ):
        raise AdapterFailure("Adapter response usage must contain numeric values")

    return AdapterResponse(
        output=output,
        events=tuple(normalized_events),
        usage=dict(usage),
        raw={
            "output": output,
            "events": normalized_events,
            "usage": dict(usage),
        },
    )


def terminate_adapter_process(process: subprocess.Popen[bytes]) -> None:
    """Terminate an adapter and its process group after a timeout."""

    if os.name == "posix":
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except OSError:
            if process.poll() is None:
                process.kill()
    elif process.poll() is None:
        process.kill()
    if process.poll() is None:
        try:
            process.wait(timeout=1)
        except subprocess.TimeoutExpired:
            process.kill()
    process.wait()


def stream_size(stream: Any) -> int:
    """Return the byte size of a seekable temporary stream."""

    stream.seek(0, os.SEEK_END)
    return int(stream.tell())


def read_stream(stream: Any) -> str:
    """Read a temporary byte stream as replacement-safe UTF-8."""

    stream.seek(0)
    return stream.read().decode("utf-8", errors="replace")


def evaluate_checks(
    checks: Iterable[Mapping[str, Any]],
    response: AdapterResponse,
    workspace: Path,
    default_skill: str,
) -> tuple[CheckResult, ...]:
    """Evaluate deterministic checks against response data and workspace state."""

    results: list[CheckResult] = []
    for check in checks:
        identifier = str(check["id"])
        check_type = str(check["type"])
        required = bool(check.get("required", True))
        case_sensitive = bool(check.get("case_sensitive", False))
        output = response.output if case_sensitive else response.output.casefold()

        passed = False
        message = ""
        if check_type in {"contains", "not_contains"}:
            expected = str(check["value"])
            candidate = expected if case_sensitive else expected.casefold()
            found = candidate in output
            passed = found if check_type == "contains" else not found
            message = f"{'found' if found else 'missing'} {expected!r}"
        elif check_type in {"contains_all", "contains_any"}:
            values = [str(value) for value in check["values"]]
            normalized = values if case_sensitive else [value.casefold() for value in values]
            matches = [value in output for value in normalized]
            passed = all(matches) if check_type == "contains_all" else any(matches)
            missing = [value for value, matched in zip(values, matches, strict=True) if not matched]
            message = "all values found" if not missing else f"missing {missing!r}"
        elif check_type in {"regex", "not_regex"}:
            flags = 0 if case_sensitive else re.IGNORECASE
            matched = re.search(str(check["pattern"]), response.output, flags) is not None
            passed = matched if check_type == "regex" else not matched
            message = f"pattern {'matched' if matched else 'did not match'}"
        elif check_type == "file_exists":
            candidate = (workspace / str(check["path"])).resolve()
            passed = candidate.is_relative_to(workspace.resolve()) and candidate.is_file()
            message = f"{check['path']!r} {'exists' if passed else 'is missing'}"
        elif check_type == "loaded_skill":
            skill_name = str(check.get("skill", default_skill))
            passed = any(
                event.get("type") == "skill_loaded" and event.get("name") == skill_name for event in response.events
            )
            message = f"skill {skill_name!r} {'was' if passed else 'was not'} observed"
        else:  # Defensive; schema validation should make this unreachable.
            message = f"unsupported check type {check_type!r}"

        results.append(
            CheckResult(
                identifier=identifier,
                check_type=check_type,
                required=required,
                passed=passed,
                message=message,
            )
        )
    return tuple(results)


def redact_text(value: str) -> str:
    """Redact common credential shapes before persisting artifacts."""

    redacted = value
    for pattern in SECRET_PATTERNS:
        if "PRIVATE KEY" in pattern.pattern:
            redacted = pattern.sub("[REDACTED PRIVATE KEY]", redacted)
        else:
            redacted = pattern.sub(
                lambda match: (
                    f"{match.group(1)}{match.group(2)}[REDACTED]"
                    if match.lastindex and match.lastindex >= 2
                    else f"{match.group(1)} [REDACTED]"
                ),
                redacted,
            )
    return redacted


def redact_value(value: Any) -> Any:
    """Recursively redact strings in artifact payloads."""

    if isinstance(value, str):
        return redact_text(value)
    if isinstance(value, list):
        return [redact_value(item) for item in value]
    if isinstance(value, tuple):
        return [redact_value(item) for item in value]
    if isinstance(value, dict):
        return {
            str(key): ("[REDACTED]" if SENSITIVE_KEY_PATTERN.search(str(key)) else redact_value(item))
            for key, item in value.items()
        }
    return value


def list_workspace_files(workspace: Path) -> tuple[str, ...]:
    """Return sorted file paths relative to an eval workspace."""

    return tuple(
        str(path.relative_to(workspace)) for path in sorted(path for path in workspace.rglob("*") if path.is_file())
    )


def run_mode(
    suite: EvalSuite,
    case: EvalCase,
    mode: str,
    adapter_command: Sequence[str],
    timeout_seconds: float,
    max_output_bytes: int,
    artifact_directory: Path,
) -> ModeResult:
    """Run and score one mode of one eval case."""

    with tempfile.TemporaryDirectory(prefix="skills-eval-") as temp_directory:
        workspace = Path(temp_directory).resolve()
        copied_files, installed_skill = copy_case_workspace(suite, case, workspace, mode)
        request = {
            "protocol_version": PROTOCOL_VERSION,
            "mode": mode,
            "skill": (
                {
                    "name": suite.skill_name,
                    "path": str(installed_skill),
                }
                if installed_skill is not None
                else None
            ),
            "prompt": case.prompt,
            "files": copied_files,
            "workspace": str(workspace),
        }

        started_at = time.monotonic()
        response = run_adapter(
            adapter_command,
            request,
            timeout_seconds=timeout_seconds,
            max_output_bytes=max_output_bytes,
            working_directory=workspace,
        )
        duration_seconds = time.monotonic() - started_at
        checks = evaluate_checks(
            case.checks,
            response,
            workspace,
            default_skill=suite.skill_name,
        )
        workspace_files = list_workspace_files(workspace)
        result = ModeResult(
            mode=mode,
            response=response,
            checks=checks,
            duration_seconds=duration_seconds,
            workspace_files=workspace_files,
        )
        write_mode_artifacts(artifact_directory, result)
        return result


def write_json(path: Path, payload: Any) -> None:
    """Write stable, redacted JSON without exposing private artifact content."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(redact_value(payload), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def write_mode_artifacts(directory: Path, result: ModeResult) -> None:
    """Write response, grading, and timing artifacts for one mode."""

    directory.mkdir(parents=True, exist_ok=True)
    (directory / "output.txt").write_text(redact_text(result.response.output) + "\n", encoding="utf-8")
    write_json(directory / "response.json", result.response.raw)
    write_json(
        directory / "grading.json",
        {
            "passed": result.passed,
            "checks": [dataclasses.asdict(check) for check in result.checks],
        },
    )
    write_json(
        directory / "timing.json",
        {
            "duration_seconds": result.duration_seconds,
            "usage": result.response.usage,
            "workspace_files": result.workspace_files,
        },
    )


def build_benchmark(
    skill_name: str,
    run_id: str,
    case_results: Sequence[dict[str, Any]],
) -> dict[str, Any]:
    """Build aggregate baseline and with-skill metrics."""

    mode_metrics: dict[str, dict[str, Any]] = {}
    for mode in ("with_skill", "without_skill"):
        mode_results = [result[mode] for result in case_results if mode in result]
        passed = sum(1 for result in mode_results if result.passed)
        total = len(mode_results)
        mode_metrics[mode] = {
            "passed": passed,
            "total": total,
            "pass_rate": passed / total if total else 0.0,
            "duration_seconds": sum(result.duration_seconds for result in mode_results),
        }

    return {
        "protocol_version": PROTOCOL_VERSION,
        "run_id": run_id,
        "skill_name": skill_name,
        "with_skill": mode_metrics["with_skill"],
        "without_skill": mode_metrics["without_skill"],
        "pass_rate_lift": (mode_metrics["with_skill"]["pass_rate"] - mode_metrics["without_skill"]["pass_rate"]),
        "cases": [
            {
                "id": result["id"],
                "iteration": result["iteration"],
                "with_skill_passed": result["with_skill"].passed,
                "without_skill_passed": result["without_skill"].passed,
            }
            for result in case_results
        ],
    }


def run_suite(
    suite: EvalSuite,
    adapter_command: Sequence[str],
    output_root: Path,
    run_id: str,
    iterations: int,
    timeout_seconds: float,
    max_output_bytes: int,
    minimum_lift: float | None = None,
) -> tuple[dict[str, Any], bool]:
    """Run all cases in a suite and return benchmark plus success."""

    ungraded_cases = [case.identifier for case in suite.cases if not case.checks]
    if ungraded_cases:
        raise ValidationFailure(
            f"{suite.skill_name} eval case(s) {ungraded_cases} have no deterministic "
            "checks; validation is allowed, but execution requires checks or a "
            "future judge adapter"
        )

    case_results: list[dict[str, Any]] = []
    for iteration in range(1, iterations + 1):
        for case in suite.cases:
            case_root = output_root / run_id / suite.skill_name / f"iteration-{iteration}" / f"eval-{case.identifier}"
            result: dict[str, Any] = {
                "id": case.identifier,
                "iteration": iteration,
            }
            write_json(
                case_root / "case.json",
                {
                    "id": case.identifier,
                    "prompt": case.prompt,
                    "expected_output": case.expected_output,
                    "assertions": case.assertions,
                    "checks": case.checks,
                },
            )
            for mode in ("without_skill", "with_skill"):
                result[mode] = run_mode(
                    suite=suite,
                    case=case,
                    mode=mode,
                    adapter_command=adapter_command,
                    timeout_seconds=timeout_seconds,
                    max_output_bytes=max_output_bytes,
                    artifact_directory=case_root / mode,
                )
            case_results.append(result)

    benchmark = build_benchmark(suite.skill_name, run_id, case_results)
    effectiveness_passed = minimum_lift is None or benchmark["pass_rate_lift"] >= minimum_lift
    benchmark["minimum_lift"] = minimum_lift
    benchmark["effectiveness_passed"] = effectiveness_passed
    write_json(output_root / run_id / suite.skill_name / "benchmark.json", benchmark)
    with_skill_passed = all(result["with_skill"].passed for result in case_results)
    return benchmark, with_skill_passed and effectiveness_passed


def select_suites(suites: Sequence[EvalSuite], requested_skills: Sequence[str]) -> list[EvalSuite]:
    """Select requested suites and reject unknown or unevaluated skill names."""

    by_name = {suite.skill_name: suite for suite in suites}
    if not requested_skills:
        return list(suites)

    missing = sorted(set(requested_skills) - by_name.keys())
    if missing:
        raise ValidationFailure("No eval suite found for skill(s): " + ", ".join(missing))
    return [by_name[name] for name in requested_skills]


def default_run_id() -> str:
    """Return a sortable UTC run identifier."""

    return datetime.datetime.now(datetime.UTC).strftime("%Y%m%dT%H%M%SZ")


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="Handbook repository root",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("validate", help="Validate skills and eval definitions")

    run_parser = subparsers.add_parser("run", help="Run with-skill and baseline evaluations")
    run_parser.add_argument(
        "--adapter",
        type=Path,
        required=True,
        help="Executable implementing the JSON adapter protocol",
    )
    run_parser.add_argument(
        "--adapter-arg",
        action="append",
        default=[],
        help="Argument passed directly to the adapter; may be repeated",
    )
    run_parser.add_argument(
        "--skill",
        action="append",
        default=[],
        help="Skill to evaluate; may be repeated (default: every eval suite)",
    )
    run_parser.add_argument("--iterations", type=int, default=1)
    run_parser.add_argument("--timeout-seconds", type=float, default=120.0)
    run_parser.add_argument("--max-output-bytes", type=int, default=1_048_576)
    run_parser.add_argument(
        "--minimum-lift",
        type=float,
        default=None,
        help="Optional minimum with-skill pass-rate lift required for success",
    )
    run_parser.add_argument("--run-id", default=None)
    run_parser.add_argument(
        "--output-root",
        type=Path,
        default=None,
        help="Artifact root (default: <repo>/tmp/skills-eval)",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the command-line interface."""

    parser = build_parser()
    arguments = parser.parse_args(argv)

    try:
        root = repository_root(arguments.repo_root)
        suites = validate_repository(root)
        if arguments.command == "validate":
            print(f"Validated {len(list((root / 'skills').glob('*/SKILL.md')))} skills and {len(suites)} eval suites.")
            return 0

        if arguments.iterations < 1:
            raise ValidationFailure("--iterations must be at least 1")
        if arguments.timeout_seconds <= 0:
            raise ValidationFailure("--timeout-seconds must be positive")
        if arguments.max_output_bytes < 1:
            raise ValidationFailure("--max-output-bytes must be positive")
        if arguments.minimum_lift is not None and not -1 <= arguments.minimum_lift <= 1:
            raise ValidationFailure("--minimum-lift must be between -1 and 1")

        run_id = arguments.run_id or default_run_id()
        if not SAFE_RUN_ID_PATTERN.fullmatch(run_id):
            raise ValidationFailure("--run-id may contain only letters, numbers, dots, underscores, and hyphens")

        adapter = arguments.adapter.expanduser().resolve()
        if not adapter.is_file():
            raise ValidationFailure(f"Adapter does not exist: {adapter}")
        if not os.access(adapter, os.X_OK):
            raise ValidationFailure(f"Adapter is not executable: {adapter}")
        adapter_command = [str(adapter), *arguments.adapter_arg]

        selected_suites = select_suites(suites, arguments.skill)
        output_root = (
            arguments.output_root.expanduser().resolve() if arguments.output_root else root / "tmp" / "skills-eval"
        )
        output_root.mkdir(parents=True, exist_ok=True)

        all_passed = True
        for suite in selected_suites:
            benchmark, passed = run_suite(
                suite=suite,
                adapter_command=adapter_command,
                output_root=output_root,
                run_id=run_id,
                iterations=arguments.iterations,
                timeout_seconds=arguments.timeout_seconds,
                max_output_bytes=arguments.max_output_bytes,
                minimum_lift=arguments.minimum_lift,
            )
            print(
                f"{suite.skill_name}: with_skill="
                f"{benchmark['with_skill']['pass_rate']:.1%}, baseline="
                f"{benchmark['without_skill']['pass_rate']:.1%}, "
                f"lift={benchmark['pass_rate_lift']:+.1%}"
            )
            if arguments.minimum_lift is None and benchmark["pass_rate_lift"] <= 0:
                print(
                    f"warning: {suite.skill_name} showed no positive measured lift; "
                    "review the artifacts before treating the skill as effective",
                    file=sys.stderr,
                )
            all_passed = all_passed and passed
        print(f"Artifacts: {output_root / run_id}")
        return 0 if all_passed else 1
    except (ValidationFailure, AdapterFailure) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
