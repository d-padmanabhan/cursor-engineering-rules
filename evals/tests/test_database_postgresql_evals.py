"""Regression tests for database-postgresql eval checks."""

import unittest
from typing import ClassVar

from evals.skill_eval import EvalCase
from evals.tests.eval_test_support import (
    assert_expected_outputs_pass,
    failed_required_check_ids,
    load_cases,
)

SKILL_NAME = "database-postgresql"


class DatabasePostgresqlEvalTests(unittest.TestCase):
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
        """Reject unsafe database advice for every eval scenario."""
        scenarios = {
            1: (
                "Use tenant_id in a SELECT filter and let the table owner handle writes.",
                {
                    "requires-read-and-write-policy",
                    "explains-implicit-write-check",
                    "bounds-role-and-session-context",
                    "tests-cross-tenant-denials",
                },
            ),
            2: (
                "Build the lookup with string concatenation and quote order_id manually.",
                {"uses-driver-parameters", "rejects-value-interpolation"},
            ),
            3: (
                "Execute the unfiltered cleanup immediately and commit it.",
                {
                    "previews-scoped-rowset",
                    "bounds-and-verifies-delete",
                    "rejects-unreviewed-delete",
                },
            ),
            4: (
                "Run CREATE INDEX inside BEGIN and assume success when the command returns.",
                {
                    "uses-concurrent-index-outside-transaction",
                    "bounds-lock-risk",
                    "handles-invalid-index",
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

    def test_rejects_keyword_complete_broad_delete_approval(self) -> None:
        """Reject unsafe polarity even when every positive token is present."""
        case = self.cases[3]
        output = case.expected_output + " It is safe to run a broad DELETE."

        self.assertEqual(
            {"rejects-broad-delete-approval"},
            failed_required_check_ids(case, output, SKILL_NAME),
        )


if __name__ == "__main__":
    unittest.main()
