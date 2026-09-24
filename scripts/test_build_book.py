"""Public PDF links must resolve without access to the private authoring repo."""

from __future__ import annotations

import unittest

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


if __name__ == "__main__":
    unittest.main()
