"""Generate the native mini-swe-agent message-ledger control-flow scene."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from diagram_style import Scene  # noqa: E402


INK = "#14213d"
MUTED = "#475569"
BLUE = "#4a9eed"
VIOLET = "#8b5cf6"
TEAL = "#06a6a6"
GREEN = "#16a34a"


def card(scene: Scene, name: str, x: int, y: int, w: int, h: int,
         stroke: str, fill: str, title: str, detail: str) -> None:
    scene.box(name, x, y, w, h, stroke, fill)
    scene.elements[-1].update(roughness=1, strokeWidth=2)
    scene.text(f"{name}-title", title, x + 20, y + 17, w - 40, 22, INK, 8)
    scene.text(f"{name}-detail", detail, x + 20, y + 55, w - 40, 17, MUTED, 8)


def arrow(scene: Scene, name: str, points: list[tuple[int, int]], color: str,
          dashed: bool = False) -> None:
    scene.arrow(name, points, color)
    scene.elements[-1].update(roughness=1, strokeWidth=3)
    if dashed:
        scene.elements[-1]["strokeStyle"] = "dashed"


def rule(scene: Scene, name: str, y: int) -> None:
    scene.arrow(name, [(76, y), (366, y)], "#d5dfe9")
    scene.elements[-1].update(strokeWidth=1, endArrowhead=None)


def build() -> None:
    d = Scene()
    d.text("title", "mini-SWE-agent：消息尾部决定何时退出", 47, 28, 1170, 35, INK, 8)
    d.text("subtitle", "DefaultAgent：query → execute_actions → save；末条 role=exit 才停止", 50, 82, 1130, 19, MUTED, 8)

    # The ledger and the loop are different things: arrows into the ledger
    # describe appends, while the blue loop arrow describes another step().
    d.box("ledger", 47, 169, 345, 609, "#b9cef0", "#f7faff")
    d.elements[-1].update(roughness=1, strokeWidth=2)
    d.text("ledger-title", "messages[] · 逐步追加", 74, 191, 300, 24, "#2563a6", 8)
    for index, y in enumerate((273, 352, 431, 510, 589, 668)):
        rule(d, f"ledger-rule-{index}", y)
    for name, value, y, color in (
        ("system", "01  system 模板", 293, INK),
        ("user", "02  user(task)", 372, INK),
        ("assistant", "03  assistant(action)", 451, VIOLET),
        ("observation", "04  observation", 530, TEAL),
        ("repeat", "…   下一轮继续追加", 609, MUTED),
        ("exit", "末条 exit → 停止", 688, GREEN),
    ):
        d.text(name, value, 74, y, 292, 19, color, 8)

    # Draw arrows before cards so they tuck cleanly beneath the card borders.
    arrow(d, "query-to-execute", [(643, 352), (643, 427)], VIOLET)
    arrow(d, "execute-to-check", [(643, 537), (643, 603)], TEAL)
    arrow(d, "continue-loop", [(789, 651), (827, 651), (827, 301), (789, 301)], BLUE)
    d.text("continue-label", "否 · 下一轮", 835, 554, 140, 18, "#2563a6", 8)
    arrow(d, "stop-to-return", [(789, 702), (901, 702)], GREEN)
    d.text("yes-label", "是", 829, 670, 45, 18, GREEN, 8)
    arrow(d, "query-appends", [(496, 301), (453, 301), (453, 460), (392, 460)], VIOLET)
    arrow(d, "execute-appends", [(496, 482), (433, 482), (433, 539), (392, 539)], TEAL)

    card(d, "query", 496, 242, 293, 110, VIOLET, "#e5dbff",
         "query()", "限额检查 → model.query")
    card(d, "execute", 496, 427, 293, 110, TEAL, "#c9f4f4",
         "execute_actions()", "env.execute → 观察")
    card(d, "stop-check", 496, 603, 293, 128, BLUE, "#d7ebff",
         "每轮 save() 之后", "末条 role == exit ?")
    card(d, "return", 901, 640, 302, 115, GREEN, "#c3fae8",
         "返回 exit.extra", "不是模型布尔值")

    # These are possible sources, not a mandatory path after query/execute.
    d.box("exit-sources", 904, 186, 298, 330, "#f5c46a", "#fff7df")
    d.elements[-1].update(roughness=1, strokeWidth=2)
    d.text("exit-title", "exit 消息可能来自", 925, 209, 255, 23, "#9a6700", 8)
    d.text("exit-1", "Submitted\n本地命令完成哨兵", 925, 271, 255, 18, INK, 8)
    d.text("exit-2", "Limits / Time\n模型请求前的限制", 925, 353, 255, 18, INK, 8)
    d.text("exit-3", "RepeatedFormatError\n连续解析失败达阈值", 925, 435, 255, 18, INK, 8)

    d.save(Path(__file__).with_name("scene.excalidraw"))


if __name__ == "__main__":
    build()
