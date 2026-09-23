"""Build a source-to-context evidence braid for GPT Researcher Hybrid mode."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from diagram_style import BLUE, GREEN, INK, MUTED, ORANGE, PURPLE, Scene  # noqa: E402


def ellipse(d: Scene, name: str, x: int, y: int, w: int, h: int, stroke: str, fill: str) -> None:
    e = d._base(name, "ellipse", x, y, w, h)
    e.update(strokeColor=stroke, backgroundColor=fill)
    d.elements.append(e)


def diamond(d: Scene, name: str, x: int, y: int, w: int, h: int, stroke: str, fill: str) -> None:
    e = d._base(name, "diamond", x, y, w, h)
    e.update(strokeColor=stroke, backgroundColor=fill)
    d.elements.append(e)


def main() -> None:
    d = Scene()
    d.text("title", "GPT Researcher：来源怎样进入报告上下文", 34, 23, 1390, 35, INK, 6)
    d.text("subtitle", "Hybrid / 非 DeepResearch 路径；两路并发收集，然后拼接上下文并交给写作器。", 36, 77, 1380, 20, MUTED, 6)

    d.arrow("local-to-context", [(246, 250), (367, 250)], BLUE)
    d.arrow("web-to-context", [(246, 530), (367, 530)], GREEN)
    d.arrow("local-to-join", [(632, 250), (747, 250), (747, 335)], BLUE)
    d.arrow("web-to-join", [(632, 530), (747, 530), (747, 455)], GREEN)
    d.arrow("join-to-state", [(861, 395), (976, 395)], PURPLE)
    d.arrow("state-to-report", [(1108, 452), (1108, 600)], PURPLE)

    ellipse(d, "local", 40, 192, 206, 116, BLUE, "#e6f1ff")
    d.text("local-label", "本地文档\nDocumentLoader", 67, 218, 178, 18, BLUE, 6)
    ellipse(d, "web", 40, 472, 206, 116, GREEN, "#e4f7ea")
    d.text("web-label", "网页检索\nURL → 抓取", 72, 496, 175, 18, GREEN, 6)

    d.box("local-context", 367, 199, 265, 103, BLUE, "#f4f9ff")
    d.text("local-context-label", "压缩 / 格式化\nlocal context", 391, 225, 231, 19, INK, 6)
    d.box("web-context", 367, 479, 265, 103, GREEN, "#f3fcf6")
    d.text("web-context-label", "子查询 · 网页内容\nweb context", 390, 504, 233, 19, INK, 6)

    diamond(d, "join", 688, 335, 173, 120, PURPLE, "#eee7ff")
    d.text("join-label", "拼接\n两路上下文", 719, 360, 135, 19, INK, 6)
    d.box("state", 976, 338, 264, 114, PURPLE, "#f3eeff")
    d.text("state-label", "researcher.context\n可选来源筛选", 998, 361, 235, 19, INK, 6)
    d.box("report", 976, 600, 264, 132, ORANGE, "#fff5e3")
    d.text("report-label", "ReportGenerator\n有上下文 → LLM 写作", 998, 625, 230, 19, INK, 6)

    d.text("parallel-note", "asyncio.gather：两路并发", 482, 381, 285, 18, MUTED, 6)
    d.text("sources-note", "多来源是入口选择；不是每篇报告都会同时用本地、网页、MCP。", 48, 687, 806, 18, MUTED, 6)
    d.box("risk", 40, 765, 1200, 112, "#d56a4c", "#fff1ed")
    d.text("risk-label", "边界：Hybrid 拼接会加固定标签。即使两路内容都空，字符串也可能非空；写作器的“空上下文”保护不能自动证明有证据。", 67, 792, 1140, 17, "#a9422b", 6)
    d.text("footer", "源码：assafelovic/gpt-researcher@6f998577；图为静态路径，未验证生成报告的事实准确性或引用质量。", 42, 908, 1340, 16, MUTED, 6)
    d.save(Path(__file__).with_name("scene.excalidraw"))


if __name__ == "__main__":
    main()
