"""The physical proof split must preserve pages without claiming a print master."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from pypdf import PdfReader, PdfWriter

from prepare_print_proof import prepare


class PrintProofTests(unittest.TestCase):
    def test_splits_covers_and_pads_only_at_end(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source.pdf"
            writer = PdfWriter()
            for number in range(7):
                writer.add_blank_page(width=595.276, height=841.89).rotate(number * 90 % 360)
            with source.open("wb") as stream:
                writer.write(stream)

            front, interior, back = prepare(source, root / "proof")
            self.assertEqual(len(PdfReader(front).pages), 1)
            self.assertEqual(len(PdfReader(back).pages), 1)
            pages = PdfReader(interior).pages
            self.assertEqual(len(pages), 8)
            self.assertEqual([page.get("/Rotate", 0) for page in pages[:5]], [90, 180, 270, 0, 90])
            self.assertTrue(all(page.get("/Rotate", 0) == 0 for page in pages[5:]))

    def test_rejects_non_a4(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source.pdf"
            writer = PdfWriter()
            for _ in range(4):
                writer.add_blank_page(width=612, height=792)
            with source.open("wb") as stream:
                writer.write(stream)
            with self.assertRaisesRegex(ValueError, "not A4"):
                prepare(source, root / "proof")


if __name__ == "__main__":
    unittest.main()
