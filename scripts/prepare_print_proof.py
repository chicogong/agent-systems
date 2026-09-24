"""Split the A4 reading PDF into non-final physical proof references.

The output is suitable for layout and legibility review, not for direct upload
as a perfect-bound production master. A printer must supply a cover template,
bleed, stock-dependent spine width, and a final file check.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from pypdf import PdfReader, PdfWriter


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "output/pdf/agent-systems-public-preview.pdf"
OUTPUT = ROOT / "output/pdf/print-proof"


def save_pages(reader: PdfReader, indices: range | list[int], target: Path, label: str) -> None:
    writer = PdfWriter()
    for index in indices:
        writer.add_page(reader.pages[index])
    writer.add_metadata({
        "/Title": "图解 Agent 系统 - " + label,
        "/Subject": "A4 layout proof only; not a commercial print master",
    })
    with target.open("wb") as stream:
        writer.write(stream)


def prepare(source: Path, output: Path) -> tuple[Path, Path, Path]:
    reader = PdfReader(source)
    if len(reader.pages) < 4:
        raise ValueError("Expected front cover, interior, and back cover")
    a4_width, a4_height = 595.276, 841.89
    for number, page in enumerate(reader.pages, 1):
        width, height = float(page.mediabox.width), float(page.mediabox.height)
        if abs(width - a4_width) > 1 or abs(height - a4_height) > 1:
            raise ValueError(f"Page {number} is not A4 portrait: {width:.1f} x {height:.1f} pt")

    output.mkdir(parents=True, exist_ok=True)
    front = output / "agent-systems-a4-front-cover-reference.pdf"
    interior = output / "agent-systems-a4-interior-proof.pdf"
    back = output / "agent-systems-a4-back-cover-reference.pdf"
    save_pages(reader, [0], front, "front cover reference")
    save_pages(reader, [len(reader.pages) - 1], back, "back cover reference")

    writer = PdfWriter()
    for index in range(1, len(reader.pages) - 1):
        writer.add_page(reader.pages[index])
    # Leave the title on a recto page. A multiple of four avoids a printer
    # silently inserting unpredictable blanks in a folded/signature proof.
    blank_count = (-len(writer.pages)) % 4
    for _ in range(blank_count):
        writer.add_blank_page(width=a4_width, height=a4_height)
    writer.add_metadata({
        "/Title": "图解 Agent 系统 - A4 interior proof",
        "/Subject": "Layout proof only; blank pages added at end; no bleed or printer template",
    })
    with interior.open("wb") as stream:
        writer.write(stream)
    return front, interior, back


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT)
    args = parser.parse_args()
    for path in prepare(args.source, args.output_dir):
        print(path)


if __name__ == "__main__":
    main()
