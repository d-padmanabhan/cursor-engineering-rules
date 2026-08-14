"""Regression tests for discriminating core-engineering eval assertions."""

import tempfile
import unittest
from pathlib import Path

from evals.skill_eval import AdapterResponse, EvalCase, evaluate_checks, load_eval_suite

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
CORE_SKILL_DIRECTORY = REPOSITORY_ROOT / "skills" / "core-engineering"


class CoreEngineeringEvalTests(unittest.TestCase):
    """Ensure known noncompliant responses cannot pass core evals."""

    @classmethod
    def setUpClass(cls) -> None:
        """Load the core-engineering eval suite once."""
        suite = load_eval_suite(CORE_SKILL_DIRECTORY)
        if suite is None:
            raise AssertionError("core-engineering eval suite is missing")
        cls.cases = {case.identifier: case for case in suite.cases}

    def failed_check_ids(self, case: EvalCase, output: str) -> set[str]:
        """Return failed required check identifiers for one response."""
        response = AdapterResponse(output=output, events=(), usage={}, raw={})
        with tempfile.TemporaryDirectory() as temp_directory:
            results = evaluate_checks(
                case.checks,
                response,
                Path(temp_directory),
                default_skill="core-engineering",
            )
        return {result.identifier for result in results if result.required and not result.passed}

    def test_python_cli_rejects_generic_shebang(self) -> None:
        """Reject otherwise plausible code that does not use uv."""
        output = """```python
#!/usr/bin/env python3
import argparse
import json
import sys

def main(argv: list[str] | None = None) -> int:
    \"\"\"Run the command.\"\"\"
    return 0

if __name__ == \"__main__\":
    raise SystemExit(main())
```"""

        failed = self.failed_check_ids(self.cases[2], output)

        self.assertIn("uses-uv-shebang", failed)
        self.assertIn("rejects-generic-python-shebang", failed)

    def test_python_cli_accepts_sys_exit_propagation(self) -> None:
        """Accept either standard mechanism for propagating main's exit code."""
        output = """
def main(argv: list[str] | None = None) -> int:
    return 0

if __name__ == "__main__":
    sys.exit(main())
"""

        failed = self.failed_check_ids(self.cases[2], output)

        self.assertNotIn("uses-typed-main", failed)
        self.assertNotIn("propagates-main-exit-code", failed)

    def test_github_actions_rejects_old_python_and_pip(self) -> None:
        """Reject workflow guidance that violates runtime and package policy."""
        output = """
uses: actions/checkout@v7.0.1
uses: actions/setup-python@v7.0.0
python-version: '3.12'
cache: pip
run: pip install -r requirements.txt
uses: astral-sh/setup-uv@v3
run: uv sync
https://github.com/actions/checkout
https://github.com/actions/setup-python
"""

        failed = self.failed_check_ids(self.cases[3], output)

        self.assertIn("uses-python-3-14", failed)
        self.assertIn("rejects-lower-python-versions", failed)
        self.assertIn("rejects-pip-and-requirements", failed)
        self.assertIn("configures-uv-in-ci", failed)
        self.assertIn("names-current-releases", failed)
        self.assertIn("uses-setup-uv-official-source", failed)

    def test_github_actions_accepts_metadata_provenance_wording(self) -> None:
        """Accept explicit metadata provenance without one prescribed verb."""
        output = "Model memory may be stale; versions come from the attached official release metadata."

        failed = self.failed_check_ids(self.cases[3], output)

        self.assertNotIn("requires-verification", failed)

    def test_kiss_review_rejects_speculative_class_hierarchy(self) -> None:
        """Reject a response that implements the proposed over-engineering."""
        output = """
Use KISS for the 30-line script, but implement the extensible design:

class PluginFactory:
    pass

Revisit this when multiple formats exist.
"""

        failed = self.failed_check_ids(self.cases[4], output)

        self.assertIn("does-not-draft-class-hierarchy", failed)


if __name__ == "__main__":
    unittest.main()
