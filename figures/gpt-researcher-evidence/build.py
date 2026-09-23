"""Build the GPT Researcher Hybrid source-convergence diagram.

The braid is intentionally not a decision tree: local and web contexts are
collected concurrently, then joined before the report-writing path.
"""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from diagram_style import Scene  # noqa: E402


INK = "#14213d"
MUTED = "#475569"
BLUE = "#4a9eed"
GREEN = "#16a34a"
PURPLE = "#8b5cf6"
ORANGE = "#f59e0b"
RED = "#d16b52"


def main() -> None:
    d = Scene()

    # A light boundary groups concurrent collection, not successive stages.
    d.box("concurrent-panel", 36, 158, 646, 418, "#cbd5e1", "#f8fafc")
    d.elements[-1]["strokeStyle"] = "dashed"

    # Connectors sit behind the cards and keep the two source paths distinct.
    d.arrow("local-to-context", [(301, 284), (389, 284)], BLUE)
    d.arrow("web-to-context", [(301, 472), (389, 472)], GREEN)
    d.arrow("local-to-join", [(647, 284), (711, 284), (711, 339), (754, 339)], BLUE)
    d.arrow("web-to-join", [(647, 472), (711, 472), (711, 415), (754, 415)], GREEN)
    d.arrow("join-to-state", [(942, 378), (1000, 378)], PURPLE)
    d.arrow("state-to-report", [(1120, 438), (1120, 558)], ORANGE)

    d.box("local-source", 65, 231, 236, 106, BLUE, "#a5d8ff")
    d.box("local-context", 389, 231, 258, 106, BLUE, "#e6f3ff")
    d.box("web-source", 65, 419, 236, 106, GREEN, "#c3fae8")
    d.box("web-context", 389, 419, 258, 106, GREEN, "#e8fbf2")
    d.box("hybrid-join", 754, 315, 188, 126, PURPLE, "#d8c8ff")
    d.box("research-context", 1000, 318, 241, 120, PURPLE, "#f0e9ff")
    d.box("report-writer", 1000, 558, 241, 124, ORANGE, "#fff3bf")
    d.box("risk", 36, 728, 1205, 108, RED, "#fff0e9")

    # Code/Comic Shanns is shared with the recent project figures. Chinese
    # glyphs use the renderer's fallback font and are checked in PNG and SVG.
    d.text("title", "GPT Researcher：来源如何进入报告上下文", 42, 24, 1190, 34, INK, 8)
    d.text("subtitle", "Hybrid 普通研究：本地与网页并发形成上下文，再交给写作器。", 44, 78, 1180, 20, MUTED, 8)
    d.text("concurrent-label", "asyncio.gather · 两路并发", 64, 176, 555, 21, MUTED, 8)

    d.text("local-source-label", "本地文档\nDocumentLoader", 87, 251, 210, 22, INK, 8)
    d.text("local-context-label", "压缩 / 格式化\nlocal context", 412, 251, 224, 22, INK, 8)
    d.text("web-source-label", "网页检索\nURL → 抓取", 87, 439, 210, 22, INK, 8)
    d.text("web-context-label", "子查询 · 网页内容\nweb context", 412, 439, 224, 22, INK, 8)

    d.text("join-label", "Hybrid 拼接\n两路上下文", 773, 342, 164, 23, INK, 8)
    d.text("state-label", "researcher.context\n可选来源筛选", 1019, 342, 212, 19, INK, 8)
    d.text("writer-edge", "write_report()", 961, 493, 225, 18, ORANGE, 8)
    d.text("report-label", "ReportGenerator\n上下文 → LLM 写作", 1019, 582, 212, 21, INK, 8)

    d.text("risk-label", "关键边界：Hybrid 拼接会加固定标签；即使双路正文都空，字符串仍可能非空。\n写作器的“空上下文”保护不能单独证明有来源证据。", 63, 748, 1150, 20, "#9a402f", 8)

    for element in d.elements:
        if element["type"] in {"rectangle", "arrow"}:
            element["roughness"] = 1
        if element["type"] == "arrow":
            element["strokeWidth"] = 3

    d.save(Path(__file__).with_name("scene.excalidraw"))


if __name__ == "__main__":
    main()
