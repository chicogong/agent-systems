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
    scene.text(f"{name}-label", label, left, y - 29, width, 20, color, 6)


def build():
    d = Scene()
    d.text("title", "OpenHands：动作先入账，结果后到达", 48, 23, 1200, 36, INK, 6)
    d.text("subtitle", "LocalConversation.run() + 默认 Agent.step() 的一次工具调用（SDK 6ebd820d）", 50, 77, 1190, 19, MUTED, 6)

    lanes = [
        (70, 170, "LocalConversation", BLUE, "#f1f7fe"),
        (380, 480, "Agent", PURPLE, "#f7f3fd"),
        (690, 790, "Tool", GREEN, "#f0faf6"),
        (1000, 1100, "EventLog", AMBER, "#fffaee"),
    ]
    for idx, (x, cx, title, color, fill) in enumerate(lanes):
        d.box(f"lane-{idx}", x, 150, 200, 840, color, fill)
        d.elements[-1]["strokeWidth"] = 1
        d.elements[-1]["opacity"] = 65
        d.text(f"lane-{idx}-title", title, x + 14, 171, 175, 21, color, 8)
        stroke(d, f"lane-{idx}-line", [(cx, 221), (cx, 960)], color,
               dashed=True, arrow=False)

    message(d, "user-event", 272, 170, 1100, "send_message() → MessageEvent", BLUE,
            lx=245, lw=405)
    message(d, "step", 362, 170, 480, "run() 调用 step()", PURPLE,
            lx=210, lw=250)
    message(d, "action-event", 452, 480, 1100, "模型 tool_call → ActionEvent（先写入）", PURPLE,
            lx=523, lw=510)

    d.text("confirmation-title", "确认模式支线", 287, 511, 260, 19, AMBER, 8)
    message(d, "pause", 559, 480, 170, "WAITING_FOR_CONFIRMATION", AMBER,
            dashed=True, lx=205, lw=265)
    message(d, "resume", 655, 170, 480, "再次 run() → 未匹配动作", AMBER,
            dashed=True, lx=198, lw=278)
    d.text("direct", "无需确认：同轮继续", 530, 615, 258, 17, GREEN, 6)

    message(d, "execute", 740, 480, 790, "tool(action, conversation)", GREEN,
            lx=505, lw=265)
    message(d, "tool-result", 827, 790, 480, "Observation / ValueError", GREEN,
            lx=507, lw=268)
    message(d, "observation", 917, 480, 1100,
            "ObservationEvent / AgentErrorEvent（回调入账）", GREEN,
            lx=521, lw=550)

    d.box("footer", 72, 1024, 1126, 103, "#dce4ef", "#f7f9fc")
    d.elements[-1]["strokeWidth"] = 1
    d.text("footer-text", "拒绝确认 → UserRejectObservation（不执行工具）\n事件顺序不等于并行工具副作用顺序；这张图只画同步 LocalConversation 的局部路径。",
           94, 1038, 1070, 18, INK, 6)
    d.save(Path(__file__).with_name("scene.excalidraw"))


if __name__ == "__main__":
    build()
