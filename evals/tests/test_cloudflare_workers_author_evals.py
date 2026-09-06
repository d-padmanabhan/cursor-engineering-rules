"""Regression tests for discriminating Cloudflare Workers authoring evals."""

import unittest
from typing import ClassVar

from evals.skill_eval import EvalCase
from evals.tests.eval_test_support import (
    assert_expected_outputs_pass,
    failed_required_check_ids,
    load_cases,
)

SKILL_NAME = "cloudflare-workers-author"


class CloudflareWorkersAuthorEvalTests(unittest.TestCase):
    """Ensure obsolete or unsafe Workers guidance cannot pass the eval suite."""

    cases: ClassVar[dict[int, EvalCase]]

    @classmethod
    def setUpClass(cls) -> None:
        """Load the Cloudflare Workers eval cases once."""
        cls.cases = load_cases(SKILL_NAME)

    def failed_checks(self, case_id: int, output: str) -> set[str]:
        """Return failed required checks for one synthetic response."""
        return failed_required_check_ids(self.cases[case_id], output, SKILL_NAME)

    def test_expected_outputs_satisfy_required_checks(self) -> None:
        """Prove every canonical response passes its required checks."""
        assert_expected_outputs_pass(self, self.cases, SKILL_NAME)

    def test_rejects_service_worker_and_handwritten_bindings(self) -> None:
        """Reject obsolete handlers and duplicated binding declarations."""
        failed = self.failed_checks(
            1,
            "Use addEventListener('fetch', handler), hand-write interface Env, and install @cloudflare/workers-types.",
        )

        self.assertIn("uses-module-worker", failed)
        self.assertIn("uses-generated-types", failed)

    def test_rejects_isolate_state_and_detached_telemetry(self) -> None:
        """Reject request state in module scope and untracked background work."""
        failed = self.failed_checks(
            2,
            "Keep currentAccount in a global variable and start telemetry after "
            "returning the response without waiting for it.",
        )

        self.assertIn("removes-request-state-from-isolate", failed)
        self.assertIn("attaches-background-work", failed)

    def test_rejects_kv_as_chat_coordinator(self) -> None:
        """Reject eventually consistent KV for concurrent room ownership."""
        failed = self.failed_checks(
            3,
            "Store membership in KV and let every isolate coordinate joins and broadcast independently.",
        )

        self.assertIn("selects-room-coordinator", failed)
        self.assertIn("defines-binding-route-and-storage", failed)
        self.assertIn("rejects-kv-coordination", failed)

    def test_rejects_keyword_complete_kv_coordination(self) -> None:
        """Reject unsafe polarity even when every positive token is present."""
        output = self.cases[3].expected_output + " I recommend using KV to coordinate room membership."

        self.assertEqual(
            {"rejects-kv-as-coordinator"},
            self.failed_checks(3, output),
        )

    def test_rejects_removed_vitest_pool_apis(self) -> None:
        """Reject pre-v1 testing APIs in favor of the current plugin contract."""
        failed = self.failed_checks(
            4,
            "Import defineWorkersConfig from @cloudflare/vitest-pool-workers/config, "
            "list @cloudflare/vitest-pool-workers in types, and use unstable_dev.",
        )

        self.assertIn("uses-current-config-api", failed)
        self.assertIn("uses-current-types-and-runtime", failed)
        self.assertIn("rejects-removed-testing-paths", failed)

    def test_rejects_immediate_full_traffic_rollout(self) -> None:
        """Reject deployment without staged evidence or rollback."""
        failed = self.failed_checks(
            5,
            "Run wrangler deploy, immediately route all customer traffic to the "
            "new code, and fix forward if metrics regress.",
        )

        self.assertIn("uploads-without-traffic", failed)
        self.assertIn("smoke-tests-specific-version", failed)
        self.assertIn("stages-and-gates-promotion", failed)
        self.assertIn("defines-version-rollback", failed)


if __name__ == "__main__":
    unittest.main()
