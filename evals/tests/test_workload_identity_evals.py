"""Regression tests for discriminating workload identity eval assertions."""

import unittest
from typing import ClassVar

from evals.skill_eval import EvalCase
from evals.tests.eval_test_support import (
    assert_expected_outputs_pass,
    failed_required_check_ids,
    load_cases,
)

SKILL_NAME = "workload-identity"


class WorkloadIdentityEvalTests(unittest.TestCase):
    """Ensure unsafe or incomplete workload identity guidance cannot pass evals."""

    cases: ClassVar[dict[int, EvalCase]]

    @classmethod
    def setUpClass(cls) -> None:
        """Load the workload identity eval suite once."""
        cls.cases = load_cases(SKILL_NAME)

    def test_expected_outputs_satisfy_required_checks(self) -> None:
        """Confirm every canonical response satisfies its required checks."""
        assert_expected_outputs_pass(self, self.cases, SKILL_NAME)

    def test_unsafe_outputs_fail_key_checks_for_every_case(self) -> None:
        """Reject unsafe identity guidance across every canonical scenario."""
        unsafe_outputs: dict[int, tuple[str, set[str]]] = {
            1: (
                "Use one shared static credential system for both workloads and leave ownership undefined.",
                {
                    "selects-substrate-per-workload",
                    "defines-platform-boundary",
                },
            ),
            2: (
                "Reuse the shared identity in every environment and select workloads by the latest image tag.",
                {
                    "separates-trust-domain",
                    "requires-narrow-immutable-selectors",
                },
            ),
            3: (
                "Any client with a valid certificate may adjust inventory because transport security is sufficient.",
                {
                    "separates-authentication-authorization",
                    "binds-explicit-principal-and-operation",
                },
            ),
            4: (
                "Trust every token from the provider, accept wildcard identities, and issue permanent credentials.",
                {
                    "pins-oidc-subject-and-audience",
                    "requires-short-lived-validated-audited-flow",
                },
            ),
            5: (
                "Delete the old credential before deployment and replace it with a shared permanent access key.",
                {
                    "replaces-static-key-with-bound-irsa",
                    "requires-reversible-cutover-and-evidence",
                    "prevents-static-secret-regression",
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

    def test_rejects_keyword_complete_broad_oidc_trust(self) -> None:
        """Reject unsafe polarity even when every positive token is present."""
        case = self.cases[4]
        output = case.expected_output + " I recommend trusting the issuer alone."

        self.assertEqual(
            {"rejects-broad-oidc-trust"},
            failed_required_check_ids(case, output, SKILL_NAME),
        )


if __name__ == "__main__":
    unittest.main()
