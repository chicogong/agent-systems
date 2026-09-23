"""Build Mem0's retrieval funnel as editable Excalidraw elements."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from diagram_style import BLUE, GREEN, INK, MUTED, ORANGE, PURPLE, Scene  # noqa: E402


def oval(d: Scene, name: str, x: int, y: int, w: int, h: int, stroke: str, fill: str) -> None:
    e = d._base(name, "ellipse", x, y, w, h)
    e.update(strokeColor=stroke, backgroundColor=fill)
    d.elements.append(e)


def main() -> None:
    d = Scene()
    d.text("title", "Mem0：多信号排序，不等于三路召回并集", 35, 28, 1390, 36, INK, 6)
    d.text("subtitle", "同步 OSS Memory.search 路径：先确定向量候选，再叠加关键词与实体分数。", 38, 84, 1350, 20, MUTED, 6)

    d.arrow("q-semantic", [(263, 425), (347, 425), (347, 237), (410, 237)], BLUE)
    d.arrow("q-keyword", [(263, 425), (410, 425)], ORANGE)
    d.arrow("q-entity", [(263, 425), (347, 425), (347, 617), (410, 617)], GREEN)
    d.arrow("semantic-candidates", [(659, 237), (755, 237)], BLUE)
    d.arrow("candidates-rank", [(1012, 237), (1110, 237), (1110, 371)], BLUE)
    d.arrow("keyword-rank", [(659, 425), (1014, 425)], ORANGE)
    d.arrow("entity-rank", [(659, 617), (955, 617), (955, 470), (1014, 470)], GREEN)
    d.arrow("rank-result", [(1146, 533), (1146, 634)], PURPLE)

    oval(d, "query", 53, 376, 210, 100, INK, "#f0f2f6")
    d.text("query-label", "query\n+ filters", 92, 397, 155, 22, INK, 8)

    oval(d, "semantic", 410, 189, 249, 96, BLUE, "#dcecff")
    d.text("semantic-label", "语义向量检索", 435, 217, 220, 22, BLUE, 6)
    oval(d, "keyword", 410, 377, 249, 96, ORANGE, "#fff2d5")
    d.text("keyword-label", "关键词 / BM25", 438, 406, 220, 22, ORANGE, 6)
    oval(d, "entity", 410, 569, 249, 96, GREEN, "#ddf5e8")
    d.text("entity-label", "实体关联", 470, 599, 180, 22, GREEN, 6)

    d.box("candidates", 755, 179, 257, 115, BLUE, "#ecf5ff")
    d.text("candidate-title", "候选集合", 782, 201, 215, 23, INK, 6)
    d.text("candidate-body", "仅语义结果入池", 782, 246, 215, 19, MUTED, 6)
    d.box("rank", 1014, 371, 264, 162, PURPLE, "#eee7ff")
    d.text("rank-title", "score_and_rank", 1036, 396, 226, 22, INK)
    d.text("rank-body", "先过语义阈值\n再叠加两类加分", 1036, 439, 218, 18, MUTED, 6)
    d.box("result", 1014, 634, 264, 99, PURPLE, "#f4efff")
    d.text("result-label", "排序后 top_k\n格式化结果", 1036, 655, 220, 20, INK, 6)

    d.text("bm25-note", "若向量库不支持 keyword_search，返回 None", 689, 334, 515, 17, MUTED, 6)
    d.text("candidate-note", "关键词命中不能单独把记忆送入候选池", 692, 562, 480, 17, MUTED, 6)
    d.text("source-note", "写入侧：add(infer=True) → LLM 提取事实 → hash 去重 → 向量库 insert；本图重点是后续 search。", 48, 807, 1310, 18, MUTED, 6)
    d.text("scope", "固定源码 mem0ai/mem0@f8082a73；静态源码示意，不代表所有向量库都提供同样的关键词搜索。", 48, 845, 1330, 16, MUTED, 6)
    d.save(Path(__file__).with_name("scene.excalidraw"))


if __name__ == "__main__":
    main()
