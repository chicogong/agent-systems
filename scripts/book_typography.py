"""Chinese punctuation-aware wrapping for this book's prose paragraphs.

The stock ReportLab 4.4.9 CJK wrapper allows hanging punctuation and has an
incomplete Chinese prohibition list.  Here we choose a legal break *within*
the available width instead.  No source text, font, or link markup is changed.

This is a local Paragraph subclass, not a ReportLab monkeypatch.  ReportLab's
``cjkU`` / ``makeCJKParaLine`` / ``ParaLines`` helpers retain styled fragments
and their drawing metadata.  These are internal interfaces of our pinned
ReportLab dependency; upgrading it requires the typography regression tests.
The break-selection algorithm below is original, not copied from ReportLab.
"""

from __future__ import annotations

from bisect import bisect_right
from unicodedata import category

from reportlab.platypus import Paragraph
from reportlab.platypus.paragraph import (
    ParaLines,
    _handleBulletWidth,
    cjkU,
    makeCJKParaLine,
)


# Closing punctuation travels with the preceding character.  Opening brackets
# travel with the following character.  This includes consecutive closers such
# as “）。” and punctuation at a change of font or link span.
NO_LINE_START = frozenset("，。、；：？！）〕］｝〉》」』】〗〙〛’”％‰…,.!?;:)]}")
NO_LINE_END = frozenset("（〔［｛〈《「『【〖〘〚‘“([{")
NO_BREAK_SPACE = frozenset("\u00a0\u202f\u2060")
_EPSILON = 1e-7


def _word_char(char: str) -> bool:
    """Keep short Latin words/identifiers together when they fit a line."""
    return bool(char) and (char.isascii() and (char.isalnum() or char == "_"))


def _legal_break(left: str, right: str) -> bool:
    if left in NO_LINE_END or right in NO_LINE_START:
        return False
    if left in NO_BREAK_SPACE or right in NO_BREAK_SPACE:
        return False
    # Do not split combining marks or a joined Unicode sequence.
    if right and (category(right).startswith("M") or right == "\u200d"):
        return False
    return left != "\u200d"


def _line_spans(glyphs: list[cjkU], widths: list[float]) -> list[tuple[int, int, float, bool]]:
    """Return (start, stop, limit, explicit_break), without hanging glyphs.

    Find the longest fitting prefix, then step back to a legal boundary.  Latin
    word boundaries are preferred; an overlong identifier/URL can still split
    at a safe character boundary.  A line too narrow for even an indivisible
    punctuation pair fails visibly rather than overflowing or looping forever.
    """
    if not glyphs:
        return []
    prefix = [0.0]
    for glyph in glyphs:
        prefix.append(prefix[-1] + float(glyph.width))
    previous, following = [], [""] * (len(glyphs) + 1)
    char = ""
    for glyph in glyphs:
        previous.append(char)
        if glyph and not (glyph.isspace() and glyph not in NO_BREAK_SPACE):
            char = str(glyph)
    previous.append(char)
    char = ""
    for index in range(len(glyphs) - 1, -1, -1):
        if glyphs[index] and not (glyphs[index].isspace() and glyphs[index] not in NO_BREAK_SPACE):
            char = str(glyphs[index])
        following[index] = char

    legal, preferred = [], []
    for index in range(1, len(glyphs)):
        left, right = previous[index], following[index]
        if _legal_break(left, right):
            legal.append(index)
            if not (_word_char(left) and _word_char(right)) or glyphs[index - 1].isspace() or glyphs[index].isspace():
                preferred.append(index)

    breaks = [i + 1 for i, glyph in enumerate(glyphs) if hasattr(glyph.frag, "lineBreak")]
    breaks.append(len(glyphs))
    result = []
    start = 0
    for stop in breaks:
        while start < stop:
            limit = widths[min(len(result), len(widths) - 1)]
            if limit <= 0:
                raise ValueError("Book paragraph has no available line width")
            fit = min(stop, bisect_right(prefix, prefix[start] + limit + _EPSILON) - 1)
            if fit == stop:
                end = stop
            else:
                choices = preferred if bisect_right(preferred, fit) > bisect_right(preferred, start) else legal
                choice = bisect_right(choices, fit) - 1
                end = choices[choice] if choice >= 0 else start
                if end <= start:
                    raise ValueError(
                        f"Book paragraph width {limit:g} pt cannot fit a Chinese punctuation group"
                    )
            explicit = end == stop and hasattr(glyphs[end - 1].frag, "lineBreak")
            result.append((start, end, limit, explicit))
            start = end
    return result


class BookParagraph(Paragraph):
    """Use legal Chinese breaks for prose; leave non-CJK layout unchanged."""

    def breakLinesCJK(self, maxWidths):
        if getattr(self, "_splitpara", False) and hasattr(self, "blPara"):
            return self.blPara
        widths = list(maxWidths) if isinstance(maxWidths, (list, tuple)) else [maxWidths]
        _handleBulletWidth(self.bulletText, self.style, widths)
        glyphs = []
        for fragment in self.frags:
            text = fragment.text
            if isinstance(text, bytes):
                text = text.decode(self.encoding)
            # Keep empty callbacks (e.g. named anchors) and explicit <br/>.
            glyphs.extend(cjkU(char, fragment, self.encoding) for char in text or [""])
        auto_leading = getattr(self, "autoLeading", getattr(self.style, "autoLeading", ""))
        calc_bounds = auto_leading not in ("", "off")
        lines = []
        self._width_max = 0
        for start, end, limit, explicit in _line_spans(glyphs, widths):
            run = glyphs[start:end]
            used = sum(float(glyph.width) for glyph in run)
            self._width_max = max(self._width_max, used)
            lines.append(makeCJKParaLine(run, limit, used, limit - used, explicit, calc_bounds))
        return ParaLines(kind=1, lines=lines)

    def _get_split_blParaFunc(self):
        if self.style.wordWrap != "CJK":
            return super()._get_split_blParaFunc()

        def fragments(blPara, start, stop):
            # Native hard splitting inserts ASCII spaces between old wrapped
            # lines.  A Chinese paragraph must instead preserve its exact text
            # when the continuation is rewrapped on a new page.
            return [fragment.clone() for line in blPara.lines[start:stop] for fragment in line.words]

        return fragments
