"""Regression checks for the author-source Markdown link boundary."""

from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase, main
from unittest.mock import patch

import check_repo


class CheckLinksTest(TestCase):
    def test_generated_site_markdown_is_not_treated_as_book_source(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            (root / "README.md").write_text("# Root\n", encoding="utf-8")
            (root / "docs").mkdir()
            (root / "docs" / "valid.md").write_text("[root](../README.md)\n", encoding="utf-8")
            generated = root / "site" / "content"
            generated.mkdir(parents=True)
            (generated / "generated.md").write_text("[route](/a-public-route)\n", encoding="utf-8")
            dependency = root / "site" / "node_modules" / "example"
            dependency.mkdir(parents=True)
            (dependency / "README.md").write_text("[package link](missing.md)\n", encoding="utf-8")
            with patch.object(check_repo, "ROOT", root):
                self.assertEqual(check_repo.check_links(), [])

    def test_broken_author_source_link_is_reported(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            (root / "docs").mkdir()
            (root / "docs" / "broken.md").write_text("[missing](no-such-file.md)\n", encoding="utf-8")
            with patch.object(check_repo, "ROOT", root):
                self.assertEqual(check_repo.check_links(), ["docs/broken.md -> no-such-file.md"])


if __name__ == "__main__":
    main()
