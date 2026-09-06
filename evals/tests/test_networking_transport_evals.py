"""Regression tests for discriminating networking transport evals."""

import unittest
from typing import ClassVar

from evals.skill_eval import EvalCase
from evals.tests.eval_test_support import (
    assert_expected_outputs_pass,
    failed_required_check_ids,
    load_cases,
)

SKILL_NAME = "networking-transport"


class NetworkingTransportEvalTests(unittest.TestCase):
    """Ensure unsafe or incomplete transport guidance cannot pass evals."""

    cases: ClassVar[dict[int, EvalCase]]

    @classmethod
    def setUpClass(cls) -> None:
        """Load the networking transport eval cases once."""
        cls.cases = load_cases(SKILL_NAME)

    def failed_checks(self, case_id: int, output: str) -> set[str]:
        """Return failed required checks for one synthetic response."""
        return failed_required_check_ids(self.cases[case_id], output, SKILL_NAME)

    def test_expected_outputs_satisfy_required_checks(self) -> None:
        """Prove every canonical response passes its required checks."""
        assert_expected_outputs_pass(self, self.cases, SKILL_NAME)

    def test_rejects_per_request_http_clients(self) -> None:
        """Reject per-call pools and missing transport lifecycle controls."""
        failed = self.failed_checks(
            1,
            "Create a fresh http.Client and Transport for every request and rely "
            "on defaults without cancellation or body cleanup.",
        )

        self.assertIn("reuses-client-and-pool", failed)
        self.assertIn("sets-transport-lifecycle", failed)
        self.assertIn("preserves-call-lifecycle", failed)

    def test_rejects_single_hop_timeout_tuning(self) -> None:
        """Reject client-only tuning that conflates timeout responsibilities."""
        failed = self.failed_checks(
            2,
            "Only raise the load balancer timeout to 75 seconds; TCP keepalive "
            "already provides the request deadline, so heartbeats are unnecessary.",
        )

        self.assertIn("finds-minimum-hop-timeout", failed)
        self.assertIn("adds-portable-heartbeat", failed)
        self.assertIn("separates-timeout-purposes", failed)
        self.assertIn("aligns-hop-policy", failed)

    def test_rejects_native_grpc_for_browser_feed(self) -> None:
        """Reject forcing an internal RPC transport onto browser clients."""
        failed = self.failed_checks(
            3,
            "Expose native gRPC directly to browsers for queries and the one-way "
            "event feed; no browser adapter or fallback is needed.",
        )

        self.assertIn("preserves-fitting-internal-grpc", failed)
        self.assertIn("uses-browser-native-contracts", failed)
        self.assertIn("conditions-alternatives", failed)

    def test_rejects_keyword_complete_native_browser_grpc(self) -> None:
        """Reject unsafe polarity even when every positive token is present."""
        output = self.cases[3].expected_output + " I recommend native gRPC for the browser console."

        self.assertEqual(
            {"rejects-native-grpc-for-browser"},
            self.failed_checks(3, output),
        )

    def test_rejects_http3_without_path_evidence(self) -> None:
        """Reject an unconditional HTTP/3 migration without fallback metrics."""
        failed = self.failed_checks(
            4,
            "Replace HTTP/2 everywhere with HTTP/3 immediately; packet loss is an "
            "origin problem and UDP reachability needs no validation.",
        )

        self.assertIn("diagnoses-h2-hol", failed)
        self.assertIn("explains-h3-fit", failed)
        self.assertIn("requires-path-and-fallback-evidence", failed)

    def test_rejects_non_resumable_immediate_sse_reconnects(self) -> None:
        """Reject reconnect behavior that loses events and creates a surge."""
        failed = self.failed_checks(
            5,
            "Always restart at the newest event and reconnect every client "
            "immediately; retain no cursor history or heartbeat.",
        )

        self.assertIn("defines-resumable-sse", failed)
        self.assertIn("bounds-replay-contract", failed)
        self.assertIn("controls-idle-and-reconnect", failed)


if __name__ == "__main__":
    unittest.main()
