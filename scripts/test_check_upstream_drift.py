from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from scripts.check_upstream_drift import audit_repository

VALID_SHA = "a" * 40
OTHER_SHA = "b" * 40


class CheckUpstreamDriftTests(unittest.TestCase):
    def test_real_repository_passes_pinned_audit(self) -> None:
        result = audit_repository()
        self.assertGreaterEqual(result["system_count"], 16)
        self.assertGreater(result["path_count"], 30)
        self.assertIn("pi", result["systems"])
        self.assertTrue(
            any("packages/agent/src/agent-loop.ts" in item for item in result["systems"]["pi"]["referenced_paths"])
        )

    def test_rejects_branch_url_and_mismatched_commit_sha(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "sources").mkdir()
            (root / "docs" / "systems" / "demo").mkdir(parents=True)
            (root / "sources" / "systems.json").write_text(
                json.dumps(
                    {
                        "demo": {
                            "scope": "loop",
                            "status": "static-slice-draft",
                            "upstream_license": "MIT",
                            "license_reviewed_at": "2026-10-01",
                            "versions": [f"https://github.com/org/demo/tree/{VALID_SHA}"],
                        }
                    }
                ),
                encoding="utf-8",
            )
            readme = root / "docs" / "systems" / "demo" / "README.md"

            readme.write_text(
                f"See [entry](https://github.com/org/demo/blob/{VALID_SHA}/src/loop.py).\n",
                encoding="utf-8",
            )
            ok = audit_repository(root)
            self.assertEqual(ok["systems"]["demo"]["referenced_paths"], ["org/demo:src/loop.py"])

            readme.write_text(
                "See [entry](https://github.com/org/demo/blob/main/src/loop.py).\n",
                encoding="utf-8",
            )
            with self.assertRaises(ValueError):
                audit_repository(root)

            readme.write_text(
                f"See [entry](https://github.com/org/demo/blob/{OTHER_SHA}/src/loop.py).\n",
                encoding="utf-8",
            )
            with self.assertRaises(ValueError):
                audit_repository(root)


if __name__ == "__main__":
    unittest.main()
