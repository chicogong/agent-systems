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
    d.text("title", "Mem0：多信号排序，不等于三路召回并集", 35, 28, 1390, 34, INK, 8)
    d.text("subtitle", "同步 OSS Memory.search 路径：先确定向量候选，再叠加关键词与实体分数。", 38, 84, 1350, 22, MUTED, 8)

    d.arrow("q-semantic", [(263, 425), (347, 425), (347, 237), (410, 237)], BLUE)
    d.arrow("q-keyword", [(263, 425), (410, 425)], ORANGE)
    d.arrow("q-entity", [(263, 425), (347, 425), (347, 617), (410, 617)], GREEN)
    d.arrow("semantic-candidates", [(659, 237), (755, 237)], BLUE)
    d.arrow("candidates-rank", [(1012, 237), (1110, 237), (1110, 371)], BLUE)
    d.arrow("keyword-rank", [(659, 425), (1014, 425)], ORANGE)
    d.arrow("entity-rank", [(659, 617), (955, 617), (955, 470), (1014, 470)], GREEN)
    d.arrow("rank-result", [(1146, 533), (1146, 634)], PURPLE)

    oval(d, "query", 53, 376, 210, 100, INK, "#f1f5f9")
    d.text("query-label", "query\n+ filters", 92, 391, 155, 26, INK, 8)

    oval(d, "semantic", 410, 189, 249, 96, BLUE, "#a5d8ff")
    d.text("semantic-label", "语义向量检索", 435, 212, 220, 26, "#2563a6", 8)
    oval(d, "keyword", 410, 377, 249, 96, ORANGE, "#fff3bf")
    d.text("keyword-label", "关键词 / BM25", 438, 401, 220, 26, "#9a6700", 8)
    oval(d, "entity", 410, 569, 249, 96, GREEN, "#c3fae8")
    d.text("entity-label", "实体关联", 470, 594, 180, 26, "#166534", 8)

    d.box("candidates", 755, 179, 257, 115, BLUE, "#e5f3ff")
    d.text("candidate-title", "候选集合", 782, 197, 215, 26, INK, 8)
    d.text("candidate-body", "仅语义结果入池", 782, 242, 215, 23, MUTED, 8)
    d.box("rank", 1014, 371, 264, 162, PURPLE, "#d0bfff")
    d.text("rank-title", "score_and_rank", 1036, 390, 226, 25, INK)
    d.text("rank-body", "先过语义阈值\n再叠加两类加分", 1036, 433, 218, 23, INK, 8)
    d.box("result", 1014, 634, 264, 99, PURPLE, "#e5dbff")
    d.text("result-label", "排序后 top_k\n格式化结果", 1036, 650, 220, 24, INK, 8)

    d.text("bm25-note", "若向量库不支持 keyword_search，返回 None", 689, 329, 515, 21, MUTED, 8)
    d.text("candidate-note", "关键词命中不能单独入候选池", 560, 521, 390, 21, MUTED, 8)
    d.text("source-note", "写入侧另见正文：add(infer=True) → 事实提取 → 去重 → insert；此图只画 search。", 48, 803, 1310, 21, MUTED, 8)
    d.text("scope", "不保证每种向量库都有关键词搜索。", 48, 845, 1330, 19, MUTED, 8)
    for element in d.elements:
        if element["type"] == "arrow":
            element.update(roughness=1, strokeWidth=3)
        elif element["type"] == "rectangle":
            element["roughness"] = 1
    d.save(Path(__file__).with_name("scene.excalidraw"))


if __name__ == "__main__":
    main()
