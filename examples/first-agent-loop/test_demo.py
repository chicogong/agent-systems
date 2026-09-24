"""Run with: python3 -m unittest discover -s examples/first-agent-loop -p 'test_*.py'"""

import unittest

from demo import run


class FirstAgentLoopTests(unittest.TestCase):
    def test_normal_path_needs_check_before_candidate(self) -> None:
        result = run("normal")
        self.assertEqual(result["status"], "candidate_ready")
        self.assertEqual(result["config"], {"timeout": 5, "retries": 3})
        self.assertEqual([event["tool"] for event in result["events"] if event["event"] == "tool_result"], ["read", "write", "check"])

    def test_denied_write_has_no_side_effect(self) -> None:
        result = run("denied")
        self.assertEqual(result["status"], "blocked")
        self.assertEqual(result["config"], {"timeout": 30, "retries": 3})
        self.assertIn({"event": "approval", "granted": False}, result["events"])

    def test_green_timeout_alone_does_not_hide_retry_regression(self) -> None:
        result = run("regression")
        self.assertEqual(result["status"], "blocked")
        self.assertEqual(result["config"], {"timeout": 5, "retries": 0})
        self.assertIn("retry rule changed", [event["detail"] for event in result["events"] if event["event"] == "tool_result"])


if __name__ == "__main__":
    unittest.main()
