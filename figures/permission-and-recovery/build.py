"""Build a two-rail decision diagram for an action with an unknown result."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from diagram_style import Scene  # noqa: E402

INK = "#203047"
MUTED = "#506177"
BLUE = "#3478e5"
GREEN = "#208664"
ORANGE = "#bb751a"
PURPLE = "#8056e8"


def card(d: Scene, key: str, x: int, y: int, w: int, h: int,
         title: str, detail: str, color: str, fill: str) -> None:
    d.box(key, x, y, w, h, color, fill)
    d.elements[-1].update(roughness=2, strokeWidth=2.5)
    d.text(f"{key}-title", title, x + 16, y + 18, w - 32, 29, INK, 6)
    d.text(f"{key}-detail", detail, x + 16, y + 70, w - 32, 25, MUTED, 6)


def arrow(d: Scene, key: str, points: list[tuple[int, int]],
          color: str, dashed: bool = False) -> None:
    d.arrow(key, points, color)
    d.elements[-1].update(
        roughness=2,
        strokeWidth=2.5 if dashed else 3,
        strokeStyle="dashed" if dashed else "solid",
    )


def build() -> None:
    d = Scene()
    d.text("claim", "超时后，先查询原操作，再决定是否重试", 42, 18, 1120, 38, INK, 6)
    d.text("local-rail", "本地记录：许可、发送、超时、查询", 43, 87, 480, 26, BLUE, 6)

    cards = [
        ("proposal", 40, "准备操作", "确定目标与变化\n申请执行许可", GREEN, "#e9f6ef"),
        ("approval", 292, "获准执行", "许可已取得\n结果另行确认", GREEN, "#e9f6ef"),
        ("request", 544, "请求已发出", "原操作 ID\n例如 #42", BLUE, "#eaf3ff"),
        ("timeout", 796, "连接超时", "还没拿到回执\n先标记结果未知", ORANGE, "#fff1dd"),
        ("query", 1048, "查询原操作", "按原 ID #42\n核对服务记录", PURPLE, "#f2ecff"),
    ]
    for key, x, title, detail, color, fill in cards:
        card(d, key, x, 147, 210, 165, title, detail, color, fill)

    for key, a, b, color in [
        ("propose-approve", 250, 292, GREEN),
        ("approve-request", 502, 544, GREEN),
        ("request-timeout", 754, 796, BLUE),
        ("timeout-query", 1006, 1048, PURPLE),
    ]:
        arrow(d, key, [(a, 230), (b, 230)], color)

    d.text("external-rail", "超时时，目标服务可能处于三种状态", 43, 371, 1200, 26, MUTED, 6)
    arrow(d, "unknown-worlds", [(901, 312), (901, 420)], ORANGE, True)
    arrow(d, "world-not-received", [(901, 420), (245, 420), (245, 462)], ORANGE, True)
    arrow(d, "world-in-flight", [(901, 420), (625, 420), (625, 462)], ORANGE, True)
    arrow(d, "world-received", [(901, 420), (1005, 420), (1005, 462)], ORANGE, True)
    card(d, "not-received", 95, 462, 300, 140, "还没接收", "查不到时还要看\n查询是否有延迟", BLUE, "#edf5ff")
    card(d, "in-flight", 475, 462, 300, 140, "请求还在路上", "先等待或查原请求\n旧请求可能迟到", PURPLE, "#f2ecff")
    card(d, "received", 855, 462, 300, 140, "目标已接收", "排队 / 执行 / 完成\n回执可能丢失", ORANGE, "#fff1dd")

    d.box("boundary", 40, 662, 1218, 112, ORANGE, "#fff8ea")
    d.elements[-1].update(roughness=2, strokeWidth=2)
    d.text("boundary-text", "重试须获准：确认旧请求已终止且未生效，或接口支持同幂等键安全重放。\n检查点 checkpoint 保存本地进度，外部结果仍需查询原操作。", 64, 684, 1160, 27, INK, 6)

    d.save(Path(__file__).with_name("scene.excalidraw"))


if __name__ == "__main__":
    build()
