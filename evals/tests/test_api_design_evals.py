"""Regression tests for discriminating API design eval assertions."""

import tempfile
import unittest
from pathlib import Path

from evals.skill_eval import AdapterResponse, EvalCase, evaluate_checks, load_eval_suite

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
API_DESIGN_SKILL_DIRECTORY = REPOSITORY_ROOT / "skills" / "api-design"


class ApiDesignEvalTests(unittest.TestCase):
    """Ensure unsafe or incomplete API guidance cannot pass evals."""

    @classmethod
    def setUpClass(cls) -> None:
        """Load the API design eval suite once."""
        suite = load_eval_suite(API_DESIGN_SKILL_DIRECTORY)
        if suite is None:
            raise AssertionError("api-design eval suite is missing")
        cls.cases = {case.identifier: case for case in suite.cases}

    def failed_check_ids(self, case: EvalCase, output: str) -> set[str]:
        """Return failed required check identifiers for one response."""
        response = AdapterResponse(output=output, events=(), usage={}, raw={})
        with tempfile.TemporaryDirectory() as temp_directory:
            results = evaluate_checks(
                case.checks,
                response,
                Path(temp_directory),
                default_skill="api-design",
            )
        return {result.identifier for result in results if result.required and not result.passed}

    def test_expected_outputs_satisfy_required_checks(self) -> None:
        """Confirm each canonical expected response satisfies its own checks."""
        for case in self.cases.values():
            with self.subTest(case=case.identifier):
                self.assertEqual(set(), self.failed_check_ids(case, case.expected_output))

    def test_rejects_state_change_through_get(self) -> None:
        """Require safe HTTP method semantics and a mutation contract."""
        output = "Keep GET because it is convenient for browsers."

        failed = self.failed_check_ids(self.cases[1], output)

        self.assertIn("rejects-unsafe-get", failed)
        self.assertIn("models-cancellation-resource", failed)

    def test_rejects_cache_only_idempotency(self) -> None:
        """Require atomic operation identity and complete result replay."""
        output = "Generate a key and cache the response body after charging."

        failed = self.failed_check_ids(self.cases[2], output)

        self.assertIn("requires-client-stable-key", failed)
        self.assertIn("requires-atomic-operation-state", failed)
        self.assertIn("replays-complete-result", failed)

    def test_rejects_unconditional_overwrite(self) -> None:
        """Require an atomic conditional write for lost-update protection."""
        output = "Last writer wins, so accept both PUT requests."

        failed = self.failed_check_ids(self.cases[3], output)

        self.assertIn("uses-conditional-write", failed)
        self.assertIn("uses-stale-precondition-status", failed)

    def test_rejects_opaque_accepted_response(self) -> None:
        """Require an authorized operation resource and terminal lifecycle."""
        output = "Return 202 accepted and ask clients to try again later."

        failed = self.failed_check_ids(self.cases[4], output)

        self.assertIn("defines-operation-resource", failed)
        self.assertIn("defines-terminal-lifecycle", failed)
        self.assertIn("defines-recovery-lifecycle", failed)

    def test_rejects_success_status_with_internal_error(self) -> None:
        """Require Problem Details without internal implementation leakage."""
        output = "Return 200 and include the database error and stack."

        failed = self.failed_check_ids(self.cases[5], output)

        self.assertIn("uses-problem-details", failed)
        self.assertIn("uses-safe-field-errors", failed)
        self.assertIn("removes-internal-details", failed)

    def test_rejects_unstable_unbounded_cursor(self) -> None:
        """Require deterministic order and a context-bound cursor."""
        output = "Base64-encode the offset and allow any page size."

        failed = self.failed_check_ids(self.cases[6], output)

        self.assertIn("requires-stable-order", failed)
        self.assertIn("requires-bound-cursor", failed)

    def test_rejects_schema_only_compatibility_claim(self) -> None:
        """Require semantic and consumer compatibility evidence."""
        output = "The schema calls it additive, so delete v1 immediately."

        failed = self.failed_check_ids(self.cases[7], output)

        self.assertIn("identifies-semantic-breaks", failed)
        self.assertIn("requires-compatibility-evidence", failed)

    def test_rejects_parsed_webhook_and_arbitrary_destination(self) -> None:
        """Require raw-body verification, replay safety, and SSRF controls."""
        output = "Verify parsed JSON, process inline, and allow every URL."

        failed = self.failed_check_ids(self.cases[8], output)

        self.assertIn("secures-inbound-webhook", failed)
        self.assertIn("prevents-webhook-ssrf", failed)

    def test_rejects_global_graphql_loader_and_depth_only_limit(self) -> None:
        """Require field authorization, loader isolation, and demand control."""
        output = "Keep the global DataLoader and limit query depth."

        failed = self.failed_check_ids(self.cases[9], output)

        self.assertIn("requires-field-authorization", failed)
        self.assertIn("scopes-dataloader", failed)
        self.assertIn("bounds-graphql-demand", failed)

    def test_rejects_protobuf_tag_reuse(self) -> None:
        """Require wire-compatible Protobuf evolution."""
        output = "Generated code compiles, so reuse tag 3."

        failed = self.failed_check_ids(self.cases[10], output)

        self.assertIn("protects-field-tags", failed)
        self.assertIn("requires-reservation-and-checks", failed)


if __name__ == "__main__":
    unittest.main()
