"""Build the editable comparison scene; local exports come from this scene."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from diagram_style import Scene  # noqa: E402


def box(scene, key, x, y, w, h, stroke, fill):
    scene.box(key, x, y, w, h, stroke, fill)
    scene.elements[-1].update(roughness=1, strokeWidth=2)


def label(scene, key, value, x, y, w, size=23, color="#172336"):
    scene.text(key, value, x, y, w, size, color, 8)


def arrow(scene, key, points, color="#526071", dashed=False):
    scene.arrow(key, points, color)
    scene.elements[-1].update(roughness=1, strokeWidth=2.5)
    if dashed:
        scene.elements[-1]["strokeStyle"] = "dashed"


def build():
    s = Scene()
    label(s, "title", "四个系统怎样接着做、怎样停止", 26, 20, 990, 35)
    label(s, "subtitle", "从工具结果返回的位置，看各自的继续与停止条件", 29, 72, 990, 23, "#526071")

    # A comparison scorecard, not a chronological pipeline across systems.
    box(s, "head-system", 24, 127, 171, 48, "#b5c1d1", "#edf2f7")
    box(s, "head-gate", 215, 127, 360, 48, "#b5c1d1", "#edf2f7")
    box(s, "head-next", 601, 127, 449, 48, "#b5c1d1", "#edf2f7")
    label(s, "h1", "系统", 38, 137, 150)
    label(s, "h2", "结果返回后", 230, 137, 325)
    label(s, "h3", "继续 / 等待 / 停止", 616, 137, 380)

    rows = [
        ("pi", "Pi", "工具结果回到循环\nrunLoop", "轮间加入指令 steering\n结束前检查 follow-up\n结束回合 finishTurn=end", "#3478e5", "#e7f0ff"),
        ("mini", "mini-SWE", "观察结果追加到消息\nmessages[-1]", "普通消息 → 下一轮\n退出消息 exit → 返回 extra", "#7957cf", "#f0eaff"),
        ("open", "OpenCode", "事件更新 ToolPart\nprocessor 返回外层循环", "continue：继续；compact：先压缩\nstop：停止；模型流出错时\n按策略等待重试 retry", "#c87617", "#fff0db"),
        ("kimi", "Kimi Code", "工具结果回到回合\nrunTurn", "接着做下一步 tool_use\n步骤间加入指令 steer\n无续跑或达到上限：结束", "#138765", "#e2f7ed"),
    ]
    for i, (key, name, gate, outcome, color, fill) in enumerate(rows):
        y = 194 + i * 133
        box(s, f"{key}-name", 24, y, 171, 107, color, fill)
        box(s, f"{key}-gate", 215, y, 360, 107, color, "#ffffff")
        box(s, f"{key}-next", 601, y, 449, 107, color, fill)
        label(s, f"{key}-name-text", name, 39, y + 31, 147, 24, color)
        label(s, f"{key}-gate-text", gate, 230, y + 20, 330, 23)
        label(s, f"{key}-next-text", outcome, 616, y + 12, 418, 22)
        arrow(s, f"{key}-arrow", [(577, y + 54), (597, y + 54)], color)

    label(s, "note", "每行独立阅读；箭头表示该系统自己的处理顺序。", 29, 741, 970, 21, "#526071")
    s.save(Path(__file__).with_name("scene.excalidraw"))


if __name__ == "__main__":
    build()
