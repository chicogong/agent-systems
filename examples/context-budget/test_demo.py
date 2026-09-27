import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

from demo import BudgetTooSmall, HISTORY, QUESTION, assemble, judge_visible, retrieve, run


class ContextBudgetTests(unittest.TestCase):
    def test_full_selection_keeps_all_records(self):
        result = run("full")
        self.assertEqual(result["visible_ids"], ["r5", "r4", "r3", "r2", "r1"])
        self.assertEqual((result["budget"], result["used_characters"], result["required_characters"]), (1200, 248, 56))
        self.assertEqual(result["answer"]["status"], "do_not_publish")
        self.assertLessEqual(result["used_characters"], result["budget"])

    def test_required_input_never_silently_truncated(self):
        with self.assertRaises(BudgetTooSmall):
            assemble(HISTORY, QUESTION, 10)
        with patch("demo.judge_visible", side_effect=AssertionError("reader must not be called")):
            result = run("recent", 10)
        self.assertEqual(result["status"], "budget_too_small")
        self.assertIsNone(result["answer"])
        self.assertIsNone(result["context"])
        self.assertGreater(result["required_characters"], result["budget"])
        self.assertEqual(result["required_characters"], 56)

    def test_recent_selection_omits_old_critical_constraint(self):
        result = run("recent")
        self.assertTrue(result["audit"]["critical_record_stored"])
        self.assertFalse(result["audit"]["critical_record_visible"])
        self.assertEqual(result["answer"]["status"], "insufficient_evidence")
        self.assertNotIn(HISTORY[0].text, result["context"])
        self.assertEqual(result["visible_ids"], ["r5", "r4", "r3", "r2"])
        self.assertEqual((result["budget"], result["used_characters"]), (220, 212))
        self.assertEqual(result["events"][-1], {
            "event": "select_record", "id": "r1", "characters": 36,
            "remaining_before": 8, "selected": False, "reason": "whole_record_does_not_fit",
        })
        self.assertLessEqual(result["used_characters"], result["budget"])

    def test_retrieval_reassembles_with_same_budget(self):
        recent, recovered = run("recent"), run("retrieve")
        self.assertEqual(retrieve(HISTORY, "用户批准"), ("r1",))
        self.assertEqual(recent["budget"], recovered["budget"])
        self.assertTrue(recovered["audit"]["critical_record_visible"])
        self.assertEqual(recovered["answer"]["status"], "do_not_publish")
        self.assertLessEqual(recovered["used_characters"], recovered["budget"])
        self.assertNotEqual(recent["visible_ids"], recovered["visible_ids"])
        self.assertEqual(recovered["visible_ids"], ["r1", "r5", "r4", "r3"])
        self.assertEqual(recovered["used_characters"], 217)

    def test_reader_cannot_read_stored_history_without_context(self):
        with patch("demo.HISTORY", None):
            self.assertEqual(judge_visible("")["status"], "insufficient_evidence")
            self.assertEqual(judge_visible("没有用户批准，不得对外发布")["status"], "do_not_publish")

    def test_retrieval_hit_does_not_guarantee_it_fits(self):
        result = run("retrieve", 91)
        self.assertEqual(result["retrieval"]["matched_ids"], ["r1"])
        self.assertFalse(result["audit"]["critical_record_visible"])
        self.assertEqual(result["answer"]["status"], "insufficient_evidence")
        self.assertEqual(result["visible_ids"], ["r3"])
        self.assertEqual(result["used_characters"], 91)
        self.assertLessEqual(result["used_characters"], result["budget"])

    def test_recent_selection_recovers_at_documented_total_budget(self):
        result = run("recent", 248)
        self.assertEqual(result["visible_ids"], ["r5", "r4", "r3", "r2", "r1"])
        self.assertEqual(result["used_characters"], 248)
        self.assertTrue(result["audit"]["answer_recovered_constraint"])

    def test_cli_rejects_too_small_budget_without_crashing(self):
        completed = subprocess.run(
            [sys.executable, str(Path(__file__).with_name("demo.py")), "--mode", "recent", "--budget", "10"],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(completed.returncode, 2)
        result = json.loads(completed.stdout)
        self.assertEqual(result["status"], "budget_too_small")
        self.assertEqual(result["required_characters"], 56)
        self.assertIsNone(result["answer"])
        self.assertEqual(completed.stderr, "")

    def test_record_is_kept_whole_at_exact_boundary(self):
        empty = assemble((), QUESTION, 1200)
        size = len(f"[{HISTORY[0].id}] {HISTORY[0].text}\n")
        exact = assemble((HISTORY[0],), QUESTION, empty["used_characters"] + size)
        too_short = assemble((HISTORY[0],), QUESTION, empty["used_characters"] + size - 1)
        self.assertEqual(exact["visible_ids"], ["r1"])
        self.assertEqual(too_short["visible_ids"], [])
        self.assertNotIn(HISTORY[0].text[:5], too_short["context"])


if __name__ == "__main__":
    unittest.main()
