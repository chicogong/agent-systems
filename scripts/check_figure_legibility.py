"""Report the physical text size of figures at their A4 book placement.

This is a geometric preflight, not a claim that a diagram is readable. Pixel
density and printed text size are independent checks. The PDF builder remains
the authority for layout; keep MAX_FIGURE_HEIGHT in sync with its figure().
"""

from __future__ import annotations

import argparse
import json
import math
import re
import struct
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "book" / "manifest.txt"
IMAGE = re.compile(r"^!\[([^\]]*)\]\(([^)]+)\)$")  # build_book.py:IMAGE
PT_PER_MM = 72 / 25.4
CONTENT_W = 168 * PT_PER_MM  # A4 width 210 mm, 21 mm margins on both sides
MAX_FIGURE_HEIGHT = 168 * PT_PER_MM  # build_book.py:figure()
REVIEW_BELOW_PT = 8.0


@dataclass(frozen=True)
class FigureReport:
    image: Path
    uses: int
    display_width_pt: float
    display_height_pt: float
    effective_ppi: float
    min_text_pt: float | None
    p10_text_pt: float | None
    smallest_labels: tuple[str, ...]
    note: str = ""


def manifest_entries() -> list[tuple[str, str | Path]]:
    """Read the same @front/@part/@back chapter paths as the PDF builder."""
    entries: list[tuple[str, str | Path]] = []
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
        entries.append((kind, path))
    return entries


def referenced_images(entries: list[tuple[str, str | Path]], root: Path) -> dict[Path, int]:
    """Follow only full-line images that build_book.chapter_flowables renders."""
    uses: dict[Path, int] = {}
    for kind, value in entries:
        if kind == "part":
            continue
        markdown = Path(value)
        for line in markdown.read_text(encoding="utf-8").splitlines():
            match = IMAGE.match(line.strip())
            if not match:
                continue
            destination = match.group(2)
            image = (markdown.parent / destination).resolve()
            if image.suffix == ".svg":
                image = image.with_name("preview.png")
            if not image.is_relative_to(root):
                raise ValueError(f"Image escapes repository: {markdown}: {destination}")
            uses[image] = uses.get(image, 0) + 1
    return uses


def percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    if not ordered:
        raise ValueError("No values for percentile")
    rank = fraction * (len(ordered) - 1)
    low = math.floor(rank)
    high = math.ceil(rank)
    return ordered[low] + (ordered[high] - ordered[low]) * (rank - low)


def png_dimensions(path: Path) -> tuple[int, int]:
    """Read PNG IHDR dimensions without decoding or changing the image."""
    with path.open("rb") as source:
        header = source.read(24)
    if (len(header) != 24 or header[:8] != b"\x89PNG\r\n\x1a\n"
            or header[8:12] != b"\x00\x00\x00\r" or header[12:16] != b"IHDR"):
        raise ValueError(f"Invalid PNG header: {path}")
    width, height = struct.unpack(">II", header[16:24])
    if width == 0 or height == 0:
        raise ValueError(f"Invalid PNG dimensions: {path}")
    return width, height


