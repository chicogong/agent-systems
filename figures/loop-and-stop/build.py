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
    label(s, "title", "工具之后：下一步由谁决定？", 26, 20, 900, 35)
    label(s, "subtitle", "同一观察点 · 四种循环闸口", 29, 72, 850, 23, "#526071")

    # A comparison scorecard, not a chronological pipeline across systems.
    box(s, "head-system", 24, 127, 171, 48, "#b5c1d1", "#edf2f7")
    box(s, "head-gate", 215, 127, 360, 48, "#b5c1d1", "#edf2f7")
    box(s, "head-next", 601, 127, 417, 48, "#b5c1d1", "#edf2f7")
    label(s, "h1", "固定切面", 38, 137, 150)
    label(s, "h2", "结果写回 → 决策点", 230, 137, 325)
    label(s, "h3", "继续 / 等待 / 停止", 616, 137, 380)

    rows = [
        ("pi", "Pi", "tool result → runLoop", "steering：轮间\nfollow-up：结束前\nfinishTurn=end：停", "#3478e5", "#e7f0ff"),
        ("mini", "mini-SWE", "observation → messages[-1]", "尾部非 exit：下一轮\n尾部 exit：返回 extra", "#7957cf", "#f0eaff"),
        ("open", "OpenCode", "ToolPart → runLoop", "continue / compact：再处理\nblocked / error：停止\n流内 retry：退避等待", "#c87617", "#fff0db"),
        ("kimi", "Kimi Code", "tool.result → runTurn", "tool_use：下一步\nsteer：等 step 边界\n无续跑或上限：结束", "#138765", "#e2f7ed"),
    ]
    for i, (key, name, gate, outcome, color, fill) in enumerate(rows):
        y = 194 + i * 133
        box(s, f"{key}-name", 24, y, 171, 107, color, fill)
        box(s, f"{key}-gate", 215, y, 360, 107, color, "#ffffff")
        box(s, f"{key}-next", 601, y, 417, 107, color, fill)
        label(s, f"{key}-name-text", name, 39, y + 31, 147, 24, color)
        label(s, f"{key}-gate-text", gate, 230, y + 32, 330, 23)
        label(s, f"{key}-next-text", outcome, 616, y + 12, 385, 22)
        arrow(s, f"{key}-arrow", [(577, y + 54), (597, y + 54)], color)

    label(s, "note", "图中每一行是不同源码切面；箭头只表示该行的控制顺序。", 29, 741, 970, 21, "#526071")
    s.save(Path(__file__).with_name("scene.excalidraw"))


if __name__ == "__main__":
    build()
