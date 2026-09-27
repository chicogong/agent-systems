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

    def test_html_thumbnail_source_is_checked(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            (root / "README.md").write_text('<img src="missing-preview.png" alt="preview">\n', encoding="utf-8")
            with patch.object(check_repo, "ROOT", root):
                self.assertEqual(check_repo.check_links(), ["README.md -> missing-preview.png"])

    def test_stale_heading_anchor_is_reported(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            (root / "README.md").write_text("# 首页\n\n## 你可以怎样读\n", encoding="utf-8")
            (root / "book").mkdir()
            (root / "book" / "CONTENTS.md").write_text("[旧入口](../README.md#从问题进入)\n", encoding="utf-8")
            with patch.object(check_repo, "ROOT", root):
                self.assertEqual(check_repo.check_links(), ["book/CONTENTS.md -> ../README.md#从问题进入 (missing heading anchor)"])

    def test_encoded_local_heading_anchor_is_valid(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            (root / "README.md").write_text("## 中文标题\n\n[本页](#%E4%B8%AD%E6%96%87%E6%A0%87%E9%A2%98)\n", encoding="utf-8")
            with patch.object(check_repo, "ROOT", root):
                self.assertEqual(check_repo.check_links(), [])

    def test_heading_slug_ignores_code_blocks_and_supports_duplicates(self) -> None:
        anchors = check_repo.markdown_anchors("## **运行** `exec_command()`：结果？\n\n```md\n## 假标题\n```\n## 重复\n## 重复\n")
        self.assertEqual(anchors, {"运行-exec_command结果", "重复", "重复-1"})


if __name__ == "__main__":
    main()
