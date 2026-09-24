"""Build the editable delegation diagram from a compact horizontal flow."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from diagram_style import Scene  # noqa: E402

INK = "#203047"
MUTED = "#536579"
BLUE = "#3478e5"
PURPLE = "#8056e8"
GREEN = "#208664"
ORANGE = "#bb751a"


def box(d: Scene, key: str, x: int, y: int, w: int, h: int,
        title: str, detail: str, color: str, fill: str) -> None:
    d.box(key, x, y, w, h, color, fill)
    d.elements[-1].update(roughness=2, strokeWidth=2.5)
    d.text(key + "-title", title, x + 20, y + 20, w - 40, 29, INK, 6)
    d.text(key + "-detail", detail, x + 20, y + 72, w - 40, 24, MUTED, 6)


def arrow(d: Scene, key: str, points: list[tuple[int, int]],
          color: str, dashed: bool = False) -> None:
    d.arrow(key, points, color)
    d.elements[-1].update(roughness=2, strokeWidth=3 if not dashed else 2.5,
                          strokeStyle="dashed" if dashed else "solid")


def build() -> None:
    d = Scene()
    d.text("title", "委派不是派出去就算完成", 46, 25, 1100, 40, INK, 6)
    d.text("subtitle", "任务合同把回报、对账和验收接成闭环", 48, 78, 940, 26, MUTED, 6)

    box(d, "owner", 42, 226, 238, 150, "所有者", "目标与验收条件\n批准完成的人", GREEN, "#e9f5ef")
    arrow(d, "owner-contract", [(280, 300), (328, 300)], GREEN)
    box(d, "contract", 328, 207, 280, 188, "任务合同", "任务 ID / 输入版本\n范围 / 权限 / 回报", GREEN, "#e7f5ee")

    arrow(d, "contract-a", [(608, 264), (672, 264), (672, 195), (718, 195)], BLUE)
    arrow(d, "contract-b", [(608, 344), (672, 344), (672, 407), (718, 407)], PURPLE)
    box(d, "worker-a", 718, 127, 240, 138, "执行 A", "状态 + 证据\n未知和副作用", BLUE, "#eaf3ff")
    box(d, "worker-b", 718, 340, 240, 138, "执行 B", "状态 + 证据\n未知和副作用", PURPLE, "#f2ecff")

    arrow(d, "a-reconcile", [(958, 195), (1026, 195), (1026, 266), (1061, 266)], BLUE)
    arrow(d, "b-reconcile", [(958, 407), (1026, 407), (1026, 335), (1061, 335)], PURPLE)
    box(d, "reconcile", 1061, 203, 265, 195, "协调者对账", "核版本 / 缺口 / 冲突\n已发生的副作用", ORANGE, "#fff1d9")

    arrow(d, "reconcile-gate", [(1194, 398), (1194, 474)], GREEN)
    box(d, "gate", 1061, 474, 265, 128, "验收关口", "满足原目标 → 交付", GREEN, "#e9f7ef")

    # Failure returns to the contract rather than directly retrying effects.
    arrow(d, "repair", [(1061, 548), (998, 548), (998, 661),
                        (469, 661), (469, 395)], ORANGE, True)
    d.text("repair-label", "缺口 / 冲突：补证 · 重新派发 · 人工处理", 493, 617, 485, 23, ORANGE, 6)
    d.save(Path(__file__).with_name("scene.excalidraw"))


if __name__ == "__main__":
    build()
