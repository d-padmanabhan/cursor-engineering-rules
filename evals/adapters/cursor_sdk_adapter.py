#!/usr/bin/env python3
"""Run one isolated handbook evaluation through the Cursor Python SDK."""

from __future__ import annotations

import json
import os
import re
import shutil
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any

SAFE_SKILL_NAME = re.compile(r"^[a-z0-9][a-z0-9-]*$")
ALLOWED_MODES = frozenset({"with_skill", "without_skill"})
READ_ONLY_TOOLS = ("read", "grep", "glob", "ls")


class AdapterInputError(ValueError):
    """Raised when the harness request violates the adapter contract."""


def read_request() -> dict[str, Any]:
    """Read and validate the request envelope from standard input."""

    try:
        request = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError) as error:
        raise AdapterInputError("standard input must contain one JSON object") from error

    if not isinstance(request, dict):
        raise AdapterInputError("request must be a JSON object")
    if request.get("protocol_version") != 1:
        raise AdapterInputError("unsupported protocol_version")
    if request.get("mode") not in ALLOWED_MODES:
        raise AdapterInputError("mode must be with_skill or without_skill")
    if not isinstance(request.get("prompt"), str) or not request["prompt"].strip():
        raise AdapterInputError("prompt must be a non-empty string")
    return request


def resolve_workspace(request: Mapping[str, Any]) -> Path:
    """Resolve an existing isolated workspace."""

    raw_workspace = request.get("workspace")
    if not isinstance(raw_workspace, str):
        raise AdapterInputError("workspace must be a string")
    workspace = Path(raw_workspace).resolve()
    if not workspace.is_dir():
        raise AdapterInputError("workspace must be an existing directory")
    return workspace


def stage_skill(request: Mapping[str, Any], workspace: Path) -> None:
    """Install the supplied skill in Cursor's project discovery path."""

    workspace = workspace.resolve()
    if request["mode"] == "without_skill":
        if request.get("skill") is not None:
            raise AdapterInputError("without_skill mode must not include a skill")
        return

    skill = request.get("skill")
    if not isinstance(skill, dict):
        raise AdapterInputError("with_skill mode requires a skill object")
    name = skill.get("name")
    raw_source = skill.get("path")
    if not isinstance(name, str) or SAFE_SKILL_NAME.fullmatch(name) is None:
        raise AdapterInputError("skill name is invalid")
    if not isinstance(raw_source, str):
        raise AdapterInputError("skill path must be a string")

    source = Path(raw_source).resolve()
    if not source.is_dir() or not source.is_relative_to(workspace):
        raise AdapterInputError("skill path must be a directory inside the workspace")
    if not (source / "SKILL.md").is_file():
        raise AdapterInputError("skill path has no SKILL.md")

    destination = workspace / ".cursor" / "skills" / name
    if destination.exists():
        raise AdapterInputError("skill destination already exists")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, destination)


def token_usage_values(usage: object | None) -> dict[str, int | float]:
    """Convert SDK token usage into the vendor-neutral adapter schema."""

    if usage is None:
        return {}

    result: dict[str, int | float] = {}
    for field_name in (
        "input_tokens",
        "output_tokens",
        "cache_read_tokens",
        "cache_write_tokens",
        "reasoning_tokens",
        "total_tokens",
    ):
        value = getattr(usage, field_name, None)
        if isinstance(value, int | float):
            result[field_name] = value
    return result


def run_cursor(request: Mapping[str, Any], workspace: Path) -> dict[str, Any]:
    """Execute one fresh, read-only Cursor agent run."""

    from cursor_sdk import Agent, AgentOptions, LocalAgentOptions  # pylint: disable=import-outside-toplevel

    api_key = os.environ.get("CURSOR_API_KEY")
    model = os.environ.get("CURSOR_EVAL_MODEL")
    if not api_key:
        raise AdapterInputError("CURSOR_API_KEY is required")
    if not model:
        raise AdapterInputError("CURSOR_EVAL_MODEL is required")

    options = AgentOptions(
        api_key=api_key,
        model=model,
        tools=READ_ONLY_TOOLS,
        local=LocalAgentOptions(cwd=workspace, setting_sources=["project"]),
    )
    with Agent.create(options) as agent:
        result = agent.send(request["prompt"]).wait()
        if result.status != "finished":
            raise RuntimeError(f"Cursor run ended with status {result.status!r}")

        usage = token_usage_values(result.usage)
        usage["duration_ms"] = result.duration_ms
        try:
            billed_usage = agent.get_usage()
        except Exception:  # pylint: disable=broad-exception-caught
            # Billing settlement is optional and may lag the completed run.
            billed_usage = None
        if billed_usage is not None and billed_usage.cost is not None:
            usage["cost_usd"] = billed_usage.cost.charged_cents / 100

    return {
        "output": result.result,
        "events": [
            {
                "type": "activation_telemetry_unavailable",
                "name": "cursor-sdk",
            }
        ],
        "usage": usage,
    }


def main() -> int:
    """Run the adapter and emit exactly one response object."""

    try:
        request = read_request()
        workspace = resolve_workspace(request)
        stage_skill(request, workspace)
        response = run_cursor(request, workspace)
    except AdapterInputError as error:
        print(f"cursor SDK adapter input error: {error}", file=sys.stderr)
        return 2
    except Exception as error:  # pylint: disable=broad-exception-caught
        print(f"cursor SDK adapter failed: {type(error).__name__}", file=sys.stderr)
        return 1

    json.dump(response, sys.stdout, separators=(",", ":"))
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
