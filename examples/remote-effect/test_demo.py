"""Assertions for the four deterministic reconciliation paths."""

import unittest

from demo import run


class RemoteEffectTests(unittest.TestCase):
    def test_normal_receipt(self) -> None:
        result = run("normal")
        self.assertEqual((result["status"], result["effects"]), ("confirmed", 1))

    def test_lost_receipt_is_reconciled(self) -> None:
        result = run("lost_receipt")
        self.assertEqual((result["status"], result["effects"]), ("confirmed_by_lookup", 1))
        self.assertEqual(result["events"][1]["result"], "accepted")

    def test_no_lookup_stops_unknown(self) -> None:
        result = run("no_lookup")
        self.assertEqual((result["status"], result["effects"]), ("unknown_stop", 1))
        self.assertFalse(any(event["event"] == "unsafe_retry" for event in result["events"]))

    def test_new_id_duplicates_effect(self) -> None:
        result = run("unsafe_new_id")
        self.assertEqual((result["status"], result["effects"]), ("duplicate_effect", 2))


if __name__ == "__main__":
    unittest.main()
