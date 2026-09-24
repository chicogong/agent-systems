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
    scene.text(f"{name}-title", title, x + 17, y + 15, w - 34, 27, INK, 8)
    scene.text(f"{name}-detail", detail, x + 17, y + 62, w - 34, 22, MUTED, 8)


def arrow(scene: Scene, name: str, points: list[tuple[int, int]], color: str,
          dashed: bool = False) -> None:
    scene.arrow(name, points, color)
    scene.elements[-1].update(roughness=1, strokeWidth=3)
    if dashed:
        scene.elements[-1]["strokeStyle"] = "dashed"


def build() -> None:
    d = Scene()
    d.text("title", "mini-SWE-agent：消息尾部决定退出", 35, 25, 995, 35, INK, 8)

    # The ledger records appends; the center column is the control flow.
    d.box("ledger", 35, 132, 285, 548, "#b9cef0", "#f7faff")
    d.elements[-1].update(roughness=1, strokeWidth=2)
    d.text("ledger-title", "messages[] · 追加", 55, 154, 250, 25, "#2563a6", 8)
    for index, y in enumerate((218, 286, 354, 422, 490, 558)):
        d.arrow(f"ledger-rule-{index}", [(55, y), (300, y)], "#d5dfe9")
        d.elements[-1].update(strokeWidth=1, endArrowhead=None)
    for name, value, y, color in (
        ("system", "01  system 模板", 230, INK),
        ("user", "02  user(task)", 298, INK),
        ("assistant", "03  assistant(action)", 366, VIOLET),
        ("observation", "04  observation", 434, TEAL),
        ("repeat", "…   下一轮继续追加", 502, MUTED),
        ("exit", "末条 exit → 停止", 570, GREEN),
    ):
        d.text(name, value, 55, y, 250, 22, color, 8)

    # Draw arrows first so the nodes cover their endpoints. The two ledger
    # routes end at different rows and never cross the main loop.
    arrow(d, "query-to-execute", [(550, 282), (550, 336)], VIOLET)
    arrow(d, "execute-to-check", [(550, 452), (550, 538)], TEAL)
    arrow(d, "query-appends", [(410, 232), (370, 232), (370, 378), (320, 378)], VIOLET)
    arrow(d, "execute-appends", [(410, 400), (345, 400), (345, 446), (320, 446)], TEAL)
    arrow(d, "continue-loop", [(690, 576), (725, 576), (725, 224), (690, 224)], BLUE)
    arrow(d, "stop-to-return", [(690, 610), (790, 610)], GREEN)

    card(d, "query", 410, 166, 280, 116, VIOLET, "#e5dbff",
         "query()", "限额检查 → model.query")
    card(d, "execute", 410, 336, 280, 116, TEAL, "#c9f4f4",
         "execute_actions()", "env.execute → 观察")
    card(d, "stop-check", 410, 538, 280, 116, BLUE, "#d7ebff",
         "每轮 save() 之后", "末条 role == exit ?")
    d.text("continue-label", "否 · 下一轮", 734, 486, 145, 22, "#2563a6", 8)
    d.text("yes-label", "是", 744, 578, 30, 22, GREEN, 8)

    # These are possible sources of exit messages, not a mandatory sequence.
    d.box("exit-sources", 790, 132, 295, 320, "#f5c46a", "#fff7df")
    d.elements[-1].update(roughness=1, strokeWidth=2)
    d.text("exit-title", "exit 消息可能来自", 808, 154, 255, 24, "#9a6700", 8)
    d.text("exit-1", "Submitted\n本地命令完成哨兵", 808, 212, 255, 22, INK, 8)
    d.text("exit-2", "Limits / Time\n模型请求前的限制", 808, 290, 255, 22, INK, 8)
    d.text("exit-3", "RepeatedFormatError\n连续解析失败达阈值", 808, 368, 255, 22, INK, 8)
    card(d, "return", 790, 538, 295, 116, GREEN, "#c3fae8",
         "返回 exit.extra", "不是模型布尔值")

    d.save(Path(__file__).with_name("scene.excalidraw"))


if __name__ == "__main__":
    build()
