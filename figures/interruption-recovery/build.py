"""Build the editable recovery decision loop.

A single uncertain result drives reconciliation, then three outcomes.
"""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from diagram_style import INK, MUTED, Scene  # noqa: E402

BLUE = "#4a9eed"
PURPLE = "#8b5cf6"
GREEN = "#16a34a"
ORANGE = "#f59e0b"


def label(d: Scene, name: str, value: str, x: int, y: int, w: int, size: int = 22, color: str = INK) -> None:
    d.text(name, value, x, y, w, size, color, 8)


def node(d: Scene, name: str, x: int, y: int, w: int, h: int, color: str, fill: str) -> None:
    d.box(name, x, y, w, h, color, fill)


def main() -> None:
    d = Scene()

    # The dashed divider marks where the request leaves local execution.
    boundary = d._base("effect-boundary", "line", 590, 26, 0, 170)
    boundary.update(points=[[0, 0], [0, 170]], strokeColor=PURPLE, strokeWidth=2, strokeStyle="dashed", roughness=1)
    d.elements.append(boundary)
    label(d, "boundary-label", "副作用边界", 530, 0, 190, 21, PURPLE)

    node(d, "request", 90, 62, 285, 91, BLUE, "#a5d8ff")
    label(d, "request-text", "用业务键 K\n发送创建请求", 113, 76, 250, 23)
    d.arrow("send", [(375, 108), (735, 108)], PURPLE)
    label(d, "send-label", "发送", 490, 70, 82, 21, PURPLE)
    node(d, "external-effect", 735, 62, 287, 91, PURPLE, "#d0bfff")
    label(d, "external-text", "可能已创建\n响应未抵达", 759, 76, 245, 23)

    d.arrow("effect-to-unknown", [(879, 153), (879, 257), (702, 257)], ORANGE)
    ellipse = d._base("unknown", "ellipse", 420, 203, 282, 108)
    ellipse.update(strokeColor=ORANGE, backgroundColor="#ffd8a8", strokeWidth=3, roughness=2)
    d.elements.append(ellipse)
    label(d, "unknown-title", "结果未知", 508, 221, 175, 28)
    label(d, "unknown-detail", "超时 · 取消 · 断线", 453, 262, 245, 21)

    d.arrow("unknown-to-query", [(561, 311), (561, 352)], ORANGE)
    node(d, "reconcile", 430, 352, 262, 76, ORANGE, "#fff3bf")
    label(d, "reconcile-text", "按 K / 请求 ID 对账", 448, 374, 236, 22)

    # A callout, not a process node: restoring state cannot undo the effect.
    label(d, "checkpoint-note", "checkpoint 只存图状态\n外部动作仍需对账", 60, 344, 315, 21, MUTED)

    d.arrow("confirmed-created", [(470, 428), (180, 526)], GREEN)
    d.arrow("confirmed-absent", [(561, 428), (561, 526)], BLUE)
    d.arrow("still-unknown", [(652, 428), (948, 526)], ORANGE)
    label(d, "created-condition", "已创建", 250, 448, 125, 21, GREEN)
    label(d, "absent-condition", "未创建\n且可重试", 585, 450, 112, 21, BLUE)
    label(d, "unknown-condition", "仍未知", 811, 456, 120, 21, ORANGE)

    node(d, "existing", 48, 526, 267, 96, GREEN, "#c3fae8")
    label(d, "existing-text", "复用已有工单 ID\n继续，不再创建", 72, 541, 235, 21)
    node(d, "retry", 427, 526, 267, 96, BLUE, "#a5d8ff")
    label(d, "retry-text", "同 K 重试\n最多 N 次", 451, 541, 235, 22)
    node(d, "human", 831, 526, 268, 96, ORANGE, "#ffd8a8")
    label(d, "human-text", "暂停，人工对账\n决定继续 / 补偿", 854, 541, 237, 21)

    # A bounded loop visibly returns to the same request. Exhaustion exits.
    d.arrow("retry-loop", [(561, 622), (561, 674), (20, 674), (20, 107), (90, 107)], BLUE)
    label(d, "retry-loop-guard", "n < N 才重发", 245, 637, 190, 21, BLUE)
    d.arrow("exhausted", [(694, 573), (831, 573)], ORANGE)
    label(d, "exhausted-condition", "达上限", 727, 534, 100, 21, ORANGE)

    for element in d.elements:
        if element["type"] == "arrow":
            element.update(strokeWidth=4, roughness=2)
        elif element["type"] == "rectangle":
            element.update(strokeWidth=2, roughness=2)
    d.save(Path(__file__).with_name("scene.excalidraw"))


if __name__ == "__main__":
    main()
