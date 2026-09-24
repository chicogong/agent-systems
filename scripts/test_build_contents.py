"""The tracked GitHub contents must be a complete view of the book manifest."""

import unittest

from build_contents import OUTPUT, render
from build_markdown import chapter_title, manifest_entries


class ContentsTests(unittest.TestCase):
    def test_tracked_contents_are_current(self):
        self.assertEqual(OUTPUT.read_text(encoding="utf-8"), render())

    def test_every_chapter_appears_once_in_order(self):
        contents = render()
        last_position = -1
        for number, (kind, value) in enumerate(
            ((kind, value) for kind, value in manifest_entries() if kind != "part"), start=1
        ):
            entry = f"{number}. [{chapter_title(value)}](../{value})"
            self.assertEqual(contents.count(entry), 1, entry)
            position = contents.index(entry)
            self.assertGreater(position, last_position)
            last_position = position


if __name__ == "__main__":
    unittest.main()
