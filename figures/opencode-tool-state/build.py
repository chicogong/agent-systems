"""Build an editable OpenCode ToolPart state-machine scene.

The state graph follows the pinned source. Only the visual language borrows
from the hand-drawn, saturated Excalidraw references; it is not a layer chart.
"""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from diagram_style import Scene  # noqa: E402


def dot(scene: Scene, name: str, x: int, y: int, diameter: int, color: str) -> None:
    element = scene._base(name, "ellipse", x, y, diameter, diameter)
    element.update(strokeColor=color, backgroundColor=color, strokeWidth=1)
    scene.elements.append(element)


def build() -> None:
    d = Scene()
    ink = "#14213d"
    muted = "#475569"
    blue = "#4a9eed"
    amber = "#f59e0b"
    green = "#16a34a"
    red = "#ef4444"

    # A ToolPart is the state-machine subject. SessionStatus is deliberately
    # outside this panel because it describes the whole session.
    d.box("toolpart-panel", 40, 154, 1220, 456, "#bfd5f5", "#f7faff")
    d.box("session-panel", 40, 640, 1220, 142, "#cbd5e1", "#f8fafc")

    # Connectors are behind their labels; completed and error are alternatives.
    d.arrow("start-to-pending", [(106, 368), (173, 368)], blue)
    d.arrow("pending-to-running", [(443, 368), (535, 368)], amber)
    d.arrow("running-to-completed", [(807, 333), (857, 333), (857, 290), (922, 290)], green)
    d.arrow("running-to-error", [(807, 404), (857, 404), (857, 485), (922, 485)], red)
    d.arrow("pending-cleanup-to-error", [(308, 434), (308, 573), (1064, 573), (1064, 547)], red)
    d.elements[-1]["strokeStyle"] = "dashed"

    dot(d, "start-dot", 76, 353, 30, blue)
    d.box("pending", 173, 302, 270, 132, blue, "#a5d8ff")
    d.box("running", 535, 302, 272, 132, amber, "#fff3bf")
    d.box("completed", 922, 228, 285, 124, green, "#c3fae8")
    d.box("error", 922, 423, 285, 124, red, "#ffe3e3")

    # Font 8 is Excalidraw's Code/Comic Shanns face used in call-path.
    d.text("title", "OpenCode：一次工具调用，如何走到结果？", 50, 25, 1200, 34, ink, 8)
    d.text("subtitle", "沿一个 callID 看 ToolPart；成功与失败在同一步分叉。", 52, 80, 1180, 19, muted, 8)
    d.text("panel-title", "ToolPart · 一个对象的状态轨迹", 73, 177, 880, 23, "#2563a6", 8)
    d.text("event-input", "tool-input-*", 105, 257, 160, 17, "#2563a6", 8)
    d.text("event-call", "tool-call", 440, 257, 150, 17, "#9a6700", 8)
    d.text("event-success", "tool-result 成功", 866, 189, 260, 17, "#166534", 8)
    d.text("event-failure", "失败结果 / tool-error / 清理", 845, 389, 335, 16, "#b42332", 8)
    d.text("pending-cleanup-label", "清理未收束的 pending", 420, 541, 400, 18, "#b42332", 8)

    d.text("pending-label", "pending\n输入尚未完整", 198, 331, 232, 21, ink, 8)
    d.text("running-label", "running\n参数已形成，等待结果", 560, 331, 236, 21, ink, 8)
    d.text("completed-label", "completed\n输出 · 元数据\n结束时间", 947, 245, 248, 20, ink, 8)
    d.text("error-label", "error\n错误 · 结束时间", 947, 451, 248, 21, ink, 8)

    d.text("session-title", "另一层 · SessionStatus", 73, 658, 460, 23, muted, 8)
    d.text("session-states", "busy  /  retry  /  idle", 76, 704, 600, 23, ink, 8)
    d.text("session-note", "描述整个会话；不是 ToolPart 的完成状态", 700, 709, 500, 18, muted, 8)

    for element in d.elements:
        if element["type"] in {"rectangle", "arrow", "ellipse"}:
            element["roughness"] = 1
        if element["type"] == "arrow":
            element["strokeWidth"] = 3

    d.save(Path(__file__).resolve().parent / "scene.excalidraw")


if __name__ == "__main__":
    build()
