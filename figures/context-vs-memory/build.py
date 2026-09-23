"""Build the sources-to-visible-context concept map as editable Excalidraw."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from diagram_style import Scene  # noqa: E402


INK = "#243042"
MUTED = "#647084"
BLUE = "#397fe0"
PURPLE = "#805be1"
GREEN = "#23956a"
TEAL = "#1d9daa"
AMBER = "#e29322"


def card(scene: Scene, name: str, x: int, y: int, w: int, h: int,
         stroke: str, fill: str, label: str) -> None:
    scene.box(name, x, y, w, h, stroke, fill)
    scene.elements[-1]["strokeWidth"] = 3
    scene.elements[-1]["roughness"] = 1
    scene.text(name + "-label", label, x + 22, y + 23, w - 44, 23, INK, 8)


def arrow(scene: Scene, name: str, start: tuple[int, int],
          end: tuple[int, int], color: str, dashed: bool = False) -> None:
    scene.arrow(name, [start, end], color)
    scene.elements[-1]["strokeWidth"] = 3
    scene.elements[-1]["roughness"] = 1
    scene.elements[-1]["strokeStyle"] = "dashed" if dashed else "solid"


def build() -> None:
    scene = Scene()
    scene.text("title", "存着 ≠ 这轮模型看见", 45, 28, 1100, 38, INK, 6)
    scene.text("subtitle", "上下文是一次请求的输入；历史与知识只是可能的来源。",
               47, 84, 1100, 22, MUTED, 6)

    scene.text("sources-heading", "可用来源", 60, 153, 380, 24, BLUE, 6)
    sources = [
        ("session", 205, BLUE, "#e8f3ff", "会话记录  transcript", "挑选"),
        ("summary", 302, PURPLE, "#f1ebff", "压缩摘要  summary", "引用"),
        ("memory", 399, GREEN, "#e8f8ef", "长期记忆  memory", "检索"),
        ("knowledge", 496, TEAL, "#e5f8fa", "外部知识  retrieval", "检索"),
    ]
    for name, y, color, fill, label, edge in sources:
        card(scene, name, 60, y, 398, 72, color, fill, label)
        arrow(scene, name + "-to-assembly", (458, y + 36), (626, y + 36),
              color, dashed=True)
        scene.text(name + "-edge", edge, 502, y + 6, 86, 20, color, 6)

    scene.text("assembly-heading", "本轮装配", 627, 153, 240, 24, AMBER, 6)
    card(scene, "assembly", 626, 205, 236, 363, AMBER, "#fff2da", "上下文装配")
    scene.text("assembly-body", "选择所需片段\n加入指令与新输入\n受窗口预算约束",
               652, 298, 188, 24, INK, 6)

    arrow(scene, "assembly-to-request", (862, 386), (961, 386), AMBER)
    scene.text("visible-heading", "模型实际可见", 960, 253, 238, 24, BLUE, 6)
    card(scene, "request", 961, 309, 239, 160, BLUE, "#e8f3ff", "本轮模型输入")
    scene.text("request-body", "只有装配后的内容\n会进入这次请求", 982, 387, 198, 23, INK, 6)

    scene.text("caveat", "虚线表示可能被选择 / 检索，并非自动全量读取；具体系统可能没有其中某一层。",
               60, 624, 1140, 20, MUTED, 6)
    scene.save(Path(__file__).with_name("scene.excalidraw"))


if __name__ == "__main__":
    build()
