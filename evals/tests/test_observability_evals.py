"""Regression tests for discriminating observability eval assertions."""

import tempfile
import unittest
from pathlib import Path

from evals.skill_eval import AdapterResponse, EvalCase, evaluate_checks, load_eval_suite

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
OBSERVABILITY_SKILL_DIRECTORY = REPOSITORY_ROOT / "skills" / "observability"


class ObservabilityEvalTests(unittest.TestCase):
    """Ensure unsafe or incomplete observability guidance cannot pass evals."""

    @classmethod
    def setUpClass(cls) -> None:
        """Load the observability eval suite once."""
        suite = load_eval_suite(OBSERVABILITY_SKILL_DIRECTORY)
        if suite is None:
            raise AssertionError("observability eval suite is missing")
        cls.cases = {case.identifier: case for case in suite.cases}

    def failed_check_ids(self, case: EvalCase, output: str) -> set[str]:
        """Return failed required check identifiers for one response."""
        response = AdapterResponse(output=output, events=(), usage={}, raw={})
        with tempfile.TemporaryDirectory() as temp_directory:
            results = evaluate_checks(
                case.checks,
                response,
                Path(temp_directory),
                default_skill="observability",
            )
        return {result.identifier for result in results if result.required and not result.passed}

    def test_container_logging_rejects_growing_json_file(self) -> None:
        """Reject an application-owned array and rotation design."""
        output = "Append each event to one JSON array in /var/log/app.json."

        failed = self.failed_check_ids(self.cases[1], output)

        self.assertIn("uses-container-streams", failed)
        self.assertIn("defines-one-event-per-line", failed)
        self.assertIn("does-not-mandate-ndjson-transport", failed)
        self.assertIn("defines-output-failure", failed)

    def test_structured_logging_rejects_json_is_safe_claim(self) -> None:
        """Reject sensitive fields and multiline values despite JSON output."""
        output = "Keep every field because structured JSON is safe to index."

        failed = self.failed_check_ids(self.cases[2], output)

        self.assertIn("removes-secrets-and-raw-payloads", failed)
        self.assertIn("governs-personal-data", failed)
        self.assertIn("prevents-log-injection", failed)
        self.assertIn("bounds-error-context", failed)

    def test_metrics_reject_high_cardinality_labels(self) -> None:
        """Reject request-level values used as metric dimensions."""
        output = "Add all identifiers as labels for precise filtering."

        failed = self.failed_check_ids(self.cases[3], output)

        self.assertIn("rejects-unbounded-labels", failed)
        self.assertIn("uses-bounded-dimensions", failed)
        self.assertIn("estimates-series-budget", failed)
        self.assertIn("routes-high-cardinality-detail", failed)

    def test_tracing_rejects_baggage_authorization(self) -> None:
        """Reject unrelated traces and caller-controlled authorization."""
        output = "Trust is_admin from baggage and create a fresh trace at each hop."

        failed = self.failed_check_ids(self.cases[4], output)

        self.assertIn("propagates-trace-context", failed)
        self.assertIn("rejects-baggage-authorization", failed)
        self.assertIn("uses-trusted-identity-policy", failed)
        self.assertIn("bounds-baggage", failed)

    def test_alerting_rejects_cpu_only_page(self) -> None:
        """Reject a copied resource threshold with no response contract."""
        output = "Page whenever CPU exceeds 80 percent."

        failed = self.failed_check_ids(self.cases[5], output)

        self.assertIn("rejects-cpu-only-page", failed)
        self.assertIn("uses-slo-burn-alerting", failed)
        self.assertIn("requires-operational-contract", failed)
        self.assertIn("tests-alert", failed)

    def test_pipeline_rejects_unbounded_zero_loss_claim(self) -> None:
        """Reject infinite buffering and a false durability guarantee."""
        output = "Use infinite retries and a persistent queue for zero loss."

        failed = self.failed_check_ids(self.cases[6], output)

        self.assertIn("rejects-zero-loss-claim", failed)
        self.assertIn("bounds-pipeline-resources", failed)
        self.assertIn("defines-overload-policy", failed)
        self.assertIn("monitors-pipeline-loss", failed)

    def test_audit_rejects_sampled_mutable_application_logs(self) -> None:
        """Reject sampled application logs as a regulated audit trail."""
        output = "The mutable seven-day application index is the audit trail."

        failed = self.failed_check_ids(self.cases[7], output)

        self.assertIn("requires-audit-fields", failed)
        self.assertIn("requires-audit-integrity", failed)
        self.assertIn("separates-diagnostic-logs", failed)


if __name__ == "__main__":
    unittest.main()
