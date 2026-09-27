"""Build the editable teaching sequence; no HTTP request is made here."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from diagram_style import BLUE, GREEN, INK, MUTED, ORANGE, Scene


def label(scene, name, text, x, y, width, size=24, color=INK, font=6, align="left"):
    scene.text(name, text, x, y, width, size, color, font, align)


def card(scene, name, title, detail, x, y, width, height, color, fill):
    scene.box(name, x, y, width, height, color, fill)
    scene.elements[-1]["roughness"] = 1
    label(scene, name + "-title", title, x + 16, y + 12, width - 32, 25, color)
    if detail:
        label(scene, name + "-detail", detail, x + 16, y + 47, width - 32, 23)


def message(scene, name, points, color, text, x, y, width, font=6):
    scene.arrow(name, points, color)
    scene.elements[-1].update(roughness=1, strokeWidth=3)
    label(scene, name + "-label", text, x, y, width, 24, color, font)


def lifeline(scene, name, x):
    line = scene._base(name, "line", x, 174, 0, 572)
    line.update(strokeColor="#a8b5c5", strokeWidth=1.5, strokeStyle="dashed",
                roughness=1, points=[[0, 0], [0, 572]],
                lastCommittedPoint=None, startBinding=None, endBinding=None,
                startArrowhead=None, endArrowhead=None)
    scene.elements.append(line)


def main():
    d = Scene()
    label(d, "title", "回执超时后，用同一个 ID 找回记录", 35, 26, 1000, 34)
    label(d, "reading", "时间向下 · 一次请求、一次查询，不重复执行", 35, 76, 1000, 25, MUTED)
    card(d, "client", "客户端", "", 40, 119, 225, 54, BLUE, "#e7f1ff")
    card(d, "transport", "HTTP 传输", "", 412, 119, 225, 54, BLUE, "#e7f1ff")
    card(d, "service", "服务", "", 786, 119, 225, 54, GREEN, "#e8f6ed")
    for name, x in (("client-life", 152), ("transport-life", 524), ("service-life", 898)):
        lifeline(d, name, x)

    message(d, "send", [(152, 225), (524, 225)], BLUE,
            "① POST /operations", 168, 186, 350, font=8)
    message(d, "forward", [(524, 225), (898, 225)], BLUE,
            "operation_id + payload", 554, 186, 340, font=8)
    card(d, "registered", "② 先登记操作", "ID → 原内容", 762, 266, 272, 96, GREEN, "#c7f0d7")

    # This is server-side waiting before a response, not a delivered message.
    d.box("wait-bar", 886, 368, 24, 417, ORANGE, "#ffddb4")
    d.elements[-1]["roughness"] = 1
    label(d, "delay", "③ 原 POST\n响应前等待", 710, 396, 174, 24, ORANGE)
    label(d, "release", "清理时才放行", 710, 754, 174, 23, ORANGE)
    card(d, "timeout", "④ read timeout", "超时配置 0.15 秒\n关原连接 ≠ 操作没发生", 28, 380, 335, 133, ORANGE, "#fff2dc")

    message(d, "query", [(152, 562), (524, 562)], BLUE,
            "⑤ GET /operations/", 168, 527, 350, font=8)
    message(d, "query-forward", [(524, 562), (898, 562)], BLUE,
            "<原 ID 经 URL 编码>", 554, 527, 340, font=8)
    message(d, "found", [(898, 635), (524, 635)], GREEN,
            "⑥ 200 · accepted", 552, 600, 326, font=8)
    message(d, "found-back", [(524, 635), (152, 635)], GREEN,
            "原 ID + payload", 194, 600, 320, font=8)
    card(d, "reconciled", "⑦ 三项匹配后确认", "状态、原 ID、内容一致", 28, 671, 470, 126, GREEN, "#c7f0d7")
    label(d, "host-confirmed", "confirmed_lookup", 44, 752, 241, 23, GREEN, 8)
    label(d, "no-repost", "不再 POST", 294, 752, 183, 23, GREEN)

    card(d, "unknown", "旁注：若查询是 404", "不能证明没发生，也不能证明旧请求不会迟到。\n无法确认 → unknown_stop；不换 ID 盲目重试。",
         35, 805, 999, 128, ORANGE, "#fff2dc")
    label(d, "boundary", "本图只画“登记后超时 → 查询找回”的恢复路径。", 35, 951, 1000, 23, MUTED)
    d.save(Path(__file__).with_name("scene.excalidraw"))


if __name__ == "__main__":
    main()
