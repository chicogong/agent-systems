"""Build the native OpenCode ToolPart state-machine scene.

The shared Scene helper emits editable Excalidraw elements; this diagram uses a
single flow/fork, intentionally different from the Pi layer diagrams.
"""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from diagram_style import INK, MUTED, Scene  # noqa: E402


def dot(scene: Scene, name: str, x: int, y: int, diameter: int, color: str) -> None:
    element = scene._base(name, "ellipse", x, y, diameter, diameter)
    element.update(strokeColor=color, backgroundColor=color, strokeWidth=1)
    scene.elements.append(element)


def build() -> None:
    d = Scene()
    blue = "#2463a6"
    amber = "#b77010"
    green = "#21845c"
    red = "#b7464b"
    gray = "#637286"

    # Draw connectors first so they sit behind the state labels.
    d.arrow("begin-to-pending", [(104, 285), (177, 285)], blue)
    d.arrow("pending-to-running", [(425, 285), (542, 285)], amber)
    d.arrow("running-to-completed", [(787, 262), (860, 262), (860, 204), (905, 204)], green)
    d.arrow("running-to-error", [(787, 307), (860, 307), (860, 405), (905, 405)], red)

    dot(d, "start-dot", 72, 269, 32, blue)
    d.box("pending", 177, 230, 248, 110, blue, "#e9f3ff")
    d.box("running", 542, 230, 245, 110, amber, "#fff1d8")
    d.box("completed", 905, 150, 280, 110, green, "#e6f6eb")
    d.box("error", 905, 350, 280, 110, red, "#fff0ef")

    d.text("title", "OpenCode · 一次工具调用的状态变化", 62, 30, 1145, 36, INK, 6)
    d.text("subtitle", "同一个 callID 对应一个 ToolPart；成功与失败是分叉，不是两个连续步骤。", 64, 80, 1120, 19, MUTED, 6)
    d.text("pending-label", "pending\n输入尚未成为完整调用", 197, 250, 210, 20, INK, 8)
    d.text("running-label", "running\n参数已形成，等待结果", 562, 250, 210, 20, INK, 8)
    d.text("completed-label", "completed\n输出 / 元数据 / 结束时间", 925, 170, 245, 20, INK, 8)
    d.text("error-label", "error\n错误 / 结束时间", 925, 370, 245, 20, INK, 8)

    d.text("first-event", "tool-input-*", 111, 205, 154, 17, blue, 8)
    d.text("second-event", "tool-call", 425, 205, 112, 17, amber, 8)
    d.text("success-event", "tool-result 成功", 795, 163, 116, 15, green, 6)
    d.text("failure-event", "失败结果 / tool-error\n或中断清理", 630, 357, 210, 14, red, 6)

    d.box("session-strip", 63, 516, 1122, 83, "#d1d9e3", "#f7f9fc")
    d.text("session-title", "另一层：SessionStatus", 84, 533, 290, 19, gray, 6)
    d.text("session-states", "busy  /  retry  /  idle", 418, 533, 400, 20, INK, 8)
    d.text("session-note", "描述整个会话；不是 ToolPart 的状态", 838, 535, 315, 16, MUTED, 6)
    d.text("footer", "静态源码图 · anomalyco/opencode@18ef3cc7 · 未做运行轨迹验证", 64, 624, 1120, 16, MUTED, 6)
    d.save(Path(__file__).resolve().parent / "scene.excalidraw")


if __name__ == "__main__":
    build()
