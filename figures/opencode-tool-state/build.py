"""Build the editable OpenCode ToolPart and SessionStatus diagram.

The vertical state graph stays readable in the A4 book and on phones.
Its lower strip names a separate session-level status, not another ToolPart node.
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
    amber = "#d58b00"
    green = "#159447"
    red = "#d93640"

    # A ToolPart follows one callID. SessionStatus belongs to the whole session.
    d.box("toolpart-panel", 20, 79, 710, 575, "#bfd5f5", "#f7faff")
    d.box("session-panel", 20, 678, 710, 162, "#cbd5e1", "#f8fafc")

    # Main progression, followed by two alternative terminal states.
    d.arrow("start-to-pending", [(106, 207), (230, 207)], blue)
    d.arrow("pending-to-running", [(365, 257), (365, 318)], amber)
    d.arrow("running-to-completed", [(315, 417), (191, 509)], green)
    d.arrow("running-to-error", [(415, 417), (537, 509)], red)

    # Pending can fail during cleanup without passing through running.
    d.arrow("pending-cleanup-to-error", [(500, 206), (685, 206), (685, 559), (668, 559)], red)
    d.elements[-1]["strokeStyle"] = "dashed"

    dot(d, "start-dot", 83, 195, 24, blue)
    d.box("pending", 230, 157, 270, 100, blue, "#a5d8ff")
    d.box("running", 230, 318, 270, 99, amber, "#fff3bf")
    d.box("completed", 52, 509, 278, 110, green, "#c3fae8")
    d.box("error", 392, 509, 276, 110, red, "#ffe3e3")

    # Short labels stay in the image; event details and edge cases are in README.
    d.text("title", "OpenCode：工具进度与会话状态", 26, 22, 678, 31, ink, 8)
    d.text("panel-title", "一次调用的记录 · ToolPart / callID", 43, 97, 580, 24, "#2563a6", 8)
    d.text("event-input", "接收参数\ntool-input-*", 46, 144, 180, 20, "#2563a6", 8)
    d.text("event-call", "完整调用到达\ntool-call", 395, 261, 155, 20, "#9a6700", 8)
    d.text("event-success", "收到成功结果", 92, 461, 176, 23, "#166534", 8)
    d.text("event-failure", "工具报错", 509, 451, 154, 19, "#b42332", 8)
    d.text("pending-cleanup-label", "收尾清理\npending\nrunning", 565, 267, 110, 20, "#b42332", 8, align="center")

    d.text("pending-label", "接收工具输入\npending", 253, 174, 222, 27, ink, 8)
    d.text("running-label", "等执行结果\nrunning", 253, 335, 222, 27, ink, 8)
    d.text("completed-label", "记录成功输出\ncompleted", 72, 526, 245, 26, ink, 8)
    d.text("error-label", "记录错误／中断\nerror", 412, 526, 244, 26, ink, 8)

    d.text("session-title", "整个会话的状态 · SessionStatus", 44, 696, 600, 24, muted, 8)
    d.text("session-states", "忙碌 busy  /  重试 retry  /  空闲 idle", 44, 744, 624, 27, ink, 8)
    d.text("session-retry", "模型回复流出错，策略允许且未超限 → retry", 44, 790, 640, 23, muted, 8)

    # Append the second cleanup branch last to preserve existing element seeds.
    d.arrow("running-cleanup-to-error", [(500, 367), (708, 367), (708, 587), (668, 587)], red)
    d.elements[-1]["strokeStyle"] = "dashed"

    for element in d.elements:
        if element["type"] in {"rectangle", "arrow", "ellipse"}:
            element["roughness"] = 1
        if element["type"] == "arrow":
            element["strokeWidth"] = 3

    d.save(Path(__file__).resolve().parent / "scene.excalidraw")


if __name__ == "__main__":
    build()
