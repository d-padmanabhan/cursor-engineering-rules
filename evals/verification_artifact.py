"""Validate independent-verification artifacts and controller semantics.

Usage:
    uv run python -m evals.verification_artifact <artifact.json>
    uv run python -m evals.verification_artifact --for-release <artifact.json>
"""

import argparse
import json
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import SchemaError

MAX_ARTIFACT_BYTES = 1_048_576
DEFAULT_SCHEMA = (
    Path(__file__).resolve().parent.parent
    / "skills"
    / "independent-verification"
    / "references"
    / "verification-artifact.schema.json"
)


class ArtifactValidationError(ValueError):
    """Raised when an artifact violates schema or semantic constraints."""


def load_json_object(path: Path, label: str) -> dict[str, Any]:
    """Load one bounded, non-symlink JSON object.

    Args:
        path: JSON file path.
        label: Human-readable input label.

    Returns:
        Parsed JSON object.

    Raises:
        ArtifactValidationError: If the path or JSON object is invalid.
    """
    if path.is_symlink():
        raise ArtifactValidationError(f"{label} must not be a symlink")
    if not path.is_file():
        raise ArtifactValidationError(f"{label} does not exist: {path}")
    if path.stat().st_size > MAX_ARTIFACT_BYTES:
        raise ArtifactValidationError(f"{label} exceeds {MAX_ARTIFACT_BYTES} bytes")
    try:
        payload: Any = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ArtifactValidationError(f"{label} is invalid JSON: {error}") from error
    if not isinstance(payload, dict):
        raise ArtifactValidationError(f"{label} root must be an object")
    return payload


def schema_errors(artifact: Mapping[str, Any], schema: Mapping[str, Any]) -> list[str]:
    """Return stable validation errors from the JSON Schema.

    Args:
        artifact: Parsed verification artifact.
        schema: Parsed Draft 2020-12 schema.

    Returns:
        Sorted human-readable validation errors.

    Raises:
        ArtifactValidationError: If the committed schema is invalid.
    """
    try:
        Draft202012Validator.check_schema(schema)
    except SchemaError as error:
        raise ArtifactValidationError(f"verification schema is invalid: {error.message}") from error

    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors: list[str] = []
    for error in validator.iter_errors(artifact):
        location = ".".join(str(part) for part in error.absolute_path) or "<root>"
        errors.append(f"{location}: {error.message}")
    return sorted(errors)


def semantic_errors(artifact: Mapping[str, Any], for_release: bool) -> list[str]:
    """Validate independence relationships that JSON Schema cannot compare.

    Args:
        artifact: Schema-valid verification artifact.
        for_release: Whether to enforce release-time human approval.

    Returns:
        Human-readable semantic errors.
    """
    implementer = artifact["implementer"]
    verifier = artifact["verifier"]
    independence = artifact["independence"]
    level = independence["level"]
    errors: list[str] = []

    for check in artifact["evidence"]["checks"]:
        status = check["status"]
        exit_code = check["exit_code"]
        artifact_hash = check["artifact_sha256"]
        if status == "passed" and exit_code != 0:
            errors.append(f"passed check {check['name']!r} must have exit_code 0")
        if status == "passed" and artifact_hash is None:
            errors.append(f"passed check {check['name']!r} must have an artifact hash")
        if check["mandatory"] and status == "skipped":
            errors.append(f"mandatory check {check['name']!r} cannot be skipped")

    if verifier["kind"] == "ai":
        if verifier["session_id"] == implementer["session_id"]:
            errors.append("verifier session must differ from implementer session")
    if level == "same-model-fresh-session":
        if verifier["kind"] != "ai":
            errors.append("same-model level requires an AI verifier")
        else:
            if verifier["provider"] != implementer["provider"]:
                errors.append("same-model level requires the same provider")
            if verifier["model"] != implementer["model"]:
                errors.append("same-model level requires the same model")
        if independence["different_model_family"]:
            errors.append("same-model level cannot claim a different model family")
        if independence["different_provider"]:
            errors.append("same-model level cannot claim a different provider")
    elif level == "different-model-same-provider":
        if verifier["kind"] != "ai":
            errors.append("different-model level requires an AI verifier")
        else:
            if verifier["provider"] != implementer["provider"]:
                errors.append("different-model level requires the same provider")
            if verifier["model"] == implementer["model"]:
                errors.append("different-model level requires a different model")
        if not independence["different_model_family"]:
            errors.append("different-model level must record model-family diversity")
        if independence["different_provider"]:
            errors.append("different-model level cannot claim a different provider")
    elif level == "different-provider":
        if verifier["kind"] != "ai":
            errors.append("different-provider level requires an AI verifier")
        else:
            if verifier["provider"] == implementer["provider"]:
                errors.append("different-provider level requires provider diversity")
            if verifier["model"] == implementer["model"]:
                errors.append("different-provider level requires model diversity")
        if not independence["different_model_family"]:
            errors.append("different-provider level must record model-family diversity")
        if not independence["different_provider"]:
            errors.append("different-provider level must record provider diversity")
    elif level == "human-domain-owner" and verifier["kind"] != "human":
        errors.append("human-domain-owner level requires a human verifier")

    if not independence["different_session"]:
        errors.append("independent verification requires a fresh session")

    if for_release:
        if artifact["verdict"] not in {"PASS", "PASS_WITH_NOTES"}:
            errors.append("release requires PASS or PASS_WITH_NOTES")
        if artifact["stale"]:
            errors.append("release requires a fresh verification target")
        if not artifact["evidence"]["deterministic_gate_passed"]:
            errors.append("release requires passing deterministic gates")
        if not all(
            artifact["revalidation"][field]
            for field in (
                "target_matches",
                "diff_matches",
                "requirements_match",
                "policy_matches",
                "evidence_matches",
            )
        ):
            errors.append("release requires successful controller revalidation")
        human_gate = artifact["human_gate"]
        if human_gate["required"] and human_gate["status"] != "approved":
            errors.append("release remains blocked until the human gate is approved")

    return errors


def validate_artifact(
    artifact: Mapping[str, Any],
    schema: Mapping[str, Any],
    *,
    for_release: bool = False,
) -> list[str]:
    """Validate schema first, then semantic independence constraints.

    Args:
        artifact: Parsed verification artifact.
        schema: Parsed verification artifact schema.
        for_release: Whether to require completed human approval.

    Returns:
        Human-readable validation errors.
    """
    errors = schema_errors(artifact, schema)
    if errors:
        return errors
    return semantic_errors(artifact, for_release)


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifact", type=Path)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    parser.add_argument(
        "--for-release",
        action="store_true",
        help="Require an approved human gate when the artifact marks one required",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Validate one artifact and return a CI-friendly exit code."""
    arguments = build_parser().parse_args(argv)
    try:
        artifact = load_json_object(arguments.artifact.resolve(), "artifact")
        schema = load_json_object(arguments.schema.resolve(), "schema")
        errors = validate_artifact(
            artifact,
            schema,
            for_release=arguments.for_release,
        )
    except ArtifactValidationError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    if errors:
        for error in errors:
            print(f"error: {error}", file=sys.stderr)
        return 1
    print("Independent verification artifact is valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
