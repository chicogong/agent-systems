"""Generate the editable browser-use step sequence diagram."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from diagram_style import INK, MUTED, Scene  # noqa: E402


def lifeline(scene: Scene, name: str, x: int) -> None:
    scene.arrow(name, [(x, 139), (x, 603)], "#c5d1dd")
    scene.elements[-1].update(strokeStyle="dashed", strokeWidth=1, endArrowhead=None)


def exchange(scene: Scene, name: str, x0: int, x1: int, y: int,
             label: str, color: str, label_x: int, label_w: int) -> None:
    scene.arrow(name, [(x0, y), (x1, y)], color)
    scene.elements[-1].update(strokeWidth=3, roughness=1)
    scene.text(name + "-label", label, label_x, y - 52, label_w, 18, color, 8)


def build() -> None:
    d = Scene()
    navy = "#3478d4"
    teal = "#06a6b4"
    purple = "#8b5cf6"
    orange = "#f59e0b"
    green = "#16a34a"

    d.text("title", "Browser Use：看网页、执行动作、记下结果", 30, 20, 840, 29, INK, 8)
    d.text("timeline", "时间 ↓", 18, 140, 90, 19, MUTED, 8)

    lanes = (
        ("agent", 115, "运行这一轮\nAgent.step", 30, 170, navy, "#a5d8ff"),
        ("browser", 345, "浏览器与工具\nBrowser + Tools", 245, 200, teal, "#c3fae8"),
        ("model", 575, "选择动作\n模型", 490, 170, purple, "#d0bfff"),
        ("history", 805, "保存记录\nAgentHistory", 720, 170, green, "#d3f9d8"),
    )
    for name, x, label, left, width, color, fill in lanes:
        lifeline(d, name + "-lifeline", x)
        d.box(name + "-head", left, 72, width, 67, color, fill)
        d.text(name + "-name", label, left + 13, 81, width - 26, 18, INK, 8, align="center")

    exchange(d, "request-state", 115, 345, 201, "请求当前网页\nget_browser_state_summary", navy, 128, 275)
    exchange(d, "state-summary", 345, 115, 253, "返回网页摘要\nBrowserStateSummary", teal, 130, 248)
    d.elements[-1]["y"] += 9
    exchange(d, "model-input", 115, 575, 319, "整理消息，询问模型\ncreate_state_messages → LLM", purple, 198, 355)
    exchange(d, "model-output", 575, 115, 385, "交回动作列表\nAgentOutput.action", purple, 265, 244)
    exchange(d, "execute-actions", 115, 345, 451, "逐项执行动作\nmulti_act → Tools.act", orange, 128, 250)
    exchange(d, "action-result", 345, 115, 517, "返回动作结果\nActionResult", orange, 175, 175)
    exchange(d, "write-history", 115, 805, 583, "有动作结果和网页摘要时，保存本轮\n_finalize → AgentHistory", green, 286, 500)

    d.box("screenshot-note", 30, 621, 860, 122, "#9dbfe8", "#f4f9ff")
    d.text("screenshot-title", "请求截图 · include_screenshot=True", 47, 635, 820, 19, "#2563a6", 8)
    d.text("screenshot-detail", "模型按 use_vision 选截图；历史仅在有截图时存路径\n出错、任务结束／序列停止、地址或焦点变化 → 停止余下动作", 47, 673, 820, 18, INK, 8)

    for element in d.elements:
        if element["type"] == "rectangle":
            element["roughness"] = 1
    d.save(Path(__file__).resolve().parent / "scene.excalidraw")


if __name__ == "__main__":
    build()
