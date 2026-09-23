"""Small native Excalidraw scene builder for this guide's technical diagrams.

No third-party package is needed to regenerate the editable source. Rendering is
handled separately by excalidraw-agent's pinned browser renderer.
"""

from __future__ import annotations

import json
from pathlib import Path

INK = "#202735"
MUTED = "#526071"
BLUE = "#3478e5"
PURPLE = "#8056e8"
GREEN = "#2fa86a"
ORANGE = "#e88816"


class Scene:
    def __init__(self) -> None:
        self.elements: list[dict] = []

    def _base(self, name: str, kind: str, x: int, y: int, w: int, h: int) -> dict:
        number = len(self.elements)
        return {
            "id": name, "type": kind, "x": x, "y": y, "width": w, "height": h,
            "angle": 0, "strokeColor": INK, "backgroundColor": "transparent",
            "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
            "roughness": 0, "opacity": 100, "groupIds": [], "frameId": None,
            "index": f"a{number:04d}", "roundness": None,
            "seed": 1300 + number * 37, "version": 1,
            "versionNonce": 5200 + number * 53, "isDeleted": False,
            "boundElements": [], "updated": 1, "link": None, "locked": False,
        }

    def box(self, name: str, x: int, y: int, w: int, h: int, stroke: str, fill: str) -> None:
        element = self._base(name, "rectangle", x, y, w, h)
        element.update(strokeColor=stroke, backgroundColor=fill, roundness={"type": 3})
        self.elements.append(element)

    def text(self, name: str, value: str, x: int, y: int, w: int, size: int,
             color: str = INK, font: int = 8, align: str = "left") -> None:
        element = self._base(name, "text", x, y, w, round(size * 1.3 * len(value.splitlines())))
        element.update(
            strokeColor=color, strokeWidth=1, text=value, fontSize=size,
            fontFamily=font, textAlign=align, verticalAlign="top",
            containerId=None, originalText=value, autoResize=False,
            lineHeight=1.25,
        )
        self.elements.append(element)

    def arrow(self, name: str, points: list[tuple[int, int]], color: str) -> None:
        x, y = points[0]
        element = self._base(name, "arrow", x, y, points[-1][0] - x, points[-1][1] - y)
        element.update(
            strokeColor=color, strokeWidth=2, roundness=None,
            points=[[px - x, py - y] for px, py in points],
            lastCommittedPoint=None, startBinding=None, endBinding=None,
            startArrowhead=None, endArrowhead="arrow", elbowed=False,
        )
        self.elements.append(element)

    def save(self, filename: Path) -> None:
        scene = {
            "type": "excalidraw", "version": 2,
            "source": "https://excalidraw.com", "elements": self.elements,
            "appState": {"viewBackgroundColor": "#ffffff"}, "files": {},
        }
        filename.write_text(json.dumps(scene, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