def inspect_figure(image: Path, uses: int) -> FigureReport:
    scene_path = image.with_name("scene.excalidraw")
    svg_path = image.with_name("diagram.svg")
    width, height = png_dimensions(image)
    scale = min(CONTENT_W / width, MAX_FIGURE_HEIGHT / height)
    display_width, display_height = width * scale, height * scale

    svg = ET.parse(svg_path).getroot()
    viewbox = [float(value) for value in svg.attrib["viewBox"].replace(",", " ").split()]
    if len(viewbox) != 4 or viewbox[2] <= 0 or viewbox[3] <= 0:
        raise ValueError(f"Invalid SVG viewBox: {svg_path}")
    svg_width, svg_height = viewbox[2:]
    x_scale = display_width / svg_width
    y_scale = display_height / svg_height
    if not math.isclose(x_scale, y_scale, rel_tol=0.01):
        raise ValueError(f"PNG/SVG aspect ratio differs by over 1%: {image}")

    scene = json.loads(scene_path.read_text(encoding="utf-8"))
    texts = [
        element for element in scene.get("elements", [])
        if element.get("type") == "text"
        and element.get("text", "").strip()
        and not element.get("isDeleted", False)
        and element.get("opacity", 100) > 0
        and isinstance(element.get("fontSize"), (int, float))
        and element["fontSize"] > 0
    ]
    if not texts:
        return FigureReport(image, uses, display_width, display_height, 72 / scale,
                            None, None, (), "no visible scene text; manual review")

    sizes = [float(element["fontSize"]) * x_scale for element in texts]
    smallest = min(sizes)
    labels = tuple(
        " ".join(element["text"].split())[:65]
        for element, size in zip(texts, sizes)
        if math.isclose(size, smallest) and element.get("text", "").strip()
    )[:3]
    svg_fonts = [
        float(node.attrib["font-size"].removesuffix("px"))
        for node in svg.iter()
        if node.tag.endswith("text") and "font-size" in node.attrib
    ]
    note = ""
    if not svg_fonts:
        note = "SVG has no inspectable text; verify export before judging size"
    elif not math.isclose(min(svg_fonts) * x_scale, smallest, abs_tol=0.25):
        note = "scene/SVG minimum font differs; verify export before judging size"
    return FigureReport(image, uses, display_width, display_height, 72 / scale,
                        smallest, percentile(sizes, 0.10), labels, note)


def select_reports(reports: list[FigureReport], figures: list[str]) -> list[FigureReport]:
    if not figures:
        return reports
    selected = [report for report in reports
                if report.image.parent.name in figures
                or report.image.parent.relative_to(ROOT).as_posix() in figures]
    unknown = set(figures) - {
        name for report in selected
        for name in (report.image.parent.name, report.image.parent.relative_to(ROOT).as_posix())
    }
    if unknown:
        raise ValueError(f"No manifest figure matched: {', '.join(sorted(unknown))}")
    return selected


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict", action="store_true",
                        help="exit nonzero when a selected figure estimates below 8 pt")
    parser.add_argument("--figure", action="append", default=[], metavar="NAME",
                        help="limit report/strict gate to a manifest figure directory; repeatable")
    args = parser.parse_args(argv)
    try:
        images = referenced_images(manifest_entries(), ROOT)
        reports = [inspect_figure(image, uses) for image, uses in sorted(images.items())]
        reports = select_reports(reports, args.figure)
    except (OSError, ValueError, KeyError, ET.ParseError, json.JSONDecodeError) as error:
        print(f"Figure preflight error: {error}", file=sys.stderr)
        return 2

    print("Figure A4 preflight (geometric estimates; inspect rendered pages at print size)")
    print("figure | uses | size mm | effective PPI | min / p10 text pt | review")
    needs_review = 0
    for report in reports:
        small = report.min_text_pt is not None and report.min_text_pt < REVIEW_BELOW_PT
        if small or report.min_text_pt is None or report.note:
            needs_review += 1
        size = (f"{report.display_width_pt/PT_PER_MM:.0f}x"
                f"{report.display_height_pt/PT_PER_MM:.0f}")
        text_size = (f"{report.min_text_pt:.1f} / {report.p10_text_pt:.1f}"
                     if report.min_text_pt is not None else "unknown")
        status = "A4 human review" if small or report.min_text_pt is None or report.note else "-"
        print(f"{report.image.parent.name} | {report.uses} | {size} | "
              f"{report.effective_ppi:.0f} | {text_size} | {status}")
        if small:
            print(f"  smallest labels: {'; '.join(report.smallest_labels)}")
        if report.note:
            print(f"  {report.note}")
    print(f"{len(reports)} figures; {needs_review} need manual review. "
          "300 PPI does not establish legibility.")
    return 1 if args.strict and needs_review else 0


if __name__ == "__main__":
    raise SystemExit(main())
