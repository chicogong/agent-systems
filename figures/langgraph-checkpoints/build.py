"""Build a checkpoint ancestry tree for LangGraph's thread state."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from diagram_style import BLUE, GREEN, INK, MUTED, ORANGE, PURPLE, Scene  # noqa: E402


def circle(d: Scene, name: str, x: int, y: int, size: int, stroke: str, fill: str) -> None:
    e = d._base(name, "ellipse", x, y, size, size)
    e.update(strokeColor=stroke, backgroundColor=fill, roughness=1, strokeWidth=2)
    d.elements.append(e)


def main() -> None:
    d = Scene()
    d.text("title", "LangGraph：同一个 thread，可以有多个状态分支", 35, 24, 1370, 34, INK, 8)
    d.text("subtitle", "checkpoint_id 定位版本；历史快照上 update_state 会写出新的后继，而不是覆盖旧结果。", 37, 79, 1350, 22, MUTED, 8)
    d.text("thread", "thread_id = T  ·  checkpoint_ns = \"\"（根命名空间）", 57, 155, 1210, 24, MUTED, 8)

    d.arrow("a-b", [(241, 321), (433, 321)], BLUE)
    d.arrow("b-c", [(594, 321), (797, 321)], BLUE)
    d.arrow("b-fork", [(552, 392), (670, 551)], PURPLE)
    d.arrow("fork-follow", [(831, 621), (1041, 621)], PURPLE)

    circle(d, "checkpoint-input", 80, 241, 161, BLUE, "#a5d8ff")
    d.text("input-label", "C₀\n输入后", 121, 270, 118, 25, BLUE, 8)
    circle(d, "checkpoint-before-b", 433, 241, 161, BLUE, "#a5d8ff")
    d.text("before-label", "C₁\nnext: B", 474, 271, 118, 25, BLUE, 8)
    circle(d, "checkpoint-original", 797, 241, 161, BLUE, "#dbeeff")
    d.text("original-label", "C₂\n原结果", 838, 271, 118, 25, BLUE, 8)
    circle(d, "checkpoint-fork", 670, 541, 161, PURPLE, "#d0bfff")
    d.text("fork-label", "C₁′\n更新 x", 710, 569, 120, 25, PURPLE, 8)
    circle(d, "checkpoint-fork-final", 1041, 541, 161, PURPLE, "#e5dbff")
    d.text("fork-final-label", "C₂′\n新结果", 1080, 569, 120, 25, PURPLE, 8)

    d.text("original-edge", "invoke(None,\nC₁.config)", 616, 256, 176, 21, BLUE, 8)
    d.text("fork-edge", "update_state(C₁.config, {x})", 654, 425, 360, 21, PURPLE, 8)
    d.text("resume-edge", "invoke(None,\nfork_config)", 854, 553, 180, 21, PURPLE, 8)
    d.text("history-note", "get_state_history(T) 看同一 thread 的快照；StateSnapshot.parent_config 指向直接父版本。", 59, 745, 1325, 22, MUTED, 8)
    d.text("lookup-note", "get_state(T) 取当前版本；get_state(T + checkpoint_id) 精确选取历史版本。", 59, 784, 1325, 22, MUTED, 8)
    d.box("boundary", 45, 843, 1315, 93, "#b9c4d3", "#f7f9fc")
    d.text("boundary-text", "示意只画关键快照，不代表执行仅写 5 个 checkpoint。\nInMemorySaver 仅适于测试；跨进程持久性取决于实际 saver。", 70, 855, 1265, 21, INK, 8)
    d.text("footer", "执行状态版本不等于长期语义记忆。", 50, 966, 1280, 18, MUTED, 8)
    for element in d.elements:
        if element["type"] == "arrow":
            element.update(roughness=1, strokeWidth=3)
        elif element["type"] == "rectangle":
            element["roughness"] = 1
    d.save(Path(__file__).with_name("scene.excalidraw"))


if __name__ == "__main__":
    main()
