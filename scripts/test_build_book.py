"""Public PDF links must resolve without access to the private authoring repo."""

from __future__ import annotations

import unittest
from tempfile import TemporaryDirectory
from pathlib import Path

from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Flowable, Image, Paragraph

import build_book


class PublicBookLinkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        build_book.prepare_public_links(build_book.manifest_paths())

    def tearDown(self) -> None:
        build_book.PUBLIC_LINKS = False

    def test_public_chapter_and_figure_links(self) -> None:
        build_book.PUBLIC_LINKS = True
        source = build_book.ROOT / "docs/systems/pi/README.md"
        chapter = build_book.inline("[导读](code-walkthrough.md)", source)
        figure = build_book.inline("[文字版](../../../figures/pi-architecture/README.md)", source)
        editable = build_book.inline("[可编辑图源](../../../figures/pi-architecture/scene.excalidraw)", source)
        self.assertIn('href="https://books.aimake.cc/systems/pi/code-walkthrough"', chapter)
        self.assertIn('href="https://books.aimake.cc/systems/pi#图的文字说明-pi-architecture"', figure)
        self.assertNotIn("href=", editable)
        self.assertNotIn("github.com/chicogong/agent-systems", chapter + figure + editable)

    def test_private_review_keeps_authoring_link(self) -> None:
        source = build_book.ROOT / "docs/systems/pi/README.md"
        private = build_book.inline("[可编辑图源](../../../figures/pi-architecture/scene.excalidraw)", source)
        self.assertIn("github.com/chicogong/agent-systems/blob/main", private)


class BookListTests(unittest.TestCase):
    def test_ordered_list_keeps_start_and_continuity(self) -> None:
        with TemporaryDirectory() as directory:
            source = Path(directory) / "chapter.md"
            source.write_text("1. First\n\n1. Second\n1. Third\n\nA paragraph.\n\n5. New list\n- A bullet\n", encoding="utf-8")
            body = ParagraphStyle("test-body")
            paragraphs = build_book.chapter_flowables(source, 0, {"body": body, "list": body})
        lines = [item.getPlainText() for item in paragraphs if isinstance(item, Paragraph)]
        self.assertEqual(lines, ["1. First", "2. Second", "3. Third", "A paragraph.", "5. New list", "• A bullet"])

    def test_code_link_label_does_not_show_markdown_ticks(self) -> None:
        rendered = build_book.inline("[`repo@sha`](https://example.com/source)")
        self.assertIn("repo@sha", rendered)
        self.assertNotIn("`", rendered)

    def test_opening_height_keeps_early_figure_with_title(self) -> None:
        class FixedHeight(Flowable):
            def __init__(self, height: float):
                super().__init__()
                self.height = height

            def wrap(self, available_width: float, available_height: float) -> tuple[float, float]:
                return available_width, self.height

        figure = Image(str(build_book.ROOT / "figures/opencode-tool-state/preview.png"), width=100, height=420)
        opening = [FixedHeight(40), FixedHeight(55), figure, FixedHeight(20)]
        self.assertGreater(build_book.chapter_opening_height(opening), 105 * build_book.mm)
        self.assertEqual(build_book.chapter_opening_height(opening[:2]), 105 * build_book.mm)


if __name__ == "__main__":
    unittest.main()
