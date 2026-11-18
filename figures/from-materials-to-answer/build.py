"""Build the onboarding diagram: turning raw materials into a cited answer."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from diagram_style import Scene, INK, MUTED

BLUE, PURPLE, GREEN, AMBER = "#3578e5", "#7c52e0", "#289e62", "#d97706"


def main() -> None:
    d = Scene()
    d.text("title", "从零散材料到可靠交付：有出处才写结论，缺信息单列待查", 28, 24, 1020, 33, INK, 6)
    d.text("subtitle", "① 先给明确的编号材料   →   ② 按任务卡逐条核对   →   ③ 分列「有据结论」与「待查缺口」", 28, 68, 1020, 20, MUTED)

    # Column 1: Raw Materials (x=28..304, w=276)
    d.box("src-group", 28, 118, 276, 442, "#cbd5e1", "#f8fafc")
    d.elements[-1]["strokeStyle"] = "dashed"
    d.text("src-header", "01 原始材料（带编号）", 48, 134, 236, 21, BLUE)

    sources = [
        ("d1", 174, "D1 日程通知", "周六 14:00 开始"),
        ("d2", 298, "D2 场地说明", "地点在图书馆二楼\n（未提能否停车）"),
        ("d3", 422, "D3 报名规则", "周五 18:00 前填表\n（未附表单链接）"),
    ]
    for key, y, heading, detail in sources:
        d.box(key, 48, y, 236, 102, BLUE, "#eaf3ff")
        d.text(f"{key}-t", heading, 66, y + 16, 200, 21, INK)
        d.text(f"{key}-d", detail, 66, y + 48, 200, 19, MUTED)

    # Column 2: Extraction & Grounding Check (x=376..648, w=272)
    d.box("process", 376, 192, 272, 290, PURPLE, "#f3eeff")
    d.text("proc-step", "02 提取与核对", 398, 212, 228, 21, PURPLE)
    d.text("proc-title", "按任务卡逐项对齐", 398, 248, 228, 23, INK)
    d.text(
        "proc-items",
        "• 核对时间、地点、报名\n• 每句结论标明材料号\n• 原文没写的绝不脑补\n• 只整理草稿，不外发",
        398,
        292,
        232,
        19,
        MUTED,
    )

    # Column 3: Two-part Deliverable (x=760..1076, w=316)
    d.box("out-verified", 760, 132, 316, 208, GREEN, "#e7f7ee")
    d.text("out-v-step", "03 可直接交付的结论", 782, 150, 272, 21, GREEN)
    d.text("out-v-title", "带出处的准确答复", 782, 184, 272, 23, INK)
    d.text(
        "out-v-body",
        "• 周六 14:00 开始 [D1]\n• 地点在图书馆二楼 [D2]\n• 周五 18:00 前报名 [D3]",
        782,
        226,
        276,
        19,
        MUTED,
    )

    d.box("out-gaps", 760, 372, 316, 184, AMBER, "#fff6e5")
    d.text("out-g-step", "04 诚实留白与下一步", 782, 390, 272, 21, AMBER)
    d.text("out-g-title", "待确认清单（不瞎猜）", 782, 424, 272, 23, INK)
    d.text(
        "out-g-body",
        "• 缺报名链接 → 问主办方\n• 未提停车位 → 出发前查",
        782,
        468,
        276,
        19,
        MUTED,
    )

    # Arrows
    for key, pts, color, dashed in [
        ("a-d1", [(284, 225), (376, 285)], BLUE, False),
        ("a-d2", [(284, 349), (376, 338)], BLUE, False),
        ("a-d3", [(284, 473), (376, 392)], BLUE, False),
        ("a-ok", [(648, 288), (760, 236)], GREEN, False),
        ("a-gap", [(648, 392), (760, 464)], AMBER, True),
    ]:
        d.arrow(key, pts, color)
        if dashed:
            d.elements[-1]["strokeStyle"] = "dashed"

    d.text("lbl-ok", "原文有据", 662, 220, 92, 19, GREEN)
    d.text("lbl-gap", "原文缺失", 662, 444, 92, 19, AMBER)

    for element in d.elements:
        if element["type"] in {"rectangle", "arrow"}:
            element["roughness"] = 1
        if element["type"] == "arrow":
            element["strokeWidth"] = 3

    d.save(ROOT / "figures/from-materials-to-answer/scene.excalidraw")


if __name__ == "__main__":
    main()
