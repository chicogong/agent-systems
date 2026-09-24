"""Generate MiMo Code's two-stage checkpoint / rebuild diagram."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from diagram_style import Scene  # noqa: E402

INK = "#172033"
MUTED = "#4b5b70"
BLUE = "#3478e5"
PURPLE = "#7653d8"
GREEN = "#23845a"
ORANGE = "#b96a10"


def card(d, name, title, detail, x, y, w, h, stroke, fill):
    d.box(name, x, y, w, h, stroke, fill)
    d.text(name + "-title", title, x + 16, y + 16, w - 32, 27, INK, 8)
    d.text(name + "-detail", detail, x + 16, y + 64, w - 32, 23, MUTED, 8)


def main():
    d = Scene()
    d.text("title", "MiMo Code：先写状态，再换窗口", 36, 25, 860, 35, INK, 8)
    d.text("subtitle", "checkpoint 由阈值触发；重建由溢出触发。", 38, 78, 850, 23, MUTED, 8)

    d.box("write-stage", 30, 142, 890, 284, "#a7c9f4", "#f4f8ff")
    d.text("write-heading", "① 提前写入 · 主 Agent 继续工作", 54, 158, 810, 28, BLUE, 8)
    card(d, "threshold", "跨阈值", "已完成回复的 token", 54, 235, 246, 118, BLUE, "#ffffff")
    card(d, "writer", "独立 writer", "后台 child session", 352, 235, 246, 118, PURPLE, "#ffffff")
    card(d, "file", "结构化文件", "成功 → watermark", 650, 235, 246, 118, PURPLE, "#ffffff")
    d.arrow("trigger", [(300, 294), (352, 294)], BLUE)
    d.arrow("persist", [(598, 294), (650, 294)], PURPLE)
    d.text("file-foot", "checkpoint.md；必要时更新项目 MEMORY.md", 54, 374, 800, 23, MUTED, 8)

    d.box("rebuild-stage", 30, 456, 890, 448, "#d5c6a5", "#fffaf2")
    d.text("rebuild-heading", "② 溢出时 · 检查可用 checkpoint", 54, 472, 810, 28, ORANGE, 8)
    d.box("overflow", 285, 546, 380, 80, BLUE, "#ffffff")
    d.text("overflow-text", "主 Agent 上下文溢出", 308, 565, 332, 27, INK, 8)

    d.arrow("decision-stem", [(475, 626), (475, 669)], ORANGE)
    d.arrow("success-edge", [(475, 669), (250, 669), (250, 707)], GREEN)
    d.arrow("fallback-edge", [(475, 669), (700, 669), (700, 707)], ORANGE)
    card(d, "success", "已有可用状态", "重建边界 → 继续", 54, 707, 390, 124, GREEN, "#eff9f2")
    card(d, "fallback", "没有可用状态", "现场等待 writer", 506, 707, 390, 124, ORANGE, "#fff4e6")
    d.text("fallback-foot", "仍失败 / 超时 / 禁用写入", 506, 844, 390, 23, ORANGE, 8)
    d.text("fallback-foot2", "→ compaction 边界", 506, 872, 390, 23, ORANGE, 8)

    for element in d.elements:
        if element["type"] == "rectangle":
            element["roughness"] = 1
        elif element["type"] == "arrow":
            element.update(roughness=1, strokeWidth=3)

    d.save(Path(__file__).with_name("scene.excalidraw"))


if __name__ == "__main__":
    main()
