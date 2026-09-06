"""Shared assertions for deterministic skill eval regression tests."""

import tempfile
import unittest
from pathlib import Path

from evals.skill_eval import AdapterResponse, EvalCase, evaluate_checks, load_eval_suite

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


def load_cases(skill_name: str) -> dict[int, EvalCase]:
    """Load one skill suite and index its cases by identifier."""

    suite = load_eval_suite(REPOSITORY_ROOT / "skills" / skill_name)
    if suite is None:
        raise AssertionError(f"{skill_name} eval suite is missing")
    return {case.identifier: case for case in suite.cases}


def failed_required_check_ids(
    case: EvalCase,
    output: str,
    skill_name: str,
) -> set[str]:
    """Return failed required check identifiers for one synthetic response."""

    response = AdapterResponse(output=output, events=(), usage={}, raw={})
    with tempfile.TemporaryDirectory() as temp_directory:
        results = evaluate_checks(
            case.checks,
            response,
            Path(temp_directory),
            default_skill=skill_name,
        )
    return {result.identifier for result in results if result.required and not result.passed}


def assert_expected_outputs_pass(
    test_case: unittest.TestCase,
    cases: dict[int, EvalCase],
    skill_name: str,
) -> None:
    """Assert that every canonical expected output satisfies required checks."""

    for case in cases.values():
        with test_case.subTest(case=case.identifier):
            test_case.assertEqual(
                set(),
                failed_required_check_ids(case, case.expected_output, skill_name),
            )
