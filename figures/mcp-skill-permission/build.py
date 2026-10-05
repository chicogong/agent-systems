"""Build the editable diagram for the Skill / MCP / permission boundary."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from diagram_style import Scene, INK, MUTED  # noqa: E402

BLUE = "#3578e5"
PURPLE = "#8056e8"
GREEN = "#2fa86a"
AMBER = "#e88816"
RED = "#bf5c49"


def main() -> None:
    d = Scene()
    d.text("title", "从操作方法到工具调用，再到结果检查", 35, 22, 1090, 34, INK, 6)
    d.text("subtitle", "Skill 提供方法，MCP 列出工具；宿主检查许可，执行后按任务核对结果。", 37, 76, 1080, 19, MUTED)

    for name, x, y, w, h, stroke, fill in [
        ("skill", 38, 134, 212, 112, PURPLE, "#f0eaff"),
        ("scope", 325, 134, 212, 112, BLUE, "#eaf3ff"),
        ("discover", 612, 134, 252, 112, GREEN, "#e7f7ee"),
        ("proposal", 38, 325, 212, 137, PURPLE, "#f0eaff"),
        ("gate", 325, 325, 212, 137, AMBER, "#fff4df"),
        ("execution", 612, 325, 212, 137, GREEN, "#e7f7ee"),
        ("verify", 899, 325, 212, 137, BLUE, "#eaf3ff"),
        ("denied", 325, 535, 212, 82, RED, "#fff0e9"),
    ]:
        d.box(name, x, y, w, h, stroke, fill)

    for name, points, color, dashed in [
        ("skill-informs", [(144, 246), (144, 325)], PURPLE, True),
        ("scope-bounds", [(431, 246), (431, 325)], BLUE, True),
        ("discover-offers", [(612, 190), (569, 190), (569, 284), (500, 284), (500, 325)], GREEN, True),
        ("proposal-to-gate", [(250, 394), (325, 394)], PURPLE, False),
        ("gate-to-execution", [(537, 394), (612, 394)], AMBER, False),
        ("execution-to-verify", [(824, 394), (899, 394)], GREEN, False),
        ("gate-to-denied", [(431, 462), (431, 535)], RED, True),
    ]:
        d.arrow(name, points, color)
        if dashed:
            d.elements[-1]["strokeStyle"] = "dashed"

    for name, value, x, y, w, size, color in [
        ("skill-title", "Skill · 方法", 54, 151, 185, 23, INK),
        ("skill-detail", "说明该怎样做\n例如先核对原文", 54, 189, 185, 19, MUTED),
        ("scope-title", "用户任务 · 范围", 341, 151, 185, 23, INK),
        ("scope-detail", "可读与可改的范围\n结果应满足的要求", 341, 189, 185, 19, MUTED),
        ("discover-title", "MCP · 工具列表", 628, 151, 225, 23, INK),
        ("discover-detail", "tools/list\n例如 kb.fetch", 628, 189, 225, 19, MUTED),
        ("proposal-title", "模型提出下一步", 54, 344, 185, 23, INK),
        ("proposal-detail", "建议查文档、改文件\n等待检查后执行", 54, 386, 185, 19, MUTED),
        ("gate-title", "宿主检查并路由", 341, 344, 185, 23, INK),
        ("gate-detail", "任务范围 · 工具策略\n必要时请用户批准", 341, 386, 185, 19, MUTED),
        ("execution-title", "工具实际执行", 628, 344, 185, 23, INK),
        ("execution-detail", "MCP: tools/call\n本地: 编辑文件\n保留结果 / 错误", 628, 386, 185, 19, MUTED),
        ("verify-title", "核对任务结果", 915, 344, 185, 23, INK),
        ("verify-detail", "核对原文与 diff\n检查测试结果\n再写交付结论", 915, 386, 185, 19, MUTED),
        ("denied-title", "拒绝：动作未执行", 341, 548, 185, 22, RED),
        ("denied-detail", "说明该动作未完成", 341, 585, 185, 19, MUTED),
        ("edge-note", "发现工具后仍要检查许可；\n调用返回后仍要核对任务结果。", 590, 565, 535, 19, MUTED),
    ]:
        d.text(name, value, x, y, w, size, color)

    for element in d.elements:
        if element["type"] in {"rectangle", "arrow"}:
            element["roughness"] = 1
        if element["type"] == "arrow":
            element["strokeWidth"] = 3
    d.save(ROOT / "figures/mcp-skill-permission/scene.excalidraw")


if __name__ == "__main__":
    main()
