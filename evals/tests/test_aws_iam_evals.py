"""Regression tests for discriminating AWS IAM eval assertions."""

import unittest
from typing import ClassVar

from evals.skill_eval import EvalCase
from evals.tests.eval_test_support import (
    assert_expected_outputs_pass,
    failed_required_check_ids,
    load_cases,
)

SKILL_NAME = "aws-iam"


class AwsIamEvalTests(unittest.TestCase):
    """Ensure unsafe or incomplete AWS IAM guidance cannot pass evals."""

    cases: ClassVar[dict[int, EvalCase]]

    @classmethod
    def setUpClass(cls) -> None:
        """Load the AWS IAM eval suite once."""
        cls.cases = load_cases(SKILL_NAME)

    def test_expected_outputs_satisfy_required_checks(self) -> None:
        """Confirm every canonical response satisfies its required checks."""
        assert_expected_outputs_pass(self, self.cases, SKILL_NAME)

    def test_unsafe_outputs_fail_key_checks_for_every_case(self) -> None:
        """Reject unsafe IAM guidance across every canonical scenario."""
        unsafe_outputs: dict[int, tuple[str, set[str]]] = {
            1: (
                "The identity policy allow overrides every restriction, so retry the request.",
                {
                    "states-deny-and-explicit-deny-precedence",
                    "covers-evaluation-inputs-and-layers",
                },
            ),
            2: (
                "Trust the entire vendor account without conditions because the shared value authenticates it.",
                {
                    "pins-vendor-and-external-id",
                    "explains-external-id-boundary",
                },
            ),
            3: (
                "Allow the service principal globally; deployment compatibility checks are unnecessary.",
                {
                    "requires-supported-source-condition",
                    "requires-service-specific-validation",
                },
            ),
            4: (
                "The identity policy alone grants decrypt. Create an unrestricted service grant with no constraints.",
                {
                    "diagnoses-key-policy",
                    "corrects-service-grant-design",
                },
            ),
            5: (
                "Attach another allow policy to override the organization guardrail immediately.",
                {
                    "states-scp-semantics",
                    "requires-hierarchy-and-independent-allow",
                },
            ),
        }

        self.assertEqual(set(self.cases), set(unsafe_outputs))
        for case_id, (output, expected_failures) in unsafe_outputs.items():
            with self.subTest(case=case_id):
                failed = failed_required_check_ids(
                    self.cases[case_id],
                    output,
                    SKILL_NAME,
                )
                self.assertTrue(expected_failures.issubset(failed))

    def test_rejects_keyword_complete_wildcard_kms_advice(self) -> None:
        """Reject unsafe polarity even when every positive token is present."""
        case = self.cases[4]
        output = case.expected_output + ' I recommend granting kms:* to Principal "*" for compatibility.'

        self.assertEqual(
            {"rejects-wildcard-kms-access"},
            failed_required_check_ids(case, output, SKILL_NAME),
        )

    def test_rejects_keyword_complete_lambda_source_account_advice(self) -> None:
        """Reject adding the condition even when the correct warning remains."""
        case = self.cases[3]
        output = case.expected_output + " I recommend adding aws:SourceAccount for extra protection."

        self.assertEqual(
            {"rejects-source-account-for-lambda"},
            failed_required_check_ids(case, output, SKILL_NAME),
        )

    def test_allows_explicit_lambda_source_account_prohibition(self) -> None:
        """Allow a correct modal prohibition without reversing its polarity."""
        case = self.cases[3]
        output = case.expected_output + " You must not use aws:SourceAccount here."

        self.assertEqual(
            set(),
            failed_required_check_ids(case, output, SKILL_NAME),
        )


if __name__ == "__main__":
    unittest.main()
