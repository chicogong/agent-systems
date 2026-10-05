"""Rebuild the introductory loop, including the non-delivery exit."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from diagram_style import Scene, INK, MUTED

BLUE, PURPLE, GREEN, AMBER, RED = "#3578e5", "#8056e8", "#2fa86a", "#e88816", "#b15d49"


def main() -> None:
    d = Scene()
    d.box("loop-lane", 236, 175, 544, 345, "#cbd5e1", "#f8f6ff")
    d.elements[-1]["strokeStyle"] = "dashed"
    for key, x, y, w, h, stroke, fill in [
        ("task", 28, 255, 176, 125, BLUE, "#eaf3ff"),
        ("decision", 268, 270, 144, 120, PURPLE, "#f0eaff"),
        ("tool", 436, 270, 144, 120, AMBER, "#fff4df"),
        ("observation", 604, 270, 144, 120, GREEN, "#e7f7ee"),
        ("check", 820, 205, 176, 125, BLUE, "#eaf3ff"),
        ("deliver", 820, 385, 176, 125, GREEN, "#e7f7ee"),
        ("stop", 820, 590, 176, 105, RED, "#fff0e9"),
    ]:
        d.box(key, x, y, w, h, stroke, fill)
    for key, points, color in [
        ("task-to-decision", [(204, 320), (268, 320)], BLUE),
        ("decision-to-tool", [(412, 330), (436, 330)], PURPLE),
        ("tool-to-observation", [(580, 330), (604, 330)], AMBER),
        ("observation-to-check", [(748, 305), (820, 267)], GREEN),
        ("check-to-deliver", [(908, 330), (908, 385)], BLUE),
        ("check-failed-correctable", [(880, 205), (880, 157), (340, 157), (340, 270)], AMBER),
        ("feedback", [(680, 390), (680, 455), (340, 455), (340, 390)], PURPLE),
        ("check-cannot-continue", [(820, 310), (795, 310), (795, 642), (820, 642)], RED),
    ]:
        d.arrow(key, points, color)
        if key in {"check-failed-correctable", "feedback", "check-cannot-continue"}:
            d.elements[-1]["strokeStyle"] = "dashed"
    d.text("title", "Agent 一步步完成任务", 28, 28, 960, 37, INK, 6)
    d.text("loop-label", "选择、执行、观察", 370, 190, 315, 23, PURPLE)
    for key, x, y, w, title, detail, size in [
        ("task", 46, 274, 140, "用户任务", "目标 · 权限\n完成标准", 25),
        ("decision", 284, 289, 120, "模型决策", "选择下一步", 23),
        ("tool", 452, 289, 120, "工具执行", "按权限读写", 23),
        ("observation", 620, 289, 120, "观察结果", "输出 · 错误", 23),
        ("check", 838, 224, 140, "核对结果", "来源 · 测试", 24),
        ("deliver", 838, 404, 140, "交付", "结果与依据", 24),
        ("stop", 838, 608, 140, "停止并说明", "失败 / 未完成", 22),
    ]:
        d.text(key + "-title", title, x, y, w, size)
        d.text(key + "-detail", detail, x, y + (38 if key == "stop" else 48), w, 18, MUTED)
    d.text("feedback-label", "未解决 → 继续", 440, 465, 208, 18, PURPLE)
    d.text("verified-label", "通过", 918, 341, 64, 18, BLUE)
    d.text("failed-label", "未通过、还能修正 → 再试", 500, 127, 336, 18, "#b66e0a")
    d.text("cannot-continue-label", "无法继续", 830, 549, 155, 18, RED)
    d.text("stop-example", "任一步用完预算、缺少许可或无法修正时，\n都可停止，说明原因和没做完的部分。", 268, 590, 488, 18, MUTED)
    for element in d.elements:
        if element["type"] in {"rectangle", "arrow"}:
            element["roughness"] = 1
        if element["type"] == "arrow":
            element["strokeWidth"] = 3
    d.save(ROOT / "figures/agent-loop/scene.excalidraw")


if __name__ == "__main__":
    main()
