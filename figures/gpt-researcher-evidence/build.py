"""Build the fixed-version Hybrid source flow, with loading before gather."""

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
ORANGE = "#d58916"
RED = "#b85b48"


def main() -> None:
    d = Scene()
    d.box("gather-region", 285, 113, 385, 387, "#bac7d8", "#f8fafc")
    d.elements[-1]["strokeStyle"] = "dashed"

    d.arrow("loaded-docs", [(250, 226), (315, 226)], BLUE)
    d.arrow("empty-docs", [(250, 405), (315, 405)], GREEN)
    d.arrow("local-context-join", [(640, 226), (687, 226), (687, 272), (717, 272)], BLUE)
    d.arrow("web-context-join", [(640, 405), (687, 405), (687, 334), (717, 334)], GREEN)
    d.arrow("join-state", [(862, 301), (880, 301), (880, 251), (895, 251)], PURPLE)
    d.arrow("state-report", [(975, 298), (975, 390)], ORANGE)

    d.box("loader", 30, 171, 220, 110, BLUE, "#e6f3ff")
    d.box("empty-input", 30, 355, 220, 100, GREEN, "#e8fbf2")
    d.box("local-context", 315, 171, 325, 110, BLUE, "#dcedff")
    d.box("web-context", 315, 350, 325, 110, GREEN, "#d9f8e8")
    d.box("hybrid-join", 717, 240, 145, 125, PURPLE, "#e9ddff")
    d.box("research-context", 900, 198, 150, 100, PURPLE, "#f2ecff")
    d.box("report-writer", 900, 390, 150, 100, ORANGE, "#fff3d6")
    d.box("empty-boundary", 717, 525, 333, 78, RED, "#fff6f3")

    d.text("heading", "Hybrid：先加载，再并发形成两路 context", 30, 26, 1020, 28, INK, 8)
    d.text("load-phase", "① 文档加载完成", 32, 112, 230, 20, MUTED, 8)
    d.text("gather-label", "② asyncio.gather · 两路并发", 307, 126, 338, 20, MUTED, 8)
    d.text("loader-label", "DocumentLoader\n或在线加载器\n加载文档", 47, 183, 190, 21, INK, 8)
    d.text("empty-label", "空文档输入 []\n走网页检索", 48, 373, 183, 22, INK, 8)
    d.text("local-label", "文档非空时：用文档\n空文档可回退网页\n→ local context", 337, 184, 278, 22, INK, 8)
    d.text("web-label", "子查询 · URL · 抓取\n→ web context", 337, 371, 278, 23, INK, 8)
    d.text("join-label", "Hybrid 拼接\n加固定标签", 732, 263, 120, 21, INK, 8)
    d.text("state-label", "researcher.\ncontext\n可选筛选", 911, 210, 130, 20, INK, 8)
    d.text("report-label", "Report\nGenerator\n→ LLM 写作", 910, 400, 133, 20, INK, 8)
    d.text("report-edge", "写报告", 879, 337, 80, 20, ORANGE, 8)
    d.text("risk", "边界：双路正文皆空时，\n固定标签仍可使拼接结果非空", 733, 539, 305, 20, RED, 8)

    for element in d.elements:
        if element["type"] in {"rectangle", "arrow"}:
            element["roughness"] = 1
        if element["type"] == "arrow":
            element["strokeWidth"] = 3

    d.save(Path(__file__).with_name("scene.excalidraw"))


if __name__ == "__main__":
    main()
