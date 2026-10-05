"""A stale SVG must fail even when its file exists and its size looks right."""

import tempfile
import unittest
from pathlib import Path
from xml.sax.saxutils import escape

from check_repo import check_exported_labels


class ExportedFigureLabelTests(unittest.TestCase):
    def compare(self, text="读取材料\n返回结果", labels=None, size=23, color="#172336",
                deleted=False, source_color="#172336"):
        scene = {"elements": [{"type": "text", "text": text, "fontSize": 23,
                                "strokeColor": source_color, "isDeleted": deleted}]}
        if labels is None:
            labels = text.splitlines()
        nodes = "".join(f'<text font-size="{size}px" fill="{color}">{escape(label)}</text>'
                        for label in labels)
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "diagram.svg"
            path.write_text(f'<svg xmlns="http://www.w3.org/2000/svg">{nodes}</svg>', encoding="utf-8")
            return check_exported_labels(scene, path)

    def test_native_multiline_labels_match(self):
        self.assertEqual(self.compare(), [])

    def test_whitespace_and_hex_case_are_normalized(self):
        self.assertEqual(self.compare(text="read  document", labels=["read document"], color="#172336"), [])
        self.assertEqual(self.compare(text="工具", source_color="#aAbBcC", color="#AABBCC"), [])

    def test_old_export_fails(self):
        self.assertTrue(self.compare(labels=["旧图文字", "返回结果"]))

    def test_missing_repeated_label_fails(self):
        self.assertTrue(self.compare(text="工具\n工具", labels=["工具"]))

    def test_extra_label_fails(self):
        self.assertTrue(self.compare(labels=["读取材料", "返回结果", "旧注释"]))

    def test_wrong_size_or_color_fails(self):
        self.assertTrue(self.compare(size=21))
        self.assertTrue(self.compare(color="#3478e5"))

    def test_deleted_source_text_is_not_expected(self):
        self.assertEqual(self.compare(deleted=True, labels=[]), [])

    def test_invalid_svg_fails(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "diagram.svg"
            path.write_text("<svg", encoding="utf-8")
            self.assertTrue(check_exported_labels({"elements": []}, path))

    def test_missing_source_fields_report_a_scene_error(self):
        for field in ("fontSize", "strokeColor"):
            with self.subTest(field=field):
                element = {"type": "text", "text": "工具", "fontSize": 23, "strokeColor": "#172336"}
                del element[field]
                errors = check_exported_labels({"elements": [element]}, Path("unused.svg"))
                self.assertTrue(errors[0].startswith("invalid scene labels"))

    def test_invalid_source_font_size_reports_a_scene_error(self):
        element = {"type": "text", "text": "工具", "fontSize": "bad", "strokeColor": "#172336"}
        errors = check_exported_labels({"elements": [element]}, Path("unused.svg"))
        self.assertTrue(errors[0].startswith("invalid scene labels"))


if __name__ == "__main__":
    unittest.main()
