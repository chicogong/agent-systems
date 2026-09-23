"""Check that the built book is complete enough for human print review."""

from __future__ import annotations

import argparse
import base64
from io import BytesIO
from pathlib import Path
import re
from tempfile import TemporaryDirectory

from PIL import Image
from pypdf import PdfReader

from build_book import DEFAULT_OUTPUT, FRONT_COVER, manifest_entries, manifest_paths
from book_cover import ORIGINAL, write_svg


def normalized_cover(svg: str) -> tuple[str, tuple[tuple[int, int], bytes]]:
    """Ignore platform-dependent PNG compression, not the cover's pixels or SVG."""
    images = re.findall(r"data:image/png;base64,([^\"]+)", svg)
    if len(images) != 1:
        raise ValueError(f"Cover SVG needs one embedded PNG, found {len(images)}")
    with Image.open(BytesIO(base64.b64decode(images[0]))) as embedded:
        pixels = (embedded.size, embedded.convert("RGBA").tobytes())
    return svg.replace(images[0], "<embedded-png>"), pixels


def check(path: Path) -> None:
    if not path.is_file():
        raise FileNotFoundError(path)
    reader = PdfReader(str(path))
    chapters = manifest_paths()
    if len(reader.pages) < len(chapters) + 4:
        raise ValueError(f"Only {len(reader.pages)} pages for {len(chapters)} chapters")
    def count_outline(items):
        return sum(count_outline(item) if isinstance(item, list) else 1 for item in items)

    expected_outlines = len(chapters) + sum(kind == "part" for kind, _ in manifest_entries())
    if count_outline(reader.outline) != expected_outlines:
        raise ValueError(f"PDF outline has {count_outline(reader.outline)} entries; expected {expected_outlines}")
    links = 0
    images = 0
    embedded_fonts = set()
    for page in reader.pages:
        for annotation in page.get("/Annots", []):
            value = annotation.get_object()
            action = value.get("/A")
            if action and action.get("/URI"):
                links += 1
        resources = page.get("/Resources", {})
        for font in resources.get("/Font", {}).values():
            descriptor = font.get_object().get("/FontDescriptor")
            if descriptor and descriptor.get_object().get("/FontFile2"):
                embedded_fonts.add(str(font.get_object().get("/BaseFont")))
        for obj in resources.get("/XObject", {}).values():
            if obj.get_object().get("/Subtype") == "/Image":
                images += 1
    if links < len(chapters):
        raise ValueError(f"Too few clickable source links: {links}")
    if images < 10:
        raise ValueError(f"Too few embedded figure images: {images}")
    if len(embedded_fonts) < 2:
        raise ValueError(f"Regular/bold fonts were not embedded: {embedded_fonts}")
    if not any("JetBrainsMono" in name for name in embedded_fonts):
        raise ValueError("Code font was not embedded")
    if not FRONT_COVER.is_file():
        raise ValueError("Editable mixed-media cover is missing")
    cover_svg = FRONT_COVER.read_text(encoding="utf-8")
    if "<svg" not in cover_svg or "data:image/png;base64" not in cover_svg or "<text " in cover_svg:
        raise ValueError("Cover SVG needs embedded art and portable vector type outlines")
    with TemporaryDirectory() as temporary:
        regenerated = Path(temporary) / "cover.svg"
        write_svg(regenerated)
        if normalized_cover(regenerated.read_text(encoding="utf-8")) != normalized_cover(cover_svg):
            raise ValueError("Tracked cover SVG differs from book_cover.py; rebuild it explicitly")
    with Image.open(ORIGINAL) as source:
        if source.size != (1024, 1536):
            raise ValueError(f"Selected illustration changed unexpectedly: {source.size}")
    # ReportLab's graphics renderer stores the one original illustration as an
    # inline image; page.images sees both inline and XObject images.
    cover_images = reader.pages[0].images
    if len(cover_images) != 1:
        raise ValueError(f"Cover needs one original illustration, found {len(cover_images)} images")
    cover_text = reader.pages[0].extract_text() or ""
    if "图解" not in cover_text or "Agent" not in cover_text or "chicogong" not in cover_text:
        raise ValueError("Vector cover text is missing or not extractable")
    title_text = reader.pages[1].extract_text() or ""
    if "图解 Agent 系统" not in title_text:
        raise ValueError("Accessible title page is missing")
    last_text = reader.pages[-1].extract_text() or ""
    if "不止会用" not in last_text or "github.com/chicogong/agent-systems" not in last_text:
        raise ValueError("Back cover is missing or not extractable")
    all_text = "\n".join(page.extract_text() or "" for page in reader.pages)
    for title in ("前言：看见回答背后的系统", "阅读指南：从问题进入", "结语：图会更新", "致谢与贡献", "作者简介"):
        if title not in all_text:
            raise ValueError(f"Book section missing: {title}")
    if "CC BY-SA" in all_text or "ISBN 978-7" in all_text:
        raise ValueError("Stale design placeholder leaked into PDF")
    print(f"Book PDF OK: {len(reader.pages)} pages, {len(chapters)} chapters, {images} image uses, {links} source links, {len(embedded_fonts)} embedded fonts")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", nargs="?", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    check(args.pdf.resolve())
