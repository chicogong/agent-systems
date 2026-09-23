"""Regression checks for the portable reading archive."""

from __future__ import annotations

import tempfile
import unittest
import zipfile
from pathlib import Path

from build_markdown import ARCHIVE_ROOT, build, manifest_entries


class MarkdownArchiveTests(unittest.TestCase):
    def test_manifest_has_one_order_for_both_exports(self) -> None:
        entries = manifest_entries()
        self.assertGreater(sum(kind != "part" for kind, _ in entries), 0)
        self.assertGreater(sum(kind == "part" for kind, _ in entries), 0)

    def test_archive_is_deterministic_and_reader_only(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            first = Path(temporary) / "one.zip"
            second = Path(temporary) / "two.zip"
            self.assertEqual(build(first), build(second))
            self.assertEqual(first.read_bytes(), second.read_bytes())
            with zipfile.ZipFile(first) as archive:
                names = set(archive.namelist())
                prefix = f"{ARCHIVE_ROOT}/"
                self.assertIn(prefix + "README.md", names)
                self.assertIn(prefix + "book/frontmatter/preface.md", names)
                self.assertIn(prefix + "docs/systems/pi/README.md", names)
                self.assertIn(prefix + "figures/pi-architecture/diagram.svg", names)
                self.assertIn(prefix + "figures/pi-architecture/preview.png", names)
                self.assertFalse(any(name.startswith(prefix + "scripts/") for name in names))
                self.assertFalse(any(name.startswith(prefix + "docs/pi-first.md") for name in names))
                index = archive.read(prefix + "README.md").decode("utf-8")
                self.assertIn(next(value for kind, value in manifest_entries() if kind == "part"), index)

    def test_authoring_links_can_be_pinned_to_a_release(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            archive_path = Path(temporary) / "release.zip"
            build(archive_path, "v1.0.0")
            with zipfile.ZipFile(archive_path) as archive:
                index = archive.read(f"{ARCHIVE_ROOT}/README.md").decode("utf-8")
                self.assertIn("/blob/v1.0.0/CONTRIBUTING.md", index)


if __name__ == "__main__":
    unittest.main()
