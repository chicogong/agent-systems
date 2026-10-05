"""Book layout and public links are checked without building the whole PDF."""

from __future__ import annotations

import unittest
from io import BytesIO
from unittest.mock import patch
from tempfile import TemporaryDirectory
from pathlib import Path

from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Flowable, Image, Paragraph, SimpleDocTemplate
from pypdf import PdfReader

import build_book
from book_typography import BookParagraph, NO_LINE_END, NO_LINE_START
from check_book_pdf import matches_clean_provenance


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

    def test_public_link_with_mixed_code_label_keeps_formatting(self) -> None:
        build_book.prepare_public_links(build_book.manifest_paths())
        target = build_book.ROOT / "docs/systems/pi/code-walkthrough.md"
        rendered = build_book.public_link(target, "`steer()` 源码", "")
        self.assertIn('href="https://books.aimake.cc/systems/pi/code-walkthrough"', rendered)
        self.assertIn('name="BookCode"', rendered)
        self.assertNotIn("`", rendered)
        self.assertIn("源码", rendered)

    def test_emphasis_renders_code_without_markdown_delimiters(self) -> None:
        rendered = build_book.inline("**提出 `check()`，不等于验收。**")
        self.assertTrue(rendered.startswith("<b>"))
        self.assertIn('name="BookCode"', rendered)
        self.assertNotIn("`", rendered)
        self.assertNotIn("**", rendered)

    def test_italic_markup_does_not_leak_or_change_code(self) -> None:
        rendered = build_book.inline("此处的*默认实现*与 `test_*.py` 不同。")
        self.assertIn("<i>默认实现</i>", rendered)
        self.assertIn("test_*.py", rendered)

    def test_chapter_and_contents_title_have_no_markdown_ticks(self) -> None:
        # No font downloads in this parser-only test; production build registers
        # BookCode before creating chapters.
        with patch.object(build_book, "CODE_NAME", "Courier"):
            chapter = build_book.Chapter("读 `exec_command` 的控制流", ParagraphStyle("test-title"), "test-chapter")
        self.assertEqual(chapter.getPlainText(), "读 exec_command 的控制流")
        self.assertEqual(chapter.chapter_title, "读 exec_command 的控制流")

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


class BookProvenanceTests(unittest.TestCase):
    def test_public_pdf_requires_matching_clean_source(self) -> None:
        commit = "a" * 40
        clean = "书稿提交：aaaaaaaaaaaa · 构建日期：2026-10-04。\n从该提交的干净工作树构建。"
        dirty = clean.replace("从该提交的干净工作树构建", "含未提交修改，仅供本地校稿")
        self.assertTrue(matches_clean_provenance(clean, commit))
        self.assertFalse(matches_clean_provenance(dirty, commit))
        self.assertFalse(matches_clean_provenance(clean, "b" * 40))
        with self.assertRaisesRegex(ValueError, "full Git SHA-1"):
            matches_clean_provenance(clean, "short")


class BookChineseTypographyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        # Built-in CID metrics make these tests offline and independent of the
        # optional downloaded book fonts (CI runs tests before fetching fonts).
        pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))

    def setUp(self) -> None:
        self.style = ParagraphStyle(
            "typography-test", fontName="STSong-Light", fontSize=10,
            leading=16, wordWrap="CJK", allowOrphans=True,
        )

    def lines(self, paragraph: Paragraph) -> list[str]:
        if paragraph.blPara.kind == 0:
            return ["".join(words) for _, words in paragraph.blPara.lines]
        return ["".join(fragment.text for fragment in line.words) for line in paragraph.blPara.lines]

    def assert_safe_lines(self, paragraph: BookParagraph) -> None:
        for text, line in zip(self.lines(paragraph), paragraph.blPara.lines):
            visible = text.strip()
            if visible:
                self.assertNotIn(visible[0], NO_LINE_START, repr(text))
                if not line.lineBreak:
                    self.assertNotIn(visible[-1], NO_LINE_END, repr(text))
            self.assertGreaterEqual(line.extraSpace, -1e-7)
            self.assertLessEqual(line.currentWidth, line.maxWidth + 1e-7)

    def test_closing_parenthesis_and_full_stop_are_not_orphaned(self) -> None:
        paragraph = BookParagraph("理解（运行循环）。", self.style)
        paragraph.wrap(70, 1000)
        self.assertEqual(self.lines(paragraph), ["理解（运行循", "环）。"])
        self.assert_safe_lines(paragraph)

    def test_chinese_comma_and_quotes_move_with_previous_character(self) -> None:
        for text in ("一二三四五，六七。", "中文逗号，句号。引号”右括号）", "读懂《图解》，“再试一次”。"):
            with self.subTest(text=text):
                paragraph = BookParagraph(text, self.style)
                paragraph.wrap(50, 1000)
                self.assert_safe_lines(paragraph)
                self.assertEqual("".join(self.lines(paragraph)), paragraph.getPlainText())

    def test_many_widths_preserve_text_and_never_overflow(self) -> None:
        markup = '先读这张图，再理解<b>循环</b>（模型、工具和结果）。<font name="Courier">run()</font> 完成后，核对“引用”；遇到问题时，再观察。'
        for width in (40, 45, 50, 60, 73, 85, 110, 160, 476):
            with self.subTest(width=width):
                paragraph = BookParagraph(markup, self.style)
                paragraph.wrap(width, 1000)
                self.assert_safe_lines(paragraph)
                self.assertEqual("".join(self.lines(paragraph)), paragraph.getPlainText())

    def test_opening_bracket_and_latin_word_breaks(self) -> None:
        paragraph = BookParagraph("一二三四（运行循环）和 <font name=\"Courier\">AgentSession</font> 交回结果。", self.style)
        paragraph.wrap(90, 1000)
        self.assert_safe_lines(paragraph)
        self.assertTrue(any("AgentSession" in line for line in self.lines(paragraph)))
        self.assertEqual("".join(self.lines(paragraph)), paragraph.getPlainText())
        # A genuinely overlong source path can still wrap; no forced overflow.
        long_word = BookParagraph('<font name="Courier">very_long_source_path_identifier</font>，结束。', self.style)
        long_word.wrap(60, 1000)
        self.assert_safe_lines(long_word)

    def test_spaces_at_span_boundaries_do_not_hide_punctuation(self) -> None:
        for text in ("一二三四 ，下一句。", "一二三四（ 下一句）。", '一二三四<font name="Courier"> </font>，下一句。'):
            with self.subTest(text=text):
                paragraph = BookParagraph(text, self.style)
                paragraph.wrap(50, 1000)
                self.assert_safe_lines(paragraph)
                self.assertEqual("".join(self.lines(paragraph)), paragraph.getPlainText())

    def test_combining_mark_and_nonbreaking_space_are_not_separated(self) -> None:
        paragraph = BookParagraph('一二<font name="Helvetica">e\u0301 A\u00a0B</font>，再看结果。', self.style)
        paragraph.wrap(40, 1000)
        self.assert_safe_lines(paragraph)
        lines = self.lines(paragraph)
        self.assertTrue(any("e\u0301" in line for line in lines))
        self.assertTrue(any("A\u00a0B" in line for line in lines))
        self.assertEqual("".join(lines), paragraph.getPlainText())

    def test_explicit_breaks_and_named_anchor_survive(self) -> None:
        paragraph = BookParagraph('<a name="chapter-test"/>第一行。<br/>第二行，接着读。', self.style)
        paragraph.wrap(60, 1000)
        self.assert_safe_lines(paragraph)
        self.assertTrue(paragraph.blPara.lines[0].lineBreak)
        self.assertEqual("".join(self.lines(paragraph)), "第一行。第二行，接着读。")
        callbacks = [fragment.cbDefn for line in paragraph.blPara.lines for fragment in line.words if hasattr(fragment, "cbDefn")]
        self.assertTrue(any(getattr(callback, "name", "") == "chapter-test" for callback in callbacks))

    def test_link_and_mixed_fonts_survive_punctuation_wrap_and_drawing(self) -> None:
        paragraph = BookParagraph('先看<link href="https://example.com/source" color="#2563a6"><font name="Courier">run()</font> 的出处</link>，再核对结果。', self.style)
        paragraph.wrap(65, 1000)
        self.assert_safe_lines(paragraph)
        self.assertEqual("".join(self.lines(paragraph)), paragraph.getPlainText())
        fonts = {fragment.fontName for line in paragraph.blPara.lines for fragment in line.words}
        self.assertEqual(fonts, {"STSong-Light", "Courier"})
        linked = [fragment for line in paragraph.blPara.lines for fragment in line.words if fragment.link]
        self.assertEqual("".join(fragment.text for fragment in linked), "run() 的出处")
        output = BytesIO()
        page = canvas.Canvas(output)
        paragraph.drawOn(page, 50, 500)
        page.save()
        reader = PdfReader(output)
        urls = [annotation.get_object()["/A"]["/URI"] for annotation in reader.pages[0]["/Annots"]]
        self.assertTrue(urls)
        self.assertEqual(set(urls), {"https://example.com/source"})

    def test_page_split_does_not_insert_spaces_or_lose_links(self) -> None:
        markup = ('先看<link href="https://example.com/source">模型交回结果</link>，再核对引用（位置与原文）。' * 8)
        paragraph = BookParagraph(markup, self.style)
        paragraph.wrap(85, 1000)
        expected = paragraph.getPlainText()
        first, rest = paragraph.split(85, 4 * self.style.leading)
        first.wrap(85, 1000)
        rest.wrap(85, 1000)
        self.assert_safe_lines(first)
        self.assert_safe_lines(rest)
        actual = "".join(self.lines(first) + self.lines(rest))
        self.assertEqual(actual, expected)
        linked = [fragment for part in (first, rest) for line in part.blPara.lines for fragment in line.words if fragment.link]
        self.assertEqual("".join(fragment.text for fragment in linked), "模型交回结果" * 8)

    def test_two_page_pdf_preserves_external_links_and_named_anchor_destination(self) -> None:
        markup = '<a name="chapter-test"/>' + (
            '先看<link href="https://example.com/source">模型交回结果</link>，再核对引用（位置与原文）。' * 9
        ) + '返回<link href="#chapter-test">章节起点</link>。'
        output = BytesIO()
        # Let the document engine split one paragraph naturally, instead of
        # manually drawing two parts or only checking fragment.link metadata.
        SimpleDocTemplate(
            output, pagesize=(200, 200), leftMargin=20, rightMargin=20,
            topMargin=20, bottomMargin=20,
        ).build([BookParagraph(markup, self.style)])
        reader = PdfReader(output)
        self.assertEqual(len(reader.pages), 2)
        page_annotations = [
            [reference.get_object() for reference in page.get("/Annots", [])]
            for page in reader.pages
        ]
        for page_index, annotations in enumerate(page_annotations):
            with self.subTest(page=page_index + 1):
                urls = [
                    annotation["/A"]["/URI"] for annotation in annotations
                    if annotation.get("/A", {}).get("/S") == "/URI"
                ]
                self.assertTrue(urls, "Each page must have a real external link annotation")
                self.assertEqual(set(urls), {"https://example.com/source"})
        destinations = [annotation["/Dest"] for annotation in page_annotations[1] if "/Dest" in annotation]
        self.assertEqual(len(destinations), 1)
        destination = destinations[0]
        self.assertEqual(destination[0], reader.pages[0].indirect_reference)
        self.assertEqual(destination[0].get_object()["/Type"], "/Page")
        self.assertEqual(destination[1], "/XYZ")
        # The named anchor still resolves to an actual position on page one.
        self.assertTrue(0 <= destination[2] <= 200)
        self.assertTrue(0 <= destination[3] <= 200)

    def test_first_line_and_later_widths_respect_list_indentation(self) -> None:
        style = ParagraphStyle("indented", parent=self.style, leftIndent=15, firstLineIndent=-15, rightIndent=5)
        paragraph = BookParagraph("1. 先读清楚这张图，再理解（运行循环）。然后核对结果。", style)
        paragraph.wrap(90, 1000)
        self.assertEqual(paragraph.blPara.lines[0].maxWidth, 85)
        self.assertTrue(all(line.maxWidth == 70 for line in paragraph.blPara.lines[1:]))
        self.assert_safe_lines(paragraph)

    def test_table_cells_use_prose_wrapper_but_code_blocks_keep_native_wrapper(self) -> None:
        table = build_book.table_rows(["| 内容 |", "| --- |", "| 理解（运行循环）。 |"], {"small": self.style}, build_book.ROOT / "reading-guide.md")[0]
        paragraph = table._cellvalues[0][0]
        self.assertIsInstance(paragraph, BookParagraph)
        paragraph.wrap(70, 1000)
        self.assert_safe_lines(paragraph)
        with TemporaryDirectory() as directory:
            source = Path(directory) / "code.md"
            source.write_text("```python\n  call(), [x]\n```\n", encoding="utf-8")
            with patch.object(build_book, "CODE_NAME", "Courier"):
                block = build_book.chapter_flowables(source, 0, {"code": self.style})[0]
        code = block._cellvalues[0][0][0]
        self.assertIsInstance(code, Paragraph)
        self.assertNotIsInstance(code, BookParagraph)
        self.assertEqual(code.getPlainText(), "\u00a0\u00a0call(), [x]")

    def test_impossible_narrow_line_fails_without_overflow(self) -> None:
        with self.assertRaisesRegex(ValueError, "cannot fit a Chinese punctuation group"):
            BookParagraph("字）。", self.style).wrap(20, 1000)

    def test_non_cjk_paragraph_keeps_reportlab_layout(self) -> None:
        style = ParagraphStyle("western", fontName="Helvetica", fontSize=10)
        native, local = Paragraph("A short English paragraph with spaces.", style), BookParagraph("A short English paragraph with spaces.", style)
        self.assertEqual(native.wrap(70, 1000), local.wrap(70, 1000))
        self.assertEqual(self.lines(native), self.lines(local))


if __name__ == "__main__":
    unittest.main()
