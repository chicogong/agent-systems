"""Faithful mixed-media cover: original illustration, editorial vector type.

The generated illustration remains a bitmap. Do not describe this as a fully
vectorized or 300 PPI print master. The SVG and PDF use this same composition.
"""

from __future__ import annotations

import html
from pathlib import Path
import re

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont as FontToolsFont
from reportlab.graphics import renderSVG
from reportlab.graphics.shapes import Drawing, Image, Line, Rect, String
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4


ROOT = Path(__file__).resolve().parents[1]
ORIGINAL = ROOT / "book" / "assets" / "cover-selected.png"
PAGE_W, PAGE_H = A4
PAPER = colors.HexColor("#fbfbf3")
INK = colors.HexColor("#192e39")
GREEN = colors.HexColor("#174a3d")
PALE = colors.HexColor("#d5e8de")


def text(d: Drawing, x: float, y: float, value: str, size: float,
         *, color=INK, font="BookNoto") -> None:
    d.add(String(x, y, value, fontName=font, fontSize=size, fillColor=color))


def cover_drawing() -> Drawing:
    """Retain the selected image's composition while typesetting editorial copy."""
    d = Drawing(PAGE_W, PAGE_H)
    d.add(Rect(0, 0, PAGE_W, PAGE_H, fillColor=PAPER, strokeColor=None))
    image_w = PAGE_H * 2 / 3
    d.add(Image((PAGE_W - image_w) / 2, 0, image_w, PAGE_H, str(ORIGINAL)))

    # Opaque paper panels replace the generated type in its original positions.
    # The art, right-hand module index and four-layer silhouette remain intact.
    d.add(Rect(36, 517, 360, 308, fillColor=PAPER, strokeColor=None))
    text(d, 47, 763, "图解", 51, color=GREEN, font="BookNotoBold")
    text(d, 45, 673, "Agent", 87, font="BookNotoBold")
    text(d, 48, 579, "系统", 79, font="BookNotoBold")
    text(d, 49, 543, "从运行机制到开源实现", 22,
         color=GREEN, font="BookNotoBold")
    d.add(Rect(49, 519, 43, 4, rx=2, ry=2, fillColor=GREEN, strokeColor=None))

    # Replace only the text regions that need reliable vector reproduction.
    d.add(Rect(39, 326, 135, 187, fillColor=PAPER, strokeColor=None))
    for i, line in enumerate(("拆开系统", "看懂原理", "对照代码", "动手实践")):
        text(d, 49, 486 - i * 29, line, 14.2)
    text(d, 49, 347, "chicogong  著", 13.8)

    # Re-typeset the imprint. The illustration itself remains the user's
    # selected image; no extra pseudo-technical shapes are invented here.
    d.add(Rect(0, 0, PAGE_W, 156, fillColor=GREEN, strokeColor=None))
    text(d, 40, 102, "理解 Agent 的现在", 15,
         color=colors.white, font="BookNotoBold")
    text(d, 40, 76, "构建更开放的未来", 15,
         color=colors.white, font="BookNotoBold")
    for x in (204, 296, 388, 480):
        d.add(Line(x, 62, x, 111, strokeColor=colors.HexColor("#8db4a2"),
                   strokeWidth=0.65))
    for x, icon, title, detail in ((221, "◇", "原理图解", "概念不抽象"),
                                   (313, "</>", "开源实现", "代码可对照"),
                                   (405, "□", "案例驱动", "项目可实践"),
                                   (497, "○", "持续演进", "社区共建")):
        text(d, x + 12, 98, icon, 14, color=colors.white,
             font="BookCode" if icon == "</>" else "BookNoto")
        text(d, x, 79, title, 8.5, color=colors.white, font="BookNotoBold")
        text(d, x, 64, detail, 7.6, color=PALE)
    d.add(Line(40, 43, 552, 43, strokeColor=colors.HexColor("#a9c8b8"),
               strokeWidth=0.7))
    text(d, 40, 19, "AGENT SYSTEMS, ILLUSTRATED", 8.5,
         color=PALE, font="BookCode")
    text(d, 350, 19, "让更多人看懂、用好 Agent 系统", 8.3, color=PALE)
    return d


def write_svg(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    renderSVG.drawToFile(cover_drawing(), str(path))
    svg = path.read_text(encoding="utf-8")
    font_dir = ROOT / "book" / ".cache"
    font_files = {
        "BookNoto": font_dir / "NotoSansSC-Regular.ttf",
        "BookNotoBold": font_dir / "NotoSansSC-Bold.ttf",
        "BookCode": font_dir / "JetBrainsMono-Regular.ttf",
    }
    fonts = {family: FontToolsFont(font_file) for family, font_file in font_files.items()}
    matches = 0

    def outlines(match: re.Match[str]) -> str:
        nonlocal matches
        matches += 1
        x, y, style = match.group("x", "y", "style")
        value = html.unescape(match.group("value"))
        family = re.search(r"font-family:\s*([^;]+)", style).group(1).strip()
        size = float(re.search(r"font-size:\s*([0-9.]+)px", style).group(1))
        fill = re.search(r"fill:\s*([^;]+)", style).group(1).strip()
        font = fonts[family]
        cmap = font.getBestCmap()
        glyph_set = font.getGlyphSet()
        advance = font["hmtx"].metrics
        parts = []
        cursor = 0
        for char in value:
            name = cmap.get(ord(char), ".notdef")
            pen = SVGPathPen(glyph_set)
            glyph_set[name].draw(pen)
            commands = pen.getCommands()
            if commands:
                parts.append(f'<path d="{commands}" transform="translate({cursor},0)"/>')
            cursor += advance[name][0]
        scale = size / font["head"].unitsPerEm
        accessible = html.escape(value, quote=True)
        return (f'<g transform="translate({x},{y}) scale({scale})" '
                f'style="fill:{fill};stroke:none;fill-rule:nonzero" aria-label="{accessible}">'
                + "".join(parts) + "</g>")

    pattern = re.compile(
        r'<text x="(?P<x>[^"]+)" y="(?P<y>[^"]+)" style="(?P<style>[^"]+)" '
        r'transform="[^"]+">(?P<value>.*?)</text>', re.S)
    svg = pattern.sub(outlines, svg)
    if matches < 20 or "<text " in svg:
        raise ValueError(f"Cover SVG text outline conversion incomplete: {matches} labels")
    path.write_text(svg, encoding="utf-8")
