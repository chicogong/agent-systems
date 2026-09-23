"""Build a checkpoint ancestry tree for LangGraph's thread state."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from diagram_style import BLUE, GREEN, INK, MUTED, ORANGE, PURPLE, Scene  # noqa: E402


def circle(d: Scene, name: str, x: int, y: int, size: int, stroke: str, fill: str) -> None:
    e = d._base(name, "ellipse", x, y, size, size)
    e.update(strokeColor=stroke, backgroundColor=fill)
    d.elements.append(e)


def main() -> None:
    d = Scene()
    d.text("title", "LangGraph：同一个 thread，可以有多个状态分支", 35, 24, 1370, 36, INK, 6)
    d.text("subtitle", "checkpoint_id 定位版本；历史快照上 update_state 会写出新的后继，而不是覆盖旧结果。", 37, 79, 1350, 19, MUTED, 6)
    d.text("thread", "thread_id = T  ·  checkpoint_ns = \"\"（根命名空间）", 57, 155, 1210, 22, MUTED, 8)

    d.arrow("a-b", [(241, 321), (433, 321)], BLUE)
    d.arrow("b-c", [(594, 321), (797, 321)], BLUE)
    d.arrow("b-fork", [(552, 392), (670, 551)], PURPLE)
    d.arrow("fork-follow", [(831, 621), (1041, 621)], PURPLE)

    circle(d, "checkpoint-input", 80, 241, 161, BLUE, "#e8f3ff")
    d.text("input-label", "C₀\n输入后", 121, 276, 118, 21, BLUE, 6)
    circle(d, "checkpoint-before-b", 433, 241, 161, BLUE, "#dcecff")
    d.text("before-label", "C₁\nnext: B", 474, 277, 118, 21, BLUE, 6)
    circle(d, "checkpoint-original", 797, 241, 161, BLUE, "#edf6ff")
    d.text("original-label", "C₂\n原结果", 838, 277, 118, 21, BLUE, 6)
    circle(d, "checkpoint-fork", 670, 541, 161, PURPLE, "#e9ddff")
    d.text("fork-label", "C₁′\n更新 x", 710, 575, 120, 21, PURPLE, 6)
    circle(d, "checkpoint-fork-final", 1041, 541, 161, PURPLE, "#f1eaff")
    d.text("fork-final-label", "C₂′\n新结果", 1080, 575, 120, 21, PURPLE, 6)

    d.text("original-edge", "invoke(None, C₁.config)", 610, 277, 260, 16, BLUE, 8)
    d.text("fork-edge", "update_state(C₁.config, {x})", 560, 462, 370, 16, PURPLE, 8)
    d.text("resume-edge", "invoke(None, fork_config)", 846, 567, 300, 16, PURPLE, 8)
    d.text("history-note", "get_state_history(T) 看同一 thread 的快照；StateSnapshot.parent_config 指向直接父版本。", 59, 748, 1325, 19, MUTED, 6)
    d.text("lookup-note", "get_state(T) 取当前版本；get_state(T + checkpoint_id) 精确选取历史版本。", 59, 785, 1325, 19, MUTED, 6)
    d.box("boundary", 45, 843, 1315, 93, "#b9c4d3", "#f7f9fc")
    d.text("boundary-text", "示意只画关键快照，不代表执行仅写 5 个 checkpoint。InMemorySaver 仅适于测试；跨进程持久性取决于实际 saver。", 70, 872, 1265, 17, INK, 6)
    d.text("footer", "固定源码 langchain-ai/langgraph@bdb85b5a；图解执行状态版本，不等于长期语义记忆。", 50, 966, 1280, 16, MUTED, 6)
    d.save(Path(__file__).with_name("scene.excalidraw"))


if __name__ == "__main__":
    main()
