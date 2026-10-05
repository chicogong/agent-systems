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
    d.text("title", "LangGraph：从旧进度继续，保留原结果", 45, 25, 1120, 31, INK, 8)
    d.text("thread", "同一任务：thread_id = T，checkpoint_ns = \"\"", 57, 112, 1110, 23, MUTED, 8)

    d.arrow("a-b", [(241, 321), (433, 321)], BLUE)
    d.arrow("b-c", [(594, 321), (797, 321)], BLUE)
    d.arrow("b-fork", [(552, 392), (670, 551)], PURPLE)
    d.arrow("fork-follow", [(831, 621), (1041, 621)], PURPLE)

    circle(d, "checkpoint-input", 80, 241, 161, BLUE, "#a5d8ff")
    d.text("input-label", "C₀\n收到输入", 121, 270, 118, 25, BLUE, 8)
    circle(d, "checkpoint-before-b", 433, 241, 161, BLUE, "#a5d8ff")
    d.text("before-label", "C₁\n待执行 B\nnext: B", 474, 271, 118, 25, BLUE, 8)
    circle(d, "checkpoint-original", 797, 241, 161, BLUE, "#dbeeff")
    d.text("original-label", "C₂\n原结果", 838, 271, 118, 25, BLUE, 8)
    circle(d, "checkpoint-fork", 670, 541, 161, PURPLE, "#d0bfff")
    d.text("fork-label", "C₁′\n更新 x", 710, 569, 120, 25, PURPLE, 8)
    circle(d, "checkpoint-fork-final", 1041, 541, 161, PURPLE, "#e5dbff")
    d.text("fork-final-label", "C₂′\n新结果", 1080, 569, 120, 25, PURPLE, 8)

    d.text("original-edge", "执行节点 B", 612, 270, 220, 23, BLUE, 8)
    d.text("fork-edge", "修改旧状态\nupdate_state(C₁.config, {x})", 654, 400, 390, 23, PURPLE, 8)
    d.text("resume-edge", "从新版本继续执行 B\ninvoke(None, fork_config)", 849, 470, 330, 23, PURPLE, 8)
    d.text("lookup-note", "内存示例 InMemorySaver：指定 checkpoint_id 读对应版本；省略时取同范围最大 ID", 59, 752, 1140, 23, MUTED, 8)
    d.text("history-note", "get_state_history(T) 查看两支历史；parent_config 记录直接父版本", 59, 795, 1120, 23, MUTED, 8)
    for element in d.elements:
        if element["type"] == "arrow":
            element.update(roughness=1, strokeWidth=3)
        elif element["type"] == "rectangle":
            element["roughness"] = 1
    d.save(Path(__file__).with_name("scene.excalidraw"))


if __name__ == "__main__":
    main()
