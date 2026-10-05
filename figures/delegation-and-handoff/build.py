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
    d.text("title", "分配任务后，汇总并核对结果", 46, 25, 1100, 40, INK, 6)
    d.text("subtitle", "先写清任务、范围和回报要求，再按原目标检查成果", 48, 78, 1240, 26, MUTED, 6)

    box(d, "owner", 42, 226, 238, 150, "任务负责人", "目标与验收条件\n确认完成的人", GREEN, "#e9f5ef")
    arrow(d, "owner-contract", [(280, 300), (328, 300)], GREEN)
    box(d, "contract", 328, 207, 280, 188, "分工清单", "任务 ID / 输入版本\n范围 / 权限 / 回报", GREEN, "#e7f5ee")

    arrow(d, "contract-a", [(608, 264), (672, 264), (672, 195), (718, 195)], BLUE)
    arrow(d, "contract-b", [(608, 344), (672, 344), (672, 407), (718, 407)], PURPLE)
    box(d, "worker-a", 718, 127, 240, 150, "执行者 A", "状态 + 依据\n外部操作与未知项", BLUE, "#eaf3ff")
    box(d, "worker-b", 718, 340, 240, 150, "执行者 B", "状态 + 依据\n外部操作与未知项", PURPLE, "#f2ecff")

    arrow(d, "a-reconcile", [(958, 195), (1026, 195), (1026, 266), (1061, 266)], BLUE)
    arrow(d, "b-reconcile", [(958, 407), (1026, 407), (1026, 335), (1061, 335)], PURPLE)
    box(d, "reconcile", 1061, 203, 265, 195, "汇总并核对", "核版本、查冲突\n补缺项、查外部结果", ORANGE, "#fff1d9")

    arrow(d, "reconcile-gate", [(1194, 398), (1194, 474)], GREEN)
    box(d, "gate", 1061, 474, 265, 128, "按原目标验收", "达到要求 → 交付", GREEN, "#e9f7ef")

    # Failure returns to the contract rather than directly retrying effects.
    arrow(d, "repair", [(1061, 548), (998, 548), (998, 661),
                        (469, 661), (469, 395)], ORANGE, True)
    d.text("repair-label", "缺项 / 冲突：补资料、重新分工或人工处理", 493, 617, 515, 23, ORANGE, 6)
    d.save(Path(__file__).with_name("scene.excalidraw"))


if __name__ == "__main__":
    build()
