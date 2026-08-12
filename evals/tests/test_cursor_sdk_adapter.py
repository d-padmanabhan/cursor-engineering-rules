"""Tests for the Cursor SDK evaluation adapter."""

from __future__ import annotations

import os
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock

from evals.adapters import cursor_sdk_adapter


class CursorSdkAdapterTests(unittest.TestCase):
    """Verify isolation, staging, telemetry, and read-only SDK options."""

    def test_stage_skill_uses_cursor_project_discovery_path(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            source = workspace / "skills" / "sample-skill"
            source.mkdir(parents=True)
            (source / "SKILL.md").write_text("---\nname: sample-skill\n---\n", encoding="utf-8")

            cursor_sdk_adapter.stage_skill(
                {
                    "mode": "with_skill",
                    "skill": {"name": "sample-skill", "path": str(source)},
                },
                workspace,
            )

            staged = workspace / ".cursor" / "skills" / "sample-skill" / "SKILL.md"
            self.assertTrue(staged.is_file())

    def test_without_skill_does_not_create_cursor_directory(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)

            cursor_sdk_adapter.stage_skill(
                {"mode": "without_skill", "skill": None},
                workspace,
            )

            self.assertFalse((workspace / ".cursor").exists())

    def test_stage_skill_rejects_source_outside_workspace(self) -> None:
        with (
            tempfile.TemporaryDirectory() as workspace_directory,
            tempfile.TemporaryDirectory() as source_directory,
        ):
            source = Path(source_directory)
            (source / "SKILL.md").write_text("---\nname: external\n---\n", encoding="utf-8")

            with self.assertRaises(cursor_sdk_adapter.AdapterInputError):
                cursor_sdk_adapter.stage_skill(
                    {
                        "mode": "with_skill",
                        "skill": {"name": "external", "path": str(source)},
                    },
                    Path(workspace_directory),
                )

    def test_run_cursor_uses_project_only_read_only_options(self) -> None:
        captured: dict[str, object] = {}

        class FakeUsage:
            input_tokens = 10
            output_tokens = 5
            cache_read_tokens = 2
            cache_write_tokens = 1
            reasoning_tokens = 1
            total_tokens = 18

        class FakeResult:
            status = "finished"
            result = "completed"
            duration_ms = 250
            usage = FakeUsage()

        class FakeCost:
            charged_cents = 3.5

        class FakeBilledUsage:
            cost = FakeCost()

        class FakeRun:
            @staticmethod
            def wait() -> FakeResult:
                return FakeResult()

        class FakeAgent:
            def __enter__(self) -> FakeAgent:
                return self

            def __exit__(self, *_args: object) -> None:
                return None

            @staticmethod
            def send(prompt: str) -> FakeRun:
                captured["prompt"] = prompt
                return FakeRun()

            @staticmethod
            def get_usage() -> FakeBilledUsage:
                return FakeBilledUsage()

        class FakeAgentType:
            @staticmethod
            def create(options: object) -> FakeAgent:
                captured["options"] = options
                return FakeAgent()

        class FakeAgentOptions:
            def __init__(self, **kwargs: object) -> None:
                self.values = kwargs

        class FakeLocalAgentOptions:
            def __init__(self, **kwargs: object) -> None:
                self.values = kwargs

        fake_sdk = types.SimpleNamespace(
            Agent=FakeAgentType,
            AgentOptions=FakeAgentOptions,
            LocalAgentOptions=FakeLocalAgentOptions,
        )

        with (
            tempfile.TemporaryDirectory() as directory,
            mock.patch.dict(sys.modules, {"cursor_sdk": fake_sdk}),
            mock.patch.dict(
                os.environ,
                {"CURSOR_API_KEY": "redacted-test-key", "CURSOR_EVAL_MODEL": "test-model"},
                clear=False,
            ),
        ):
            response = cursor_sdk_adapter.run_cursor(
                {"prompt": "Review the fixture"},
                Path(directory),
            )

        options = captured["options"]
        self.assertEqual(options.values["tools"], cursor_sdk_adapter.READ_ONLY_TOOLS)
        self.assertEqual(options.values["model"], "test-model")
        self.assertEqual(options.values["local"].values["setting_sources"], ["project"])
        self.assertEqual(response["output"], "completed")
        self.assertEqual(
            response["events"],
            [{"type": "activation_telemetry_unavailable", "name": "cursor-sdk"}],
        )
        self.assertEqual(response["usage"]["total_tokens"], 18)
        self.assertEqual(response["usage"]["cost_usd"], 0.035)


if __name__ == "__main__":
    unittest.main()
