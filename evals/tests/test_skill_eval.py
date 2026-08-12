"""Unit tests for the Agent Skills evaluation harness."""

import json
import os
import sys
import tempfile
import textwrap
import time
import unittest
from pathlib import Path

from evals.skill_eval import (
    AdapterFailure,
    AdapterResponse,
    CheckResult,
    EvalCase,
    EvalSuite,
    ModeResult,
    ValidationFailure,
    build_benchmark,
    copy_case_workspace,
    evaluate_checks,
    load_eval_suite,
    parse_frontmatter,
    redact_text,
    redact_value,
    run_adapter,
    run_suite,
    validate_skill_metadata,
)


class SkillMetadataTests(unittest.TestCase):
    """Validate frontmatter parsing and directory contracts."""

    def test_parse_folded_description(self) -> None:
        with tempfile.TemporaryDirectory() as temp_directory:
            skill_file = Path(temp_directory) / "SKILL.md"
            skill_file.write_text(
                textwrap.dedent(
                    """\
                    ---
                    name: sample-skill
                    description: >-
                      First line for discovery.
                      Second line for triggering.
                    ---
                    # Sample
                    """
                ),
                encoding="utf-8",
            )

            metadata = parse_frontmatter(skill_file)

            self.assertEqual(metadata["name"], "sample-skill")
            self.assertEqual(
                metadata["description"],
                "First line for discovery. Second line for triggering.",
            )

    def test_validate_skill_name_matches_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temp_directory:
            skills_directory = Path(temp_directory) / "skills"
            skill_directory = skills_directory / "directory-name"
            skill_directory.mkdir(parents=True)
            (skill_directory / "SKILL.md").write_text(
                "---\nname: different-name\ndescription: A test skill.\n---\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValidationFailure, "does not match directory"):
                validate_skill_metadata(skills_directory)

    def test_validate_skill_rejects_symlinks(self) -> None:
        with tempfile.TemporaryDirectory() as temp_directory:
            root = Path(temp_directory)
            skills_directory = root / "skills"
            skill_directory = skills_directory / "sample-skill"
            skill_directory.mkdir(parents=True)
            (skill_directory / "SKILL.md").write_text(
                "---\nname: sample-skill\ndescription: A test skill.\n---\n",
                encoding="utf-8",
            )
            outside_file = root / "outside.txt"
            outside_file.write_text("private\n", encoding="utf-8")
            (skill_directory / "linked.txt").symlink_to(outside_file)

            with self.assertRaisesRegex(ValidationFailure, "symlinks are not allowed"):
                validate_skill_metadata(skills_directory)

    def test_validate_skill_rejects_symlinked_skill_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temp_directory:
            root = Path(temp_directory)
            skills_directory = root / "skills"
            external_skill = root / "external-skill"
            external_skill.mkdir(parents=True)
            (external_skill / "SKILL.md").write_text(
                "---\nname: sample-skill\ndescription: A test skill.\n---\n",
                encoding="utf-8",
            )
            skills_directory.mkdir()
            (skills_directory / "sample-skill").symlink_to(external_skill, target_is_directory=True)

            with self.assertRaisesRegex(ValidationFailure, "skill directories cannot be symlinks"):
                validate_skill_metadata(skills_directory)


class EvalSchemaTests(unittest.TestCase):
    """Validate eval schema and fixture boundary handling."""

    def test_load_eval_suite_accepts_portable_skill_root_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temp_directory:
            root = Path(temp_directory)
            skill_directory = root / "skills" / "sample-skill"
            fixture = skill_directory / "evals" / "files" / "input.txt"
            fixture.parent.mkdir(parents=True)
            fixture.write_text("portable\n", encoding="utf-8")
            (fixture.parent.parent / "evals.json").write_text(
                json.dumps(
                    {
                        "skill_name": "sample-skill",
                        "evals": [
                            {
                                "id": 1,
                                "prompt": "Review this.",
                                "expected_output": "A review.",
                                "assertions": ["Names the primary risk."],
                                "files": ["evals/files/input.txt"],
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            suite = load_eval_suite(skill_directory)

            self.assertIsNotNone(suite)
            assert suite is not None
            self.assertEqual(suite.cases[0].files, (fixture.resolve(),))
            self.assertEqual(suite.cases[0].assertions, ("Names the primary risk.",))
            self.assertEqual(suite.cases[0].checks, ())

    def test_load_eval_suite_rejects_fixture_traversal(self) -> None:
        with tempfile.TemporaryDirectory() as temp_directory:
            root = Path(temp_directory)
            skill_directory = root / "skills" / "sample-skill"
            eval_directory = skill_directory / "evals"
            eval_directory.mkdir(parents=True)
            outside_file = skill_directory / "outside.txt"
            outside_file.write_text("outside\n", encoding="utf-8")
            (eval_directory / "evals.json").write_text(
                json.dumps(
                    {
                        "skill_name": "sample-skill",
                        "evals": [
                            {
                                "id": 1,
                                "prompt": "Review this.",
                                "expected_output": "A review.",
                                "files": ["../outside.txt"],
                                "checks": [
                                    {
                                        "id": "review",
                                        "type": "contains",
                                        "value": "review",
                                    }
                                ],
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValidationFailure, "escapes skill directory"):
                load_eval_suite(skill_directory)

    def test_load_eval_suite_rejects_non_boolean_case_sensitivity(self) -> None:
        with tempfile.TemporaryDirectory() as temp_directory:
            skill_directory = Path(temp_directory) / "skills" / "sample-skill"
            eval_directory = skill_directory / "evals"
            eval_directory.mkdir(parents=True)
            (eval_directory / "evals.json").write_text(
                json.dumps(
                    {
                        "skill_name": "sample-skill",
                        "evals": [
                            {
                                "id": 1,
                                "prompt": "Review this.",
                                "expected_output": "A review.",
                                "files": [],
                                "checks": [
                                    {
                                        "id": "review",
                                        "type": "contains",
                                        "value": "review",
                                        "case_sensitive": "false",
                                    }
                                ],
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValidationFailure, "must be a boolean"):
                load_eval_suite(skill_directory)

    def test_copy_case_workspace_keeps_fixtures_equal(self) -> None:
        with tempfile.TemporaryDirectory() as temp_directory:
            root = Path(temp_directory)
            skill_directory = root / "sample-skill"
            eval_directory = skill_directory / "evals"
            fixture = eval_directory / "fixtures" / "input.txt"
            fixture.parent.mkdir(parents=True)
            fixture.write_text("same input\n", encoding="utf-8")
            (skill_directory / "SKILL.md").write_text(
                "---\nname: sample-skill\ndescription: Test.\n---\n",
                encoding="utf-8",
            )
            suite = EvalSuite(
                skill_name="sample-skill",
                skill_directory=skill_directory,
                eval_directory=eval_directory,
                cases=(),
            )
            case = EvalCase(
                identifier=1,
                prompt="Test",
                expected_output="Test",
                assertions=(),
                files=(fixture,),
                checks=(),
            )
            with_workspace = root / "with"
            without_workspace = root / "without"

            with_files, installed = copy_case_workspace(suite, case, with_workspace, "with_skill")
            without_files, baseline_installed = copy_case_workspace(suite, case, without_workspace, "without_skill")

            self.assertEqual(with_files[0]["sha256"], without_files[0]["sha256"])
            self.assertIsNotNone(installed)
            self.assertIsNone(baseline_installed)
            self.assertFalse((without_workspace / "skills").exists())


class DeterministicCheckTests(unittest.TestCase):
    """Verify deterministic output, file, and activation checks."""

    def test_evaluate_text_file_and_activation_checks(self) -> None:
        with tempfile.TemporaryDirectory() as temp_directory:
            workspace = Path(temp_directory)
            (workspace / "result.json").write_text("{}\n", encoding="utf-8")
            response = AdapterResponse(
                output="Use a parameterized SQL query. Avoid a broad rewrite.",
                events=({"type": "skill_loaded", "name": "core-engineering"},),
                usage={"input_tokens": 100},
                raw={},
            )
            checks = [
                {
                    "id": "parameterized",
                    "type": "contains",
                    "value": "parameterized SQL",
                },
                {
                    "id": "no-secret",
                    "type": "not_contains",
                    "value": "hardcoded password",
                },
                {
                    "id": "artifact",
                    "type": "file_exists",
                    "path": "result.json",
                },
                {
                    "id": "activation",
                    "type": "loaded_skill",
                    "skill": "core-engineering",
                },
            ]

            results = evaluate_checks(checks, response, workspace, default_skill="core-engineering")

            self.assertTrue(all(result.passed for result in results))

    def test_optional_failure_does_not_fail_mode(self) -> None:
        result = ModeResult(
            mode="with_skill",
            response=AdapterResponse(output="", events=(), usage={}, raw={}),
            checks=(
                CheckResult(
                    identifier="optional",
                    check_type="contains",
                    required=False,
                    passed=False,
                    message="missing",
                ),
            ),
            duration_seconds=0.1,
            workspace_files=(),
        )

        self.assertTrue(result.passed)


class AdapterTests(unittest.TestCase):
    """Exercise adapter protocol handling and limits."""

    def make_adapter(self, directory: Path, body: str) -> Path:
        adapter = directory / "adapter.py"
        adapter.write_text(body, encoding="utf-8")
        adapter.chmod(adapter.stat().st_mode | 0o100)
        return adapter

    def test_run_adapter_accepts_valid_response(self) -> None:
        with tempfile.TemporaryDirectory() as temp_directory:
            adapter = self.make_adapter(
                Path(temp_directory),
                textwrap.dedent(
                    """\
                    #!/usr/bin/env python3
                    import json
                    import sys

                    request = json.load(sys.stdin)
                    json.dump(
                        {
                            "output": request["prompt"],
                            "events": [],
                            "usage": {"input_tokens": 1},
                        },
                        sys.stdout,
                    )
                    """
                ),
            )

            response = run_adapter(
                [str(adapter)],
                {"prompt": "hello"},
                timeout_seconds=2,
                max_output_bytes=1024,
            )

            self.assertEqual(response.output, "hello")
            self.assertEqual(response.usage["input_tokens"], 1)

    def test_run_adapter_enforces_timeout(self) -> None:
        with tempfile.TemporaryDirectory() as temp_directory:
            adapter = self.make_adapter(
                Path(temp_directory),
                textwrap.dedent(
                    """\
                    #!/usr/bin/env python3
                    import time

                    time.sleep(2)
                    """
                ),
            )

            with self.assertRaisesRegex(AdapterFailure, "timed out"):
                run_adapter(
                    [str(adapter)],
                    {"payload": "x" * 2_000_000},
                    timeout_seconds=0.05,
                    max_output_bytes=1024,
                )

    def test_run_adapter_rejects_oversized_output(self) -> None:
        with tempfile.TemporaryDirectory() as temp_directory:
            adapter = self.make_adapter(
                Path(temp_directory),
                textwrap.dedent(
                    """\
                    #!/usr/bin/env python3
                    print("x" * 2048)
                    """
                ),
            )

            with self.assertRaisesRegex(AdapterFailure, "output exceeded"):
                run_adapter(
                    [str(adapter)],
                    {},
                    timeout_seconds=1,
                    max_output_bytes=128,
                )

    def test_run_adapter_rejects_unknown_response_fields(self) -> None:
        with tempfile.TemporaryDirectory() as temp_directory:
            adapter = self.make_adapter(
                Path(temp_directory),
                textwrap.dedent(
                    """\
                    #!/usr/bin/env python3
                    import json

                    print(json.dumps({"output": "ok", "hidden_trace": "private"}))
                    """
                ),
            )

            with self.assertRaisesRegex(AdapterFailure, "unsupported fields"):
                run_adapter(
                    [str(adapter)],
                    {},
                    timeout_seconds=1,
                    max_output_bytes=1024,
                )

    def test_run_adapter_rejects_unknown_event_fields(self) -> None:
        with tempfile.TemporaryDirectory() as temp_directory:
            adapter = self.make_adapter(
                Path(temp_directory),
                textwrap.dedent(
                    """\
                    #!/usr/bin/env python3
                    import json

                    print(
                        json.dumps(
                            {
                                "output": "ok",
                                "events": [
                                    {
                                        "type": "skill_loaded",
                                        "name": "sample-skill",
                                        "hidden_trace": "private",
                                    }
                                ],
                            }
                        )
                    )
                    """
                ),
            )

            with self.assertRaisesRegex(AdapterFailure, "event.*unsupported fields"):
                run_adapter(
                    [str(adapter)],
                    {},
                    timeout_seconds=1,
                    max_output_bytes=1024,
                )

    @unittest.skipUnless(os.name == "posix", "process-group test requires POSIX")
    def test_run_adapter_timeout_kills_descendants(self) -> None:
        with tempfile.TemporaryDirectory() as temp_directory:
            directory = Path(temp_directory)
            marker = directory / "descendant-survived"
            child_code = (
                "import pathlib,signal,time;"
                "signal.signal(signal.SIGTERM, signal.SIG_IGN);"
                "time.sleep(0.5);"
                f"pathlib.Path({str(marker)!r}).write_text('survived')"
            )
            adapter = self.make_adapter(
                directory,
                textwrap.dedent(
                    f"""\
                    #!/usr/bin/env python3
                    import subprocess
                    import sys
                    import time

                    subprocess.Popen([sys.executable, "-c", {child_code!r}])
                    time.sleep(5)
                    """
                ),
            )

            with self.assertRaisesRegex(AdapterFailure, "timed out"):
                run_adapter(
                    [str(adapter)],
                    {},
                    timeout_seconds=0.05,
                    max_output_bytes=1024,
                )
            time.sleep(0.7)
            self.assertFalse(marker.exists())

    def test_run_adapter_does_not_invoke_shell(self) -> None:
        with tempfile.TemporaryDirectory() as temp_directory:
            marker = Path(temp_directory) / "should-not-exist"
            with self.assertRaises(AdapterFailure):
                run_adapter(
                    [f"{sys.executable};touch", str(marker)],
                    {},
                    timeout_seconds=1,
                    max_output_bytes=1024,
                )
            self.assertFalse(marker.exists())


class BenchmarkTests(unittest.TestCase):
    """Verify with-skill and baseline aggregation."""

    @staticmethod
    def mode_result(mode: str, passed: bool, duration: float) -> ModeResult:
        return ModeResult(
            mode=mode,
            response=AdapterResponse(output="", events=(), usage={}, raw={}),
            checks=(
                CheckResult(
                    identifier="required",
                    check_type="contains",
                    required=True,
                    passed=passed,
                    message="",
                ),
            ),
            duration_seconds=duration,
            workspace_files=(),
        )

    def test_build_benchmark_calculates_lift(self) -> None:
        case_results = [
            {
                "id": 1,
                "iteration": 1,
                "with_skill": self.mode_result("with_skill", True, 1.0),
                "without_skill": self.mode_result("without_skill", False, 0.5),
            },
            {
                "id": 2,
                "iteration": 1,
                "with_skill": self.mode_result("with_skill", True, 1.5),
                "without_skill": self.mode_result("without_skill", True, 1.0),
            },
        ]

        benchmark = build_benchmark("sample-skill", "run-1", case_results)

        self.assertEqual(benchmark["with_skill"]["pass_rate"], 1.0)
        self.assertEqual(benchmark["without_skill"]["pass_rate"], 0.5)
        self.assertEqual(benchmark["pass_rate_lift"], 0.5)
        self.assertEqual(benchmark["paired_win_rate"], 0.5)
        self.assertEqual(benchmark["with_skill"]["median_duration_seconds"], 1.25)
        self.assertEqual(benchmark["with_skill"]["p95_duration_seconds"], 1.5)
        self.assertFalse(benchmark["activation_telemetry_supported"])
        self.assertIsNone(benchmark["activation_rate"])


class SuiteExecutionTests(unittest.TestCase):
    """Exercise isolated modes and artifact generation end to end."""

    def test_run_suite_rejects_ungraded_assertion_only_case(self) -> None:
        with tempfile.TemporaryDirectory() as temp_directory:
            root = Path(temp_directory)
            suite = EvalSuite(
                skill_name="sample-skill",
                skill_directory=root,
                eval_directory=root / "evals",
                cases=(
                    EvalCase(
                        identifier=1,
                        prompt="Test",
                        expected_output="Expected",
                        assertions=("Does the expected thing.",),
                        files=(),
                        checks=(),
                    ),
                ),
            )

            with self.assertRaisesRegex(ValidationFailure, "have no deterministic checks"):
                run_suite(
                    suite=suite,
                    adapter_command=[],
                    output_root=root / "artifacts",
                    run_id="ungraded",
                    iterations=1,
                    timeout_seconds=1,
                    max_output_bytes=1024,
                )

    def test_run_suite_writes_benchmark_and_mode_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_directory:
            root = Path(temp_directory)
            skill_directory = root / "sample-skill"
            eval_directory = skill_directory / "evals"
            eval_directory.mkdir(parents=True)
            (skill_directory / "SKILL.md").write_text(
                "---\nname: sample-skill\ndescription: Test.\n---\n",
                encoding="utf-8",
            )
            adapter = root / "adapter.py"
            adapter.write_text(
                textwrap.dedent(
                    """\
                    #!/usr/bin/env python3
                    import json
                    import os
                    import sys

                    request = json.load(sys.stdin)
                    if "expected_output" in request:
                        raise SystemExit(3)
                    if os.getcwd() != request["workspace"]:
                        raise SystemExit(4)
                    json.dump(
                        {
                            "output": request["mode"],
                            "events": [],
                            "usage": {},
                        },
                        sys.stdout,
                    )
                    """
                ),
                encoding="utf-8",
            )
            adapter.chmod(adapter.stat().st_mode | 0o100)
            suite = EvalSuite(
                skill_name="sample-skill",
                skill_directory=skill_directory,
                eval_directory=eval_directory,
                cases=(
                    EvalCase(
                        identifier=1,
                        prompt="Test",
                        expected_output="with_skill",
                        assertions=(),
                        files=(),
                        checks=(
                            {
                                "id": "mode",
                                "type": "contains",
                                "value": "with_skill",
                            },
                        ),
                    ),
                ),
            )
            output_root = root / "artifacts"

            benchmark, passed = run_suite(
                suite=suite,
                adapter_command=[str(adapter)],
                output_root=output_root,
                run_id="test-run",
                iterations=1,
                timeout_seconds=2,
                max_output_bytes=1024,
            )

            self.assertTrue(passed)
            self.assertEqual(benchmark["pass_rate_lift"], 1.0)
            self.assertTrue(
                (
                    output_root / "test-run" / "sample-skill" / "iteration-1" / "eval-1" / "with_skill" / "grading.json"
                ).is_file()
            )
            self.assertTrue((output_root / "test-run" / "sample-skill" / "benchmark.json").is_file())

            zero_lift_suite = EvalSuite(
                skill_name="sample-skill",
                skill_directory=skill_directory,
                eval_directory=eval_directory,
                cases=(
                    EvalCase(
                        identifier=1,
                        prompt="Test",
                        expected_output="Both modes pass.",
                        assertions=(),
                        files=(),
                        checks=(
                            {
                                "id": "both-modes",
                                "type": "contains",
                                "value": "skill",
                            },
                        ),
                    ),
                ),
            )
            zero_lift_benchmark, zero_lift_passed = run_suite(
                suite=zero_lift_suite,
                adapter_command=[str(adapter)],
                output_root=output_root,
                run_id="zero-lift",
                iterations=1,
                timeout_seconds=2,
                max_output_bytes=1024,
                minimum_lift=0.1,
            )

            self.assertFalse(zero_lift_passed)
            self.assertFalse(zero_lift_benchmark["effectiveness_passed"])


class RedactionTests(unittest.TestCase):
    """Verify common credential shapes are not persisted."""

    def test_redact_text_hides_tokens_and_private_keys(self) -> None:
        private_key_start = "-----BEGIN " + "PRIVATE KEY-----"
        private_key_end = "-----END " + "PRIVATE KEY-----"
        secret_text = (
            f"Authorization: Bearer abc.def.ghi\napi_key=super-secret\n{private_key_start}\nsecret\n{private_key_end}"
        )

        redacted = redact_text(secret_text)

        self.assertNotIn("abc.def.ghi", redacted)
        self.assertNotIn("super-secret", redacted)
        self.assertNotIn("\nsecret\n", redacted)
        self.assertIn("[REDACTED", redacted)

    def test_redact_value_uses_sensitive_dictionary_keys(self) -> None:
        redacted = redact_value(
            {
                "events": [
                    {
                        "authorization": "opaque-value",
                        "nested": {"client_secret": "another-value"},
                    }
                ]
            }
        )

        self.assertEqual(redacted["events"][0]["authorization"], "[REDACTED]")
        self.assertEqual(redacted["events"][0]["nested"]["client_secret"], "[REDACTED]")


if __name__ == "__main__":
    unittest.main()
