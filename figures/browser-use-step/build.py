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
    scene.text(name + "-label", label, label_x, y - 31, label_w, 19, color, 8)


def build() -> None:
    d = Scene()
    navy = "#3478d4"
    teal = "#06a6b4"
    purple = "#8b5cf6"
    orange = "#f59e0b"
    green = "#16a34a"

    d.text("title", "browser-use · 一轮 step 的观察—行动时序", 30, 20, 840, 29, INK, 8)
    d.text("timeline", "时间 ↓", 18, 140, 90, 19, MUTED, 8)

    lanes = (
        ("agent", 115, "Agent.step", 30, 170, navy, "#a5d8ff"),
        ("browser", 345, "Browser + Tools", 245, 200, teal, "#c3fae8"),
        ("model", 575, "模型", 490, 170, purple, "#d0bfff"),
        ("history", 805, "History", 720, 170, green, "#d3f9d8"),
    )
    for name, x, label, left, width, color, fill in lanes:
        lifeline(d, name + "-lifeline", x)
        d.box(name + "-head", left, 85, width, 54, color, fill)
        d.text(name + "-name", label, left + 13, 101, width - 26, 20, INK, 8)

    exchange(d, "request-state", 115, 345, 187, "get_browser_state_summary", navy, 128, 275)
    exchange(d, "state-summary", 345, 115, 253, "BrowserStateSummary", teal, 130, 248)
    exchange(d, "model-input", 115, 575, 319, "create_state_messages → LLM", purple, 198, 355)
    exchange(d, "model-output", 575, 115, 385, "AgentOutput.action", purple, 265, 244)
    exchange(d, "execute-actions", 115, 345, 451, "multi_act → Tools.act", orange, 128, 250)
    exchange(d, "action-result", 345, 115, 517, "ActionResult", orange, 175, 175)
    exchange(d, "write-history", 115, 805, 583, "_finalize → AgentHistory（有 last_result 时）", green, 286, 500)

    d.box("screenshot-note", 30, 621, 860, 96, "#9dbfe8", "#f4f9ff")
    d.text("screenshot-title", "截图采集：include_screenshot=True", 47, 635, 430, 19, "#2563a6", 8)
    d.text("screenshot-detail", "模型是否看图：use_vision；历史仅在有截图时存路径", 47, 673, 820, 19, INK, 8)

    for element in d.elements:
        if element["type"] == "rectangle":
            element["roughness"] = 1
    d.save(Path(__file__).resolve().parent / "scene.excalidraw")


if __name__ == "__main__":
    build()
