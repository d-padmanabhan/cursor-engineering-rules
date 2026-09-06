"""Regression tests for data-engineering eval checks."""

import unittest
from typing import ClassVar

from evals.skill_eval import EvalCase
from evals.tests.eval_test_support import (
    assert_expected_outputs_pass,
    failed_required_check_ids,
    load_cases,
)

SKILL_NAME = "data-engineering"


class DataEngineeringEvalTests(unittest.TestCase):
    """Ensure canonical guidance passes and unsafe guidance fails."""

    cases: ClassVar[dict[int, EvalCase]]

    @classmethod
    def setUpClass(cls) -> None:
        """Load the eval suite once for this test class."""
        cls.cases = load_cases(SKILL_NAME)

    def test_expected_outputs_satisfy_required_checks(self) -> None:
        """Prove every canonical output satisfies all required checks."""
        assert_expected_outputs_pass(self, self.cases, SKILL_NAME)

    def test_unsafe_outputs_fail_key_checks_for_every_case(self) -> None:
        """Reject unsafe pipeline advice for every eval scenario."""
        scenarios = {
            1: (
                "Append the corrected rows directly, advance the watermark, and skip validation.",
                {
                    "defines-rerunnable-scope",
                    "makes-backfill-idempotent",
                    "requires-reconciliation",
                },
            ),
            2: (
                "Change the existing amount field to cents in place and notify consumers later.",
                {
                    "identifies-semantic-break",
                    "versions-complete-contract",
                    "coordinates-consumer-migration",
                },
            ),
            3: (
                "Retry forever, commit the source offset first, and replay the raw records.",
                {
                    "bounds-transient-retries",
                    "captures-quarantine-evidence",
                    "defines-progress-and-replay",
                },
            ),
        }

        for case_id, (output, expected_failures) in scenarios.items():
            with self.subTest(case=case_id):
                failed = failed_required_check_ids(
                    self.cases[case_id],
                    output,
                    SKILL_NAME,
                )
                self.assertTrue(expected_failures.issubset(failed))

    def test_rejects_keyword_complete_in_place_unit_approval(self) -> None:
        """Reject unsafe polarity even when every positive token is present."""
        case = self.cases[2]
        output = case.expected_output + " Ship this in-place units change today; it is compatible."

        self.assertEqual(
            {"rejects-in-place-unit-approval"},
            failed_required_check_ids(case, output, SKILL_NAME),
        )

    def test_allows_diagnosis_of_existing_unbounded_retry(self) -> None:
        """Allow a correct answer to restate the diagnosed retry failure."""
        case = self.cases[3]
        output = case.expected_output + " Today the consumer retries forever."

        self.assertEqual(
            set(),
            failed_required_check_ids(case, output, SKILL_NAME),
        )


if __name__ == "__main__":
    unittest.main()
