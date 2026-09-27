"""Real loopback requests plus synthetic ledger contract assertions."""
from concurrent.futures import ThreadPoolExecutor
import socket
import time
import unittest
from unittest.mock import patch

import demo

from demo import MODES, accepted, replay_status, request, run, running_service


class HttpReceiptTests(unittest.TestCase):
    def test_normal(self):
        result = run("normal")
        self.assertEqual(result["host"]["status"], "confirmed_receipt")
        self.assertEqual(result["host"]["events"][0]["http_status"], 201)

    def test_real_timeout_then_lookup(self):
        result = run("timeout_then_lookup")
        self.assertEqual(result["host"]["status"], "confirmed_lookup")
        self.assertEqual(result["host"]["events"][0]["transport"], "timeout")
        self.assertEqual(result["observer_after_cleanup"]["registered_effects"], 1)

    def test_same_id_replay(self):
        result = run("same_id_retry")
        self.assertEqual(result["host"]["status"], "confirmed_replay")
        self.assertTrue(result["host"]["events"][1]["body"]["replayed"])
        self.assertEqual(result["observer_after_cleanup"]["registered_effects"], 1)

    def test_stale_lookup_stays_unknown(self):
        result = run("lookup_lag")
        self.assertEqual(result["host"]["status"], "unknown_stop")
        self.assertEqual(result["host"]["events"][1]["http_status"], 404)
        self.assertEqual(result["observer_after_cleanup"]["registered_effects"], 1)

    def test_late_original_request_is_not_cancelled(self):
        result = run("late_commit")
        self.assertEqual(result["host"]["status"], "unknown_stop")
        self.assertEqual(result["host"]["events"][1]["http_status"], 404)
        self.assertEqual(result["observer_after_cleanup"]["registered_effects"], 1)
        self.assertEqual([x["event"] for x in result["observer_after_cleanup"]["events"]][:3],
                         ["received", "lookup_reply", "registered"])

    def test_bad_new_id_causes_two_registrations(self):
        result = run("unsafe_new_id")
        self.assertEqual(result["host"]["status"], "duplicate_effect")
        self.assertEqual(result["observer_after_cleanup"]["registered_effects"], 2)

    def test_payload_conflict_is_rejected(self):
        result = run("payload_conflict")
        self.assertEqual(result["host"]["status"], "conflict_stop")
        self.assertEqual(result["host"]["events"][1]["http_status"], 409)
        self.assertEqual(list(result["observer_after_cleanup"]["operations"].values()), ["publish-v1"])

    def test_atomic_parallel_deduplication(self):
        with running_service() as (port, ledger):
            with ThreadPoolExecutor(max_workers=4) as workers:
                results = list(workers.map(lambda _n: request(port, "POST", "/operations",
                                   {"operation_id": "same-key", "payload": "same-value"}), range(4)))
            self.assertEqual(sorted(x["http_status"] for x in results), [200, 200, 200, 201])
            self.assertEqual(ledger.snapshot()["registered_effects"], 1)

    def test_invalid_body_cannot_register(self):
        with running_service() as (port, ledger):
            result = request(port, "POST", "/operations", {"operation_id": "../bad", "payload": "x"})
            self.assertEqual(result["http_status"], 400)
            self.assertEqual(ledger.snapshot()["registered_effects"], 0)

    def test_lookup_missing(self):
        with running_service() as (port, _ledger):
            self.assertEqual(request(port, "GET", "/operations/missing")["http_status"], 404)

    def test_closed_even_when_caller_raises(self):
        with self.assertRaisesRegex(RuntimeError, "caller failure"):
            with running_service() as (port, _ledger):
                raise RuntimeError("caller failure")
        with self.assertRaises(OSError):
            with socket.create_connection(("127.0.0.1", port), timeout=0.1):
                pass

    def test_receipt_must_match_key_and_payload(self):
        result = {"http_status": 200, "body": {"status": "accepted", "operation_id": "a", "payload": "b"}}
        self.assertTrue(accepted(result, "a", "b"))
        self.assertFalse(accepted(result, "a", "other"))
        self.assertFalse(accepted(result, "other", "b"))

    def test_invalid_mode(self):
        self.assertEqual(len(MODES), 7)
        with self.assertRaises(ValueError):
            run("not-a-mode")

    def test_replay_timeout_is_unknown(self):
        self.assertEqual(replay_status({"transport": "timeout", "http_status": None}, "a", "b"),
                         "unknown_stop")

    def test_conflict_requires_matching_receipt(self):
        result = {"http_status": 409, "body": {"status": "payload_conflict", "operation_id": "a"}}
        self.assertEqual(replay_status(result, "a", "b"), "conflict_stop")
        self.assertEqual(replay_status(result, "other", "b"), "unknown_stop")
        self.assertEqual(replay_status({"http_status": 500, "body": result["body"]}, "a", "b"), "unknown_stop")

    def test_registration_precedes_read_timeout_even_if_processing_is_slow(self):
        moments = {}
        original_register, original_request = demo.Ledger.register, demo.request

        def slow_register(ledger, operation_id, payload):
            time.sleep(0.25)  # deliberately longer than the 0.15s socket timeout
            result = original_register(ledger, operation_id, payload)
            moments["registered"] = time.monotonic()
            return result

        def observe_request(*args, **kwargs):
            result = original_request(*args, **kwargs)
            if result.get("transport") == "timeout":
                moments["timed_out"] = time.monotonic()
            return result

        with patch.object(demo.Ledger, "register", slow_register), patch.object(demo, "request", observe_request):
            result = run("timeout_then_lookup")
        self.assertLess(moments["registered"], moments["timed_out"])
        self.assertEqual(result["host"]["status"], "confirmed_lookup")


if __name__ == "__main__":
    unittest.main()
