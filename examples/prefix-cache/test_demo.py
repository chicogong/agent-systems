import json
from pathlib import Path
import subprocess
import sys
import unittest

from demo import run


class PrefixCacheDemoTests(unittest.TestCase):
    def test_layered_hit_achieves_high_cache_rate(self):
        result = run("layered_hit")
        self.assertEqual(result["status"], "high_cache_hit")
        self.assertEqual(result["total_turns"], 5)
        ledger = result["ledger"]
        self.assertEqual(ledger["total_input_tokens"], 38100)
        self.assertEqual(ledger["cumulative_cached_tokens"], 36600)
        self.assertEqual(ledger["cumulative_uncached_tokens"], 1500)
        self.assertEqual(ledger["overall_hit_rate"], "96.06%")
        self.assertTrue(float(ledger["overall_hit_rate"].rstrip("%")) > 95.0)

        # Step 2: after append, 7000 tokens from Step 1 are cached
        step2 = result["turns"][1]
        self.assertEqual(step2["input_tokens"], 7300)
        self.assertEqual(step2["cache_read_tokens"], 7000)
        self.assertEqual(step2["uncached_tokens"], 300)
        self.assertEqual(step2["prefix_status"], "prefix_hit")

    def test_dynamic_timestamp_busts_entire_cache(self):
        result = run("dynamic_timestamp")
        self.assertEqual(result["status"], "cache_bust_timestamp")
        ledger = result["ledger"]
        self.assertEqual(ledger["cumulative_cached_tokens"], 0)
        self.assertEqual(ledger["cumulative_uncached_tokens"], 38100)
        self.assertEqual(ledger["overall_hit_rate"], "0.00%")
        for step in result["turns"]:
            self.assertEqual(step["cache_read_tokens"], 0)
            self.assertEqual(step["uncached_tokens"], step["input_tokens"])

    def test_shuffled_tools_causes_partial_miss(self):
        result = run("shuffled_tools")
        self.assertEqual(result["status"], "cache_bust_shuffled")
        ledger = result["ledger"]
        # System prompt matches (6000 tokens), but tools and messages diverged
        self.assertEqual(ledger["cumulative_cached_tokens"], 24000)
        self.assertTrue(float(ledger["overall_hit_rate"].rstrip("%")) < 65.0)
        for step in result["turns"][1:]:
            self.assertEqual(step["cache_read_tokens"], 6000)
            self.assertEqual(step["prefix_status"], "partial_miss_tools_diverged")

    def test_invalid_mode_raises(self):
        with self.assertRaises(ValueError):
            run("invalid_mode")

    def test_cli_execution(self):
        completed = subprocess.run(
            [sys.executable, str(Path(__file__).with_name("demo.py")), "--mode", "layered_hit"],
            capture_output=True,
            text=True,
            check=True,
        )
        data = json.loads(completed.stdout)
        self.assertEqual(data["status"], "high_cache_hit")
        self.assertEqual(data["mode"], "layered_hit")
        self.assertEqual(data["ledger"]["overall_hit_rate"], "96.06%")


if __name__ == "__main__":
    unittest.main()
