"""The public archive must match its exact, versioned source bundle."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from check_markdown_archive import check_archive


class ArchiveCheckTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.archive = Path(self.directory.name) / "reading.zip"
        self.archive.write_bytes(b"approved source bundle")
        self.commit = "a" * 40

    def expected(self, destination, commit):
        self.assertEqual(commit, self.commit)
        Path(destination).write_bytes(b"approved source bundle")

    def test_exact_versioned_bundle_passes(self):
        with patch("check_markdown_archive.build", side_effect=self.expected) as build:
            check_archive(self.archive, self.commit)
        build.assert_called_once()

    def test_other_archive_is_rejected(self):
        self.archive.write_bytes(b"extra or replaced private contents")
        with patch("check_markdown_archive.build", side_effect=self.expected):
            with self.assertRaisesRegex(ValueError, "approved source bundle"):
                check_archive(self.archive, self.commit)

    def test_short_or_malformed_reference_is_rejected(self):
        with patch("check_markdown_archive.build") as build:
            for reference in ("main", "a" * 12, "g" * 40, "A" * 40):
                with self.subTest(reference=reference):
                    with self.assertRaisesRegex(ValueError, "full source commit"):
                        check_archive(self.archive, reference)
        build.assert_not_called()


if __name__ == "__main__":
    unittest.main()
