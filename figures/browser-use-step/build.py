"""Generate the editable browser-use step sequence diagram."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from diagram_style import INK, MUTED, Scene  # noqa: E402


def lifeline(scene: Scene, name: str, x: int, y0: int, y1: int) -> None:
    scene.arrow(name, [(x, y0), (x, y1)], "#c5d1dd")
    scene.elements[-1].update(strokeStyle="dashed", strokeWidth=1, endArrowhead=None)


def exchange(scene: Scene, name: str, x0: int, x1: int, y: int, label: str, color: str, label_x: int, label_w: int) -> None:
    scene.arrow(name, [(x0, y), (x1, y)], color)
    scene.elements[-1]["strokeWidth"] = 2
    scene.text(name + "-label", label, label_x, y - 31, label_w, 16, color, 8)


def build() -> None:
    d = Scene()
    navy = "#284d76"
    teal = "#137b86"
    purple = "#7152a4"
    orange = "#ab6519"
    green = "#267d56"

    # Lifelines make ordering explicit; the labels, not color alone, carry meaning.
    for name, x in (("agent", 135), ("browser", 390), ("model", 645), ("history", 900)):
        lifeline(d, name + "-lifeline", x, 170, 733)

    exchange(d, "request-state", 135, 390, 220, "get_browser_state_summary", navy, 158, 250)
    exchange(d, "state-summary", 390, 135, 300, "BrowserStateSummary", teal, 178, 210)
    exchange(d, "model-input", 135, 645, 380, "create_state_messages → LLM", purple, 260, 360)
    exchange(d, "model-output", 645, 135, 460, "AgentOutput.action", purple, 332, 230)
    exchange(d, "execute-actions", 135, 390, 540, "multi_act → Tools.act", orange, 160, 245)
    exchange(d, "action-result", 390, 135, 620, "ActionResult", orange, 230, 155)
    exchange(d, "write-history", 135, 900, 700, "_finalize → AgentHistory", green, 410, 275)

    d.box("agent-head", 40, 117, 190, 53, navy, "#eaf2fb")
    d.box("browser-head", 295, 117, 190, 53, teal, "#e7f6f4")
    d.box("model-head", 550, 117, 190, 53, purple, "#f0eafb")
    d.box("history-head", 805, 117, 190, 53, green, "#eaf5ec")
    d.text("agent-name", "Agent.step", 62, 129, 155, 19, INK, 8)
    d.text("browser-name", "Browser + Tools", 308, 129, 170, 19, INK, 8)
    d.text("model-name", "模型", 610, 129, 100, 19, INK, 6)
    d.text("history-name", "History", 857, 129, 120, 19, INK, 8)

    d.text("title", "browser-use · 一轮 step 的观察—行动时序", 35, 24, 1015, 34, INK, 6)
    d.text("subtitle", "沿时间向下读。横向箭头是请求或结果；四条泳道分别负责控制、网页、决策与留痕。", 37, 70, 1000, 18, MUTED, 6)
    d.text("timeline", "时间 ↓", 17, 181, 93, 16, MUTED, 6)

    d.box("screenshot-note", 39, 769, 956, 91, "#c7d6e9", "#f8fbff")
    d.text("screenshot-title", "截图 ≠ 模型必定看图", 59, 782, 370, 21, navy, 6)
    d.text("screenshot-detail", "采集请求 include_screenshot=True   ·   模型消息由 use_vision 决定   ·   历史有截图时才保存路径", 59, 817, 900, 17, INK, 6)
    d.text("footer", "静态源码图 · browser-use/browser-use@d8110c5 · _finalize 只有在有 last_result 时才记历史", 40, 880, 980, 15, MUTED, 6)
    d.save(Path(__file__).resolve().parent / "scene.excalidraw")


if __name__ == "__main__":
    build()
