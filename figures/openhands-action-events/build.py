"""Build OpenHands' ActionEvent/ObservationEvent swimlane as native Excalidraw."""

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from diagram_style import Scene  # noqa: E402


INK = "#243042"
MUTED = "#647084"
BLUE = "#3877c8"
PURPLE = "#7455bd"
AMBER = "#b87916"
GREEN = "#228668"


def stroke(scene: Scene, name: str, pts: list[tuple[int, int]], color: str,
           dashed: bool = False, arrow: bool = True):
    scene.arrow(name, pts, color)
    shape = scene.elements[-1]
    shape["strokeWidth"] = 2 if dashed else 3
    shape["strokeStyle"] = "dashed" if dashed else "solid"
    shape["endArrowhead"] = "arrow" if arrow else None


def message(scene: Scene, name: str, y: int, x1: int, x2: int,
            label: str, color: str, dashed: bool = False,
            lx: int | None = None, lw: int | None = None):
    stroke(scene, name, [(x1, y), (x2, y)], color, dashed)
    left = lx if lx is not None else min(x1, x2) + 24
    width = lw if lw is not None else abs(x2 - x1) - 48
    scene.text(f"{name}-label", label, left, y - 46, width, 24, color, 6)


def build():
    d = Scene()
    d.text("title", "OpenHands：动作先入账，结果后到达", 48, 23, 1200, 36, INK, 6)
    d.text("subtitle", "LocalConversation.run() + 默认 Agent.step() 的一次工具调用", 50, 77, 1190, 24, MUTED, 6)

    lanes = [
        (70, 170, "LocalConversation", BLUE, "#f1f7fe"),
        (380, 480, "Agent", PURPLE, "#f7f3fd"),
        (690, 790, "Tool", GREEN, "#f0faf6"),
        (1000, 1100, "EventLog", AMBER, "#fffaee"),
    ]
    for idx, (x, cx, title, color, fill) in enumerate(lanes):
        d.box(f"lane-{idx}", x, 150, 200, 840, color, fill)
        d.elements[-1]["strokeWidth"] = 2
        d.elements[-1]["roughness"] = 1
        d.elements[-1]["opacity"] = 80
        lane_title = "Local\nConversation" if idx == 0 else title
        d.text(f"lane-{idx}-title", lane_title, x + 14, 170, 175,
               24, color, 8)
        stroke(d, f"lane-{idx}-line", [(cx, 221), (cx, 960)], color,
               dashed=True, arrow=False)

    message(d, "user-event", 272, 170, 1100, "send_message() → MessageEvent", BLUE,
            lx=245, lw=405)
    message(d, "step", 362, 170, 480, "run() 调用 step()", PURPLE,
            lx=210, lw=250)
    message(d, "action-event", 452, 480, 1100, "模型 tool_call → ActionEvent（先写入）", PURPLE,
            lx=523, lw=510)

    message(d, "pause", 559, 480, 170, "WAITING_FOR_CONFIRMATION", AMBER,
            dashed=True, lx=198, lw=370)
    message(d, "resume", 655, 170, 480, "获准后再次 run()", AMBER,
            dashed=True, lx=198, lw=290)
    d.text("direct", "无需确认：同轮继续", 705, 615, 300, 24, GREEN, 6)

    message(d, "execute", 740, 480, 790, "tool(action, conversation)", GREEN,
            lx=505, lw=265)
    message(d, "tool-result", 827, 790, 480, "Observation / ValueError", GREEN,
            lx=507, lw=268)
    message(d, "observation", 917, 480, 1100,
            "ObservationEvent / AgentErrorEvent（回调入账）", GREEN,
            lx=521, lw=550)

    d.box("rejection", 72, 1010, 1126, 66, "#dce4ef", "#f7f9fc")
    d.elements[-1]["strokeWidth"] = 2
    d.elements[-1]["roughness"] = 1
    d.text("rejection-text", "拒绝确认 → UserRejectObservation（不执行工具）",
           94, 1027, 1070, 24, INK, 6)
    # Keep the parallel-order caveat in the adjacent text version.
    # Reduce vertical intervals while retaining label size at book width.
    for element in d.elements:
        if element["y"] >= 150:
            element["y"] = 150 + round((element["y"] - 150) * 0.82)
            if element["type"] != "text":
                element["height"] = round(element["height"] * 0.82)
            if element["type"] == "arrow":
                element["points"] = [[x, round(y * 0.82)] for x, y in element["points"]]
    d.save(Path(__file__).with_name("scene.excalidraw"))


if __name__ == "__main__":
    build()
