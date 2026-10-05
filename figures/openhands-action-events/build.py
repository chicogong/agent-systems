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
            lx: int | None = None, lw: int | None = None,
            size: int = 24, label_gap: int = 46):
    stroke(scene, name, [(x1, y), (x2, y)], color, dashed)
    left = lx if lx is not None else min(x1, x2) + 24
    width = lw if lw is not None else abs(x2 - x1) - 48
    scene.text(f"{name}-label", label, left, y - label_gap, width, size, color, 6)


def build():
    d = Scene()
    d.text("title", "OpenHands：先记录动作，再执行和记录结果", 48, 23, 1200, 36, INK, 6)
    d.text("subtitle", "接收输入 send_message() → 会话 run() → Agent.step()", 50, 77, 1190, 24, MUTED, 6)

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
        lane_title = ("本地会话\nLocal\nConversation", "安排动作\nAgent",
                      "执行工具\nTool", "事件清单\nEventLog")[idx]
        d.text(f"lane-{idx}-title", lane_title, x + 14, 154, 175,
               21 if idx == 0 else 22, color, 8)
        stroke(d, f"lane-{idx}-line", [(cx, 270), (cx, 960)], color,
               dashed=True, arrow=False)

    message(d, "user-event", 272, 170, 1100, "记录用户输入 · MessageEvent", BLUE,
            lx=245, lw=405)
    message(d, "step", 362, 170, 480, "运行一步 · step()", PURPLE,
            lx=210, lw=250)
    message(d, "action-event", 452, 480, 1100, "先记工具动作 · ActionEvent", PURPLE,
            lx=523, lw=510)

    d.box("confirmation-opt", 122, 482, 500, 208, AMBER, "transparent")
    d.elements[-1].update(strokeStyle="dashed", strokeWidth=1, roughness=1)
    d.text("confirmation-opt-label", "仅需用户确认时", 137, 450, 255, 21, AMBER, 6)
    message(d, "pause", 559, 480, 170, "等待用户批准\nWAITING_FOR_CONFIRMATION", AMBER,
            dashed=True, lx=198, lw=370, size=21, label_gap=69)
    message(d, "resume", 655, 170, 480, "批准后，宿主再 run()", AMBER,
            dashed=True, lx=198, lw=290)
    d.text("direct", "无需确认：同一步执行", 705, 615, 300, 24, GREEN, 6)

    message(d, "execute", 740, 480, 790, "执行 · tool(...)", GREEN,
            lx=505, lw=265)
    message(d, "tool-result", 827, 790, 480, "观察结果／错误\nObservation / ValueError", GREEN,
            lx=507, lw=310, size=21, label_gap=69)
    message(d, "observation", 917, 480, 1100,
            "记录结果／错误事件\nObservationEvent / AgentErrorEvent", GREEN,
            lx=521, lw=550, size=21, label_gap=69)

    d.box("rejection", 72, 1010, 1126, 66, "#dce4ef", "#f7f9fc")
    d.elements[-1]["strokeWidth"] = 2
    d.elements[-1]["roughness"] = 1
    d.text("rejection-text", "用户拒绝：记录 UserRejectObservation，跳过工具",
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
