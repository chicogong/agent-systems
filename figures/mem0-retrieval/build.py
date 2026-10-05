"""Build Mem0's retrieval funnel as editable Excalidraw elements."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from diagram_style import Scene  # noqa: E402

BLUE = "#4a9eed"
GREEN = "#16a34a"
INK = "#14213d"
MUTED = "#475569"
ORANGE = "#f59e0b"
PURPLE = "#8b5cf6"


def oval(d: Scene, name: str, x: int, y: int, w: int, h: int, stroke: str, fill: str) -> None:
    e = d._base(name, "ellipse", x, y, w, h)
    e.update(strokeColor=stroke, backgroundColor=fill, roughness=1, strokeWidth=2)
    d.elements.append(e)


def main() -> None:
    d = Scene()
    d.text("title", "Mem0：先按含义找记忆，再加分排序", 35, 28, 1390, 34, INK, 8)
    d.arrow("q-semantic", [(268, 400), (325, 400), (325, 237), (400, 237)], BLUE)
    d.arrow("q-keyword", [(278, 425), (400, 425)], ORANGE)
    d.arrow("q-entity", [(268, 450), (345, 450), (345, 617), (400, 617)], GREEN)
    d.arrow("semantic-candidates", [(670, 237), (755, 237)], BLUE)
    d.arrow("candidates-rank", [(1012, 237), (1110, 237), (1110, 371)], BLUE)
    d.arrow("keyword-rank", [(670, 425), (1014, 425)], ORANGE)
    d.arrow("entity-rank", [(670, 617), (955, 617), (955, 470), (1014, 470)], GREEN)
    d.arrow("rank-result", [(1146, 533), (1146, 634)], PURPLE)

    oval(d, "query", 38, 361, 240, 130, INK, "#f1f5f9")
    d.text("query-label", "查询 query\n范围 filters", 53, 391, 210, 27, INK, 8, align="center")

    oval(d, "semantic", 400, 172, 270, 130, BLUE, "#a5d8ff")
    d.text("semantic-label", "按含义查找\n语义向量检索", 415, 202, 240, 27, "#2563a6", 8, align="center")
    oval(d, "keyword", 400, 360, 270, 130, ORANGE, "#fff3bf")
    d.text("keyword-label", "关键词 BM25\n可用时加分", 415, 390, 240, 27, "#9a6700", 8, align="center")
    oval(d, "entity", 400, 552, 270, 130, GREEN, "#c3fae8")
    d.text("entity-label", "找到相关实体\n命中时加分", 415, 582, 240, 27, "#166534", 8, align="center")

    d.box("candidates", 755, 179, 257, 115, BLUE, "#e5f3ff")
    d.text("candidate-title", "入围记忆", 782, 195, 215, 27, INK, 8)
    d.text("candidate-body", "只取语义结果", 782, 242, 215, 27, MUTED, 8)
    d.box("rank", 1014, 371, 264, 162, PURPLE, "#d0bfff")
    d.text("rank-title", "score_and_rank", 1036, 390, 226, 27, INK)
    d.text("rank-body", "先过语义阈值\n再加分并排序", 1036, 433, 218, 27, INK, 8)
    d.box("result", 1014, 634, 264, 99, PURPLE, "#e5dbff")
    d.text("result-label", "取前 top_k 条\n整理结果格式", 1036, 650, 220, 27, INK, 8)
    for element in d.elements:
        if element["type"] == "arrow":
            element.update(roughness=1, strokeWidth=3)
        elif element["type"] == "rectangle":
            element["roughness"] = 1
    d.save(Path(__file__).with_name("scene.excalidraw"))


if __name__ == "__main__":
    main()
