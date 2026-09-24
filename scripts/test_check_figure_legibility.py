"""Geometry and manifest-path checks for the A4 figure preflight."""

from __future__ import annotations

import json
import struct
import tempfile
import unittest
import zlib
from pathlib import Path

from check_figure_legibility import (
    CONTENT_W,
    PT_PER_MM,
    inspect_figure,
    referenced_images,
)


class FigureLegibilityTests(unittest.TestCase):
    @staticmethod
    def write_png(path: Path, width: int, height: int) -> None:
        """Create a valid 1-bit grayscale PNG using only the standard library."""
        def chunk(name: bytes, content: bytes) -> bytes:
            return (struct.pack(">I", len(content)) + name + content
                    + struct.pack(">I", zlib.crc32(name + content)))

        row = b"\0" + b"\xff" * ((width + 7) // 8)
        header = struct.pack(">IIBBBBB", width, height, 1, 0, 0, 0, 0)
        path.write_bytes(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header)
                         + chunk(b"IDAT", zlib.compress(row * height))
                         + chunk(b"IEND", b""))

    def make_figure(self, parent: Path, *, png_size: tuple[int, int],
                    viewbox_size: tuple[int, int], fonts: tuple[int, ...]) -> Path:
        parent.mkdir(parents=True)
        image = parent / "preview.png"
        self.write_png(image, *png_size)
        width, height = viewbox_size
        svg_text = "".join(
            f'<text font-size="{font}px">label {index}</text>'
            for index, font in enumerate(fonts)
        )
        (parent / "diagram.svg").write_text(
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">{svg_text}</svg>',
            encoding="utf-8",
        )
        (parent / "scene.excalidraw").write_text(json.dumps({"elements": [
            {"type": "text", "text": f"label {index}", "fontSize": font}
            for index, font in enumerate(fonts)
        ]}), encoding="utf-8")
        return image

    def test_width_limited_print_size_and_pixel_density_are_independent(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            image = self.make_figure(Path(temporary) / "wide", png_size=(4000, 2000),
                                     viewbox_size=(1000, 500), fonts=(16, 20, 30))
            result = inspect_figure(image, uses=2)
            self.assertAlmostEqual(result.display_width_pt, CONTENT_W)
            self.assertAlmostEqual(result.display_height_pt, CONTENT_W / 2)
            self.assertAlmostEqual(result.min_text_pt, 16 * CONTENT_W / 1000)
            self.assertAlmostEqual(result.p10_text_pt, 16.8 * CONTENT_W / 1000)
            self.assertGreater(result.effective_ppi, 300)
            self.assertLess(result.min_text_pt, 8)
            self.assertEqual(result.smallest_labels, ("label 0",))

    def test_height_limit_uses_actual_display_size(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            image = self.make_figure(Path(temporary) / "tall", png_size=(2000, 4000),
                                     viewbox_size=(500, 1000), fonts=(20,))
            result = inspect_figure(image, uses=1)
            self.assertAlmostEqual(result.display_height_pt, 168 * PT_PER_MM)
            self.assertAlmostEqual(result.display_width_pt, 84 * PT_PER_MM)
            self.assertAlmostEqual(result.min_text_pt, 20 * 168 * PT_PER_MM / 1000)
            self.assertEqual(result.p10_text_pt, result.min_text_pt)

    def test_only_manifest_full_line_images_are_counted_and_svg_uses_png(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            image = self.make_figure(root / "figures" / "sample", png_size=(400, 200),
                                     viewbox_size=(100, 50), fonts=(16,))
            markdown = root / "docs" / "chapter.md"
            markdown.parent.mkdir()
            markdown.write_text(
                "![first](../figures/sample/diagram.svg)\n"
                "![second](../figures/sample/diagram.svg)\n"
                "See ![inline](../figures/sample/diagram.svg) in prose.\n",
                encoding="utf-8",
            )
            self.assertEqual(referenced_images([("chapter", markdown)], root), {image: 2})


if __name__ == "__main__":
    unittest.main()
