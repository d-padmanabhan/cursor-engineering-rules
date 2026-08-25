"""Regression tests for discriminating documentation-standards evals."""

import tempfile
import unittest
from pathlib import Path

from evals.skill_eval import AdapterResponse, EvalCase, evaluate_checks, load_eval_suite

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DOCUMENTATION_SKILL_DIRECTORY = REPOSITORY_ROOT / "skills" / "documentation-standards"


class DocumentationStandardsEvalTests(unittest.TestCase):
    """Ensure unsafe or incomplete Docusaurus guidance cannot pass evals."""

    @classmethod
    def setUpClass(cls) -> None:
        """Load the documentation-standards eval suite once."""
        suite = load_eval_suite(DOCUMENTATION_SKILL_DIRECTORY)
        if suite is None:
            raise AssertionError("documentation-standards eval suite is missing")
        cls.cases = {case.identifier: case for case in suite.cases}

    def failed_check_ids(self, case: EvalCase, output: str) -> set[str]:
        """Return failed required check identifiers for one response."""
        response = AdapterResponse(output=output, events=(), usage={}, raw={})
        with tempfile.TemporaryDirectory() as temp_directory:
            results = evaluate_checks(
                case.checks,
                response,
                Path(temp_directory),
                default_skill="documentation-standards",
            )
        return {
            result.identifier
            for result in results
            if result.required and not result.passed
        }

    def test_untrusted_mdx_rejects_sandbox_only_argument(self) -> None:
        """Reject direct compilation even when the build runs in a sandbox."""
        output = "Compile the customer MDX directly because the CI sandbox contains it."

        failed = self.failed_check_ids(self.cases[5], output)

        self.assertIn("rejects-direct-untrusted-mdx", failed)
        self.assertIn("restricts-active-content", failed)

    def test_search_eval_rejects_built_in_assumption(self) -> None:
        """Reject a search plan with no provider or production index check."""
        output = "Docusaurus includes search, so deploy the site without configuration."

        failed = self.failed_check_ids(self.cases[6], output)

        self.assertIn("rejects-automatic-search-assumption", failed)
        self.assertIn("configures-search-provider", failed)
        self.assertIn("verifies-production-index", failed)
        self.assertIn("protects-search-credentials", failed)

    def test_deployment_eval_rejects_development_server_validation(self) -> None:
        """Reject validation that ignores the production subpath and build."""
        output = "The development server works at /, so keep the existing config."

        failed = self.failed_check_ids(self.cases[7], output)

        self.assertIn("corrects-deployment-path", failed)
        self.assertIn("fails-on-broken-links", failed)
        self.assertIn("tests-generated-site", failed)

    def test_versioning_eval_rejects_unbounded_patch_snapshots(self) -> None:
        """Reject hand-copied snapshots for every patch and every preview."""
        output = "Copy all 40 patch versions and load every version in previews."

        failed = self.failed_check_ids(self.cases[8], output)

        self.assertIn("limits-versioning-scope", failed)
        self.assertIn("uses-versioning-cli", failed)
        self.assertIn("bounds-preview-versions", failed)


if __name__ == "__main__":
    unittest.main()
