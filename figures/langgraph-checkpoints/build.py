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
    d.text("title", "从 C₁ 分叉：原结果仍保留", 45, 25, 1120, 31, INK, 8)
    d.text("thread", "同一 thread_id = T · checkpoint_ns = \"\"", 57, 112, 1110, 23, MUTED, 8)

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

    d.text("original-edge", "原执行：节点 B", 612, 270, 220, 23, BLUE, 8)
    d.text("fork-edge", "update_state(C₁.config, {x})", 654, 425, 390, 23, PURPLE, 8)
    d.text("resume-edge", "invoke(None, fork_config)\n节点 B 再执行", 849, 470, 330, 23, PURPLE, 8)
    d.text("lookup-note", "InMemorySaver：未指定 checkpoint_id → 最大 ID；指定 ID → 对应快照", 59, 752, 1140, 23, MUTED, 8)
    d.text("history-note", "get_state_history(T)：两支可追溯；parent_config：直接父版本", 59, 795, 1120, 23, MUTED, 8)
    for element in d.elements:
        if element["type"] == "arrow":
            element.update(roughness=1, strokeWidth=3)
        elif element["type"] == "rectangle":
            element["roughness"] = 1
    d.save(Path(__file__).with_name("scene.excalidraw"))


if __name__ == "__main__":
    main()
