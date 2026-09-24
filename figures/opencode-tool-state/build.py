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
    d.text("title", "一次工具调用的两层状态", 26, 22, 678, 31, ink, 8)
    d.text("panel-title", "ToolPart · 同一个 callID", 43, 97, 580, 24, "#2563a6", 8)
    d.text("event-input", "tool-input-*", 46, 160, 180, 23, "#2563a6", 8)
    d.text("event-call", "tool-call", 395, 277, 155, 23, "#9a6700", 8)
    d.text("event-success", "成功结果", 92, 461, 176, 23, "#166534", 8)
    d.text("event-failure", "失败结果", 507, 424, 140, 23, "#b42332", 8)
    d.text("pending-cleanup-label", "清理未收束的\npending", 516, 239, 161, 23, "#b42332", 8)

    d.text("pending-label", "pending\n输入未完整", 253, 174, 222, 27, ink, 8)
    d.text("running-label", "running\n等待结果", 253, 335, 222, 27, ink, 8)
    d.text("completed-label", "completed\n输出 · 元数据", 72, 526, 245, 26, ink, 8)
    d.text("error-label", "error\n错误 · 结束时间", 412, 526, 244, 26, ink, 8)

    d.text("session-title", "SessionStatus · 会话层", 44, 696, 600, 24, muted, 8)
    d.text("session-states", "busy  /  retry  /  idle", 44, 744, 624, 27, ink, 8)
    d.text("session-retry", "retry：可重试的模型流错误，且未超限", 44, 790, 640, 23, muted, 8)

    for element in d.elements:
        if element["type"] in {"rectangle", "arrow", "ellipse"}:
            element["roughness"] = 1
        if element["type"] == "arrow":
            element["strokeWidth"] = 3

    d.save(Path(__file__).resolve().parent / "scene.excalidraw")


if __name__ == "__main__":
    build()
