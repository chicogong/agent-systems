"""Build a printable, linked PDF from the curated Markdown book manifest.

The Markdown files remain the source of truth. This renderer intentionally
supports the small Markdown subset used by the guide; unsupported blocks fail
visibly in the output instead of silently changing the source documents.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import html
import re
import subprocess
from pathlib import Path
from urllib.parse import quote, urlparse

from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics import renderPDF
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics.shapes import Drawing
from reportlab.platypus import (
    BaseDocTemplate,
    CondPageBreak,
    Flowable,
    Frame,
    Image,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.platypus.tableofcontents import TableOfContents

from book_cover import cover_drawing


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "book" / "manifest.txt"
DEFAULT_OUTPUT = ROOT / "output" / "pdf" / "agent-systems-preview.pdf"
READER_URL = "https://books.aimake.cc/"
FRONT_COVER = ROOT / "book" / "assets" / "cover.svg"
DEFAULT_FONT = ROOT / "book" / ".cache" / "NotoSansSC-Regular.ttf"
FONT_NAME = "BookNoto"
BOLD_NAME = "BookNotoBold"
CODE_NAME = "BookCode"
INK = colors.HexColor("#1e3140")
MUTED = colors.HexColor("#55736a")
PAGE_W, PAGE_H = A4
MARGIN_X = 21 * mm
CONTENT_W = PAGE_W - MARGIN_X * 2


def styles(font_path: Path) -> dict[str, ParagraphStyle]:
    if not font_path.is_file():
        raise FileNotFoundError(f"Book font missing: {font_path}; run python3 scripts/fetch_book_font.py")
    bold_path = font_path.with_name("NotoSansSC-Bold.ttf")
    if not bold_path.is_file():
        raise FileNotFoundError(f"Book bold font missing: {bold_path}; run python3 scripts/fetch_book_font.py")
    mono_path = font_path.with_name("JetBrainsMono-Regular.ttf")
    if not mono_path.is_file():
        raise FileNotFoundError(f"Book code font missing: {mono_path}; run python3 scripts/fetch_book_font.py")
    pdfmetrics.registerFont(TTFont(FONT_NAME, str(font_path)))
    pdfmetrics.registerFont(TTFont(BOLD_NAME, str(bold_path)))
    pdfmetrics.registerFont(TTFont(CODE_NAME, str(mono_path)))
    pdfmetrics.registerFontFamily(FONT_NAME, normal=FONT_NAME, bold=BOLD_NAME, italic=FONT_NAME, boldItalic=BOLD_NAME)
    base = dict(fontName=FONT_NAME, textColor=INK, wordWrap="CJK")
    return {
        "title": ParagraphStyle("title", **base, fontSize=31, leading=45, alignment=TA_CENTER, spaceAfter=18),
        "subtitle": ParagraphStyle("subtitle", **(base | {"textColor": MUTED}), fontSize=13, leading=22, alignment=TA_CENTER),
        "h1": ParagraphStyle("h1", **(base | {"fontName": BOLD_NAME}), fontSize=18, leading=27, spaceBefore=0, spaceAfter=14, keepWithNext=True),
        "h1_compact": ParagraphStyle("h1_compact", **(base | {"fontName": BOLD_NAME}), fontSize=16, leading=25, spaceBefore=0, spaceAfter=14, keepWithNext=True),
        "h2": ParagraphStyle("h2", **(base | {"fontName": BOLD_NAME}), fontSize=14, leading=22, spaceBefore=15, spaceAfter=8, keepWithNext=True),
        "h3": ParagraphStyle("h3", **(base | {"fontName": BOLD_NAME}), fontSize=11.5, leading=18, spaceBefore=12, spaceAfter=6, keepWithNext=True),
        "body": ParagraphStyle("body", **base, fontSize=10, leading=18, spaceAfter=9),
        "list": ParagraphStyle("list", **base, fontSize=10, leading=18, leftIndent=15, firstLineIndent=-15, spaceAfter=7),
        "small": ParagraphStyle("small", **base, fontSize=8.8, leading=15, spaceAfter=6),
        "caption": ParagraphStyle("caption", **(base | {"textColor": MUTED}), fontSize=8.5, leading=14, alignment=TA_CENTER, spaceBefore=5, spaceAfter=14),
        "quote": ParagraphStyle("quote", **(base | {"textColor": MUTED}), fontSize=9, leading=16, leftIndent=12, rightIndent=8, spaceAfter=9),
        "toc": ParagraphStyle("toc", **base, fontSize=10, leading=17, leftIndent=12, firstLineIndent=-12, spaceBefore=5),
        "toc_chapter": ParagraphStyle("toc_chapter", **base, fontSize=9, leading=15, leftIndent=25, firstLineIndent=-12, spaceBefore=3),
        "part": ParagraphStyle("part", **(base | {"fontName": BOLD_NAME}), fontSize=28, leading=39),
        "code": ParagraphStyle("code", **(base | {"textColor": colors.HexColor("#314b66")}), fontSize=8.8, leading=16),
    }


TOKEN = re.compile(r"(\[[^\]]+\]\([^)]+\)|`[^`]+`|\*\*[^*]+\*\*)")
LINK = re.compile(r"^\[([^\]]+)\]\(([^)]+)\)$")
IMAGE = re.compile(r"^!\[([^\]]*)\]\(([^)]+)\)$")
HEADING = re.compile(r"^(#{1,3})\s+(.+)$")
LIST = re.compile(r"^\s*(?:(?P<bullet>[-*])|(?P<number>\d+)\.)\s+(?P<content>.+)$")
CHAPTER_KEYS: dict[Path, str] = {}
PUBLIC_LINKS = False
PUBLIC_ROUTES: dict[Path, str] = {}
FIGURE_OWNERS: dict[str, str] = {}
PUBLIC_SUPPLEMENTS = (
    "docs/concepts/README.md",
    "docs/systems/README.md",
    "docs/comparisons/README.md",
    "sources/README.md",
    "sources/jev.md",
    "sources/mcp-skill-tool-lifecycle.md",
    "sources/kimi-code.md",
    "sources/mimo-code.md",
)


def public_route(path: Path) -> str:
    relative = path.relative_to(ROOT).as_posix().removesuffix(".md")
    if relative.startswith("book/frontmatter/"):
        relative = relative.replace("book/frontmatter/", "front/", 1)
    elif relative.startswith("book/backmatter/"):
        relative = relative.replace("book/backmatter/", "back/", 1)
    elif relative.startswith("docs/"):
        relative = relative[5:]
    return "/" + relative.removesuffix("/README")


def public_link(target: Path, label: str, fragment: str) -> str:
    """Resolve only assets deliberately included in the public reader build."""
    relative = target.relative_to(ROOT).as_posix()
    url = PUBLIC_ROUTES.get(target)
    if target == ROOT / "README.md":
        url = "/"
    elif relative == "CONTRIBUTING.md":
        url = "/feedback"
        label = "反馈方式"
    elif relative == "LICENSE-CONTENT.md":
        url = "https://creativecommons.org/licenses/by/4.0/"
    elif relative == "LICENSE-CODE":
        url = "https://opensource.org/license/mit"
    elif re.fullmatch(r"figures/[^/]+/diagram\.svg", relative):
        slug = relative.split("/")[1]
        url = f"/assets/figures/{slug}/diagram.svg" if slug in FIGURE_OWNERS else None
    elif re.fullmatch(r"figures/[^/]+/README\.md", relative):
        slug = relative.split("/")[1]
        owner = FIGURE_OWNERS.get(slug)
        url = f"{owner}#图的文字说明-{slug}" if owner else None
    elif re.fullmatch(r"figures/[^/]+/(?:scene\.excalidraw|preview\.png)", relative):
        return ""
    if not url:
        return html.escape(label)
    if fragment and "#" not in url:
        url += "#" + quote(fragment, safe="-_")
    if url.startswith("/"):
        url = READER_URL.rstrip("/") + url
    return f'<link href="{html.escape(url, quote=True)}" color="#2563a6">{html.escape(label)}</link>'


def prepare_public_links(paths: list[Path]) -> None:
    PUBLIC_ROUTES.clear()
    FIGURE_OWNERS.clear()
    for path in (*paths, *(ROOT / name for name in PUBLIC_SUPPLEMENTS)):
        PUBLIC_ROUTES[path] = public_route(path)
    for path in (*paths, *(ROOT / name for name in PUBLIC_SUPPLEMENTS)):
        markdown = path.read_text(encoding="utf-8")
        for destination in re.findall(r"!\[[^\]]*\]\(([^)]+)\)", markdown):
            target = (path.parent / destination).resolve()
            if target.is_relative_to(ROOT) and re.fullmatch(r"figures/[^/]+/diagram\.svg", target.relative_to(ROOT).as_posix()):
                FIGURE_OWNERS.setdefault(target.parent.name, PUBLIC_ROUTES[path])


def code_markup(source: str, preserve_leading: bool = False) -> str:
    leading = len(source) - len(source.lstrip(" ")) if preserve_leading else 0
    source = source[leading:]
    parts = []
    for segment in re.split(r"([\x20-\x7e]+)", source):
        if segment and all(" " <= char <= "~" for char in segment):
            parts.append(f'<font name="{CODE_NAME}">{html.escape(segment)}</font>')
        else:
            parts.append(html.escape(segment))
    return "&#160;" * leading + "".join(parts)


def link_label_markup(label: str) -> str:
    if label.startswith("`") and label.endswith("`") and label.count("`") == 2:
        return f'<font name="{CODE_NAME}">{html.escape(label[1:-1])}</font>'
    return html.escape(label)


def inline(source: str, current_path: Path | None = None) -> str:
    result: list[str] = []
    for part in TOKEN.split(source):
        match = LINK.match(part)
        if match:
            label, href = match.groups()
            if urlparse(href).scheme in {"https", "http"}:
                result.append(f'<link href="{html.escape(href, quote=True)}" color="#2563a6">{link_label_markup(label)}</link>')
            elif current_path is not None:
                local_path, _, fragment = href.partition("#")
                target = (current_path.parent / local_path).resolve()
                if target in CHAPTER_KEYS:
                    result.append(f'<link href="#{CHAPTER_KEYS[target]}" color="#2563a6">{link_label_markup(label)}</link>')
                elif PUBLIC_LINKS and target.is_relative_to(ROOT):
                    result.append(public_link(target, label, fragment))
                elif target.is_relative_to(ROOT) and target.exists():
                    public_path = quote(target.relative_to(ROOT).as_posix(), safe="/")
                    public_url = f"https://github.com/chicogong/agent-systems/blob/main/{public_path}"
                    if fragment:
                        public_url += f"#{quote(fragment, safe='-')}"
                    result.append(f'<link href="{html.escape(public_url, quote=True)}" color="#2563a6">{link_label_markup(label)}</link>')
                else:
                    result.append(html.escape(label))
            else:
                result.append(html.escape(label))
        elif part.startswith("`") and part.endswith("`"):
            result.append(f'<font color="#6b40a0">{code_markup(part[1:-1])}</font>')
        elif part.startswith("**") and part.endswith("**"):
            result.append(f"<b>{html.escape(part[2:-2])}</b>")
        else:
            result.append(html.escape(part))
    return "".join(result)


def manifest_entries() -> list[tuple[str, str | Path]]:
    entries: list[tuple[str, str | Path]] = []
    paths: set[Path] = set()
    for raw in MANIFEST.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("@part "):
            entries.append(("part", line[6:]))
            continue
        kind = "chapter"
        if line.startswith("@front "):
            kind, line = "front", line[7:]
        elif line.startswith("@back "):
            kind, line = "back", line[6:]
        path = (ROOT / line).resolve()
        if not path.is_relative_to(ROOT) or not path.is_file() or path.suffix != ".md":
            raise ValueError(f"Invalid book chapter: {line}")
        if path in paths:
            raise ValueError(f"Duplicate book chapter: {line}")
        paths.add(path)
        entries.append((kind, path))
    if not paths or not any(kind == "part" for kind, _ in entries):
        raise ValueError("Book manifest is empty")
    order = [kind for kind, _ in entries]
    if order != sorted(order, key={"front": 0, "part": 1, "chapter": 1, "back": 2}.get):
        raise ValueError("Book manifest must order frontmatter, parts, chapters, then backmatter")
    return entries


def manifest_paths() -> list[Path]:
    return [entry for kind, entry in manifest_entries() if kind in {"front", "chapter", "back"}]


class Part(Paragraph):
    def __init__(self, text: str, style: ParagraphStyle, key: str):
        super().__init__(html.escape(text), style)
        self.part_title = text
        self.part_key = key


class Chapter(Paragraph):
    def __init__(self, text: str, style: ParagraphStyle, key: str, outline_level: int = 1):
        super().__init__(html.escape(text), style)
        self.chapter_title = text
        self.chapter_key = key
        self.outline_level = outline_level


class BookDoc(BaseDocTemplate):
    def __init__(self, filename: str, public_links: bool = False):
        self.public_links = public_links
        super().__init__(
            filename,
            pagesize=A4,
            leftMargin=MARGIN_X,
            rightMargin=MARGIN_X,
            topMargin=21 * mm,
            bottomMargin=20 * mm,
            title="图解 Agent 系统 · 在线阅读预览" if public_links else "图解 Agent 系统 · 源码阅读预览",
            author="Chicogong",
            pageCompression=1,
        )
        frame = Frame(MARGIN_X, 19 * mm, CONTENT_W, PAGE_H - 39 * mm, leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
        self.addPageTemplates([
            PageTemplate(id="book", frames=[frame], onPage=self.decorate),
            PageTemplate(id="back", frames=[frame], onPage=self.back_cover),
        ])

    def back_cover(self, canvas, doc):
        canvas.saveState()
        canvas.setFillColor(colors.HexColor("#faf9f4"))
        canvas.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
        green = colors.HexColor("#174a3d")
        dark = colors.HexColor("#1e3140")
        canvas.setFillColor(green)
        canvas.setFont(BOLD_NAME, 31)
        canvas.drawString(22 * mm, 255 * mm, "不止会用，")
        canvas.drawString(22 * mm, 239 * mm, "更要看懂。")
        canvas.setStrokeColor(green)
        canvas.setLineWidth(3)
        canvas.line(22 * mm, 228 * mm, 40 * mm, 228 * mm)
        canvas.setFillColor(dark)
        canvas.setFont(FONT_NAME, 12)
        for offset, line in enumerate((
            "从运行循环到工具、上下文、记忆与权限，",
            "用清晰的图解建立机制，用固定版本的源码核对实现。",
            "每章标明证据边界，提供清晰图稿与文字说明。" if self.public_links else "每章标明证据边界，保留可编辑图源与文字说明。",
        )):
            canvas.drawString(22 * mm, (211 - 10 * offset) * mm, line)
        canvas.setFont(BOLD_NAME, 13)
        for offset, (title, detail) in enumerate((
            ("理解机制", "把抽象概念拆成可追问的运行路径"),
            ("对照源码", "沿固定版本核查入口、状态与副作用"),
            ("持续修订", "让图文随着证据和项目变化而更新"),
        )):
            y = (162 - offset * 27) * mm
            canvas.setFillColor(green)
            canvas.circle(24 * mm, y + 1.5 * mm, 2.2 * mm, fill=1, stroke=0)
            canvas.drawString(32 * mm, y, title)
            canvas.setFillColor(dark)
            canvas.setFont(FONT_NAME, 10)
            canvas.drawString(32 * mm, y - 6 * mm, detail)
            canvas.setFont(BOLD_NAME, 13)
        wave = canvas.beginPath()
        wave.moveTo(0, 53 * mm)
        wave.curveTo(46 * mm, 70 * mm, 103 * mm, 44 * mm, PAGE_W, 63 * mm)
        wave.lineTo(PAGE_W, 49 * mm)
        wave.lineTo(0, 49 * mm)
        wave.close()
        canvas.setFillColor(colors.HexColor("#e1eee7"))
        canvas.drawPath(wave, stroke=0, fill=1)
        canvas.setFillColor(green)
        canvas.rect(0, 0, PAGE_W, 49 * mm, fill=1, stroke=0)
        canvas.setFillColor(colors.white)
        canvas.setFont(BOLD_NAME, 12)
        canvas.drawString(22 * mm, 31 * mm, "图解 Agent 系统")
        canvas.setFont(FONT_NAME, 9)
        canvas.drawString(22 * mm, 21 * mm, "开放书稿 · 原创图文 CC BY 4.0 · 构建脚本 MIT")
        canvas.drawString(22 * mm, 12 * mm, "books.aimake.cc")
        qr = QrCodeWidget(READER_URL)
        qr_w = qr.getBounds()[2]
        qr_size = 31 * mm
        qr_x, qr_y = PAGE_W - 47 * mm, 9 * mm
        canvas.setFillColor(colors.white)
        canvas.roundRect(qr_x - 2 * mm, qr_y - 2 * mm, qr_size + 4 * mm,
                         qr_size + 4 * mm, 2 * mm, fill=1, stroke=0)
        qr_drawing = Drawing(qr_size, qr_size, transform=[qr_size / qr_w, 0, 0, qr_size / qr_w, 0, 0])
        qr_drawing.add(qr)
        renderPDF.draw(qr_drawing, canvas, qr_x, qr_y)
        canvas.linkURL(READER_URL, (22 * mm, 10 * mm, 138 * mm, 19 * mm), relative=0)
        canvas.restoreState()

    def decorate(self, canvas, doc):
        canvas.saveState()
        if doc.page == 1:
            renderPDF.draw(cover_drawing(), canvas, 0, 0)
            canvas.restoreState()
            return
        canvas.setStrokeColor(colors.HexColor("#d8e2ec"))
        canvas.line(MARGIN_X, 17 * mm, PAGE_W - MARGIN_X, 17 * mm)
        canvas.setFont(FONT_NAME, 8)
        canvas.setFillColor(MUTED)
        canvas.drawString(MARGIN_X, 12 * mm, "图解 Agent 系统 · 在线阅读预览" if self.public_links else "图解 Agent 系统 · 固定源码阅读预览")
        canvas.drawRightString(PAGE_W - MARGIN_X, 12 * mm, str(doc.page))
        canvas.restoreState()

    def afterFlowable(self, flowable: Flowable):
        if isinstance(flowable, Part):
            self.canv.bookmarkPage(flowable.part_key)
            self.canv.addOutlineEntry(flowable.part_title, flowable.part_key, level=0)
            self.notify("TOCEntry", (0, flowable.part_title, self.page, flowable.part_key))
        elif isinstance(flowable, Chapter):
            self.canv.bookmarkPage(flowable.chapter_key)
            self.canv.addOutlineEntry(flowable.chapter_title, flowable.chapter_key, level=flowable.outline_level)
            self.notify("TOCEntry", (flowable.outline_level, flowable.chapter_title, self.page, flowable.chapter_key))


def figure(path: Path, alt: str, style: dict[str, ParagraphStyle]) -> list[Flowable]:
    if path.suffix == ".svg":
        path = path.with_name("preview.png")
    if not path.is_file():
        raise FileNotFoundError(f"Book figure missing: {path}")
    with PILImage.open(path) as bitmap:
        width, height = bitmap.size
    scale = min(CONTENT_W / width, 168 * mm / height)
    effective_ppi = 72 / scale
    if effective_ppi < 300:
        raise ValueError(f"Figure below 300 PPI at book size: {path} ({effective_ppi:.0f} PPI)")
    drawing = Image(str(path), width=width * scale, height=height * scale)
    drawing.hAlign = "CENTER"
    drawing.spaceBefore = 5
    return [drawing, Paragraph(html.escape(alt), style["caption"])]


def table_rows(lines: list[str], style: dict[str, ParagraphStyle], current_path: Path) -> list[Flowable]:
    rows = [[cell.strip() for cell in line.strip().strip("|").split("|")] for line in lines]
    if len(rows) < 3:
        return [Paragraph(inline(" ".join(lines), current_path), style["body"])]
    headers = rows[0]
    rendered: list[Flowable] = []
    for values in rows[2:]:
        details = []
        for name, value in zip(headers, values):
            details.append(f"<b>{inline(name, current_path)}：</b>{inline(value, current_path)}")
        p = Paragraph("<br/>".join(details), style["small"])
        box = Table([[p]], colWidths=[CONTENT_W], hAlign="LEFT")
        box.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f5f8fc")),
            ("LINEBELOW", (0, 0), (-1, -1), 0.35, colors.HexColor("#dce6f0")),
            ("LEFTPADDING", (0, 0), (-1, -1), 9),
            ("RIGHTPADDING", (0, 0), (-1, -1), 9),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        rendered.extend([box, Spacer(1, 5)])
    return rendered


def chapter_flowables(path: Path, index: int, style: dict[str, ParagraphStyle], outline_level: int = 1) -> list[Flowable]:
    lines = path.read_text(encoding="utf-8").splitlines()
    result: list[Flowable] = []
    paragraph: list[str] = []
    list_kind: str | None = None
    list_counter = 0

    def flush():
        if paragraph:
            result.append(Paragraph(inline(" ".join(paragraph), path), style["body"]))
            paragraph.clear()

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if PUBLIC_LINKS:
            line = re.sub(r"\[[^\]]+\]\([^)]*/figures/[^/]+/(?:scene\.excalidraw|preview\.png)\)", "", line)
            line = re.sub(r"^(?:\s*·\s*)+|(?:\s*·\s*)+$", "", line).strip()
            line = re.sub(r"(?:\s*·\s*){2,}", " · ", line)
        if line.startswith("[返回") or line.startswith("[图源]("):
            flush()
            list_kind = None
            i += 1
            continue
        if not line:
            flush()
            i += 1
            continue
        heading = HEADING.match(line)
        image = IMAGE.match(line)
        listing = LIST.match(line)
        if not listing:
            list_kind = None
        if heading:
            flush()
            level, title = heading.groups()
            if level == "#":
                heading_style = style["h1_compact"] if len(title) >= 40 else style["h1"]
                result.append(Chapter(title, heading_style, f"chapter-{index}", outline_level))
            else:
                result.append(Paragraph(inline(title, path), style["h2" if level == "##" else "h3"]))
        elif image:
            flush()
            alt, destination = image.groups()
            result.extend(figure((path.parent / destination).resolve(), alt, style))
        elif line.startswith("|"):
            flush()
            block = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                block.append(lines[i])
                i += 1
            result.extend(table_rows(block, style, path))
            continue
        elif line.startswith("```"):
            flush()
            i += 1
            code_lines = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code_lines.append(Paragraph(code_markup(lines[i], preserve_leading=True) or "&#160;", style["code"]))
                i += 1
            if code_lines:
                block = Table([[code_lines]], colWidths=[CONTENT_W], hAlign="LEFT")
                block.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f2f6fb")),
                    ("LINEBEFORE", (0, 0), (0, -1), 2, colors.HexColor("#5b8ec3")),
                    ("LEFTPADDING", (0, 0), (-1, -1), 10),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                    ("TOPPADDING", (0, 0), (-1, -1), 7),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                ]))
                result.extend([block, Spacer(1, 6)])
        elif line.startswith(">"):
            flush()
            result.append(Paragraph(inline(line.lstrip("> "), path), style["quote"]))
        elif listing:
            flush()
            kind = "ordered" if listing.group("number") else "bullet"
            if kind == "ordered":
                if list_kind != kind:
                    list_counter = int(listing.group("number"))
                else:
                    list_counter += 1
                marker = f"{list_counter}."
            else:
                marker = "•"
            list_kind = kind
            result.append(Paragraph(marker + " " + inline(listing.group("content"), path), style["list"]))
        elif line.startswith("---"):
            flush()
        else:
            paragraph.append(line)
        i += 1
    flush()
    return result


def chapter_opening_height(flowables: list[Flowable]) -> float:
    """Keep a near-opening main figure with the title and scope paragraph."""
    first_image = next((i for i, item in enumerate(flowables[:4]) if isinstance(item, Image)), None)
    if first_image is None:
        return 105 * mm
    opening = flowables[: first_image + 2]  # Include the figure caption.
    height = sum(
        item.getSpaceBefore() + item.wrap(CONTENT_W, PAGE_H)[1] + item.getSpaceAfter()
        for item in opening
    )
    return min(max(height + 5 * mm, 105 * mm), 240 * mm)


def book_identity() -> tuple[str, bool, str]:
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()
    dirty = bool(subprocess.run(["git", "status", "--porcelain"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip())
    built_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d UTC")
    return commit, dirty, built_utc


def build(output: Path, font_path: Path, public_links: bool = False) -> None:
    global PUBLIC_LINKS
    PUBLIC_LINKS = public_links
    output.parent.mkdir(parents=True, exist_ok=True)
    style = styles(font_path)
    entries = manifest_entries()
    paths = manifest_paths()
    CHAPTER_KEYS.clear()
    CHAPTER_KEYS.update({path: f"chapter-{i}" for i, path in enumerate(paths)})
    if public_links:
        prepare_public_links(paths)
    commit, dirty, built_utc = book_identity()
    commit_url = f"https://github.com/chicogong/agent-systems/commit/{commit}"
    version_note = "含未提交修改，仅供本地校稿；不是该提交的原样产物。" if dirty else "从该提交的干净工作树构建。"
    story: list[Flowable] = [
        Spacer(1, 1),
        PageBreak(),
        Spacer(1, 57 * mm),
        Paragraph("图解 Agent 系统", style["title"]),
        Paragraph("从运行机制到开源实现", style["subtitle"]),
        Spacer(1, 58 * mm),
        Paragraph("chicogong 著", style["subtitle"]),
        PageBreak(),
        Paragraph("关于本版", style["h1"]),
        Paragraph(f'公开预览 · 书稿提交：<link href="{commit_url}" color="#2563a6">{commit[:12]}</link> · 构建日期：{built_utc}。{version_note}', style["body"]),
        Paragraph('勘误与阅读反馈：<link href="https://books.aimake.cc/feedback" color="#2563a6">books.aimake.cc/feedback</link>。固定版本的 PDF 应与发布清单中的完整提交和 SHA-256 一起保存；本站 PDF 阅读页是可替换的最新电子校样入口。', style["body"]),
        Paragraph("本书的项目结论对应各章注明的固定源码版本。除非单独说明，它们是静态代码阅读，不是运行评测或产品安全认证。", style["body"]),
        Paragraph('原创文字与图：<link href="https://creativecommons.org/licenses/by/4.0/legalcode" color="#2563a6">CC BY 4.0</link>。构建脚本：<link href="https://opensource.org/license/mit" color="#2563a6">MIT</link>。正文 <link href="https://github.com/google/fonts/blob/e44c4b011a820c2cbe2fd2cfa8052037d7edb571/ofl/notosanssc/OFL.txt" color="#2563a6">Noto Sans SC</link>、代码 <link href="https://github.com/google/fonts/blob/e44c4b011a820c2cbe2fd2cfa8052037d7edb571/ofl/jetbrainsmono/OFL.txt" color="#2563a6">JetBrains Mono</link> 均依 SIL OFL 1.1 授权。上游项目与其商标、代码遵守各自许可；链接不表示对本书的认可。', style["body"]),
        Paragraph("正文以 Markdown 为准；PDF 由书稿清单自动生成。章节有意保留研究范围、未覆盖情况和可点击的固定源码链接。" + ("本公共阅读版的内部参考链接优先指向在线章节和已发布的图稿；可编辑图源可从公开源码仓查看。" if public_links else ""), style["body"]),
        PageBreak(),
    ]
    chapter_index = 0
    for kind, value in entries:
        if kind != "front":
            continue
        story.extend(chapter_flowables(value, chapter_index, style, outline_level=0))
        story.append(PageBreak())
        chapter_index += 1
    story.append(Paragraph("目录", style["h1"]))
    toc = TableOfContents()
    toc.levelStyles = [style["toc"], style["toc_chapter"]]
    story.extend([toc, PageBreak()])
    part_index = 0
    first_chapter_in_part = True
    for kind, value in entries:
        if kind == "part":
            if part_index:
                story.append(PageBreak())
            story.extend([
                Spacer(1, 51 * mm),
                Part(str(value), style["part"], f"part-{part_index}"),
                Spacer(1, 5 * mm),
                Paragraph("固定版本的源码阅读 · 图文相互校验", style["subtitle"]),
                PageBreak(),
            ])
            part_index += 1
            first_chapter_in_part = True
        elif kind == "chapter":
            chapter = chapter_flowables(value, chapter_index, style)
            if not first_chapter_in_part:
                story.append(CondPageBreak(chapter_opening_height(chapter)))
            story.extend(chapter)
            first_chapter_in_part = False
            chapter_index += 1
    for kind, value in entries:
        if kind != "back":
            continue
        story.append(CondPageBreak(70 * mm))
        story.extend(chapter_flowables(value, chapter_index, style, outline_level=0))
        chapter_index += 1
    story.extend([NextPageTemplate("back"), PageBreak(), Spacer(1, 1)])
    BookDoc(str(output), public_links=public_links).multiBuild(story)
    print(f"Built {output} from {len(paths)} Markdown chapters ({'public' if public_links else 'private'} links)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--font", type=Path, default=DEFAULT_FONT)
    parser.add_argument("--public-links", action="store_true", help="link only to the public reader, included figures, and external sources")
    args = parser.parse_args()
    build(args.output.resolve(), args.font.resolve(), public_links=args.public_links)
