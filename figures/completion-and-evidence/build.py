"""Build the completion & evidence verification diagram (Reader Trial C)."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from diagram_style import Scene, INK, MUTED

BLUE, PURPLE, GREEN, AMBER, RED = "#3578e5", "#7c52e0", "#289e62", "#d97706", "#c24135"


def main() -> None:
    d = Scene()
    d.text("title", "Agent 说「已完成」时该查什么：把口头宣告变成三件套核验", 28, 24, 1080, 33, INK, 6)
    d.text("subtitle", "回合正常结束 ≠ 需求全部满足；对照原始约束核查「实际改动、完整断言、操作边界」才能签收", 28, 68, 1080, 20, MUTED)

    # Left: Task Contract + Agent Claim (x=28..284, w=256)
    d.box("req", 28, 140, 256, 186, BLUE, "#eaf3ff")
    d.text("req-step", "01 原始任务约束", 48, 158, 216, 20, BLUE)
    d.text("req-title", "既要改对，也要守边界", 48, 190, 216, 22, INK)
    d.text(
        "req-body",
        "• timeout 改为 5 秒\n• 保持 retries = 3\n• 跑测试，不提交推送",
        48,
        230,
        216,
        19,
        MUTED,
    )

    d.box("claim", 28, 378, 256, 168, PURPLE, "#f3eeff")
    d.text("claim-step", "02 Agent 结束回合", 48, 396, 216, 20, PURPLE)
    d.text("claim-title", "声称「已改好且测试过」", 48, 428, 216, 22, INK)
    d.text("claim-body", "仅凭结束事件或口头总结，\n看不出是否误伤其他规则", 48, 468, 216, 19, MUTED)

    # Top Trap Path: False Completion (x=376..748, w=372)
    d.box("trap", 376, 122, 372, 132, RED, "#fff1ef")
    d.elements[-1]["strokeStyle"] = "dashed"
    d.text("trap-title", "假完成陷阱：局部测试掩盖连带破坏", 398, 142, 332, 21, RED)
    d.text(
        "trap-body",
        "test_timeout 通过（只测了 5 秒），\n但 diff 里 retries 被改成了 0！",
        398,
        180,
        332,
        19,
        MUTED,
    )

    # Center Verification Gate: 3 Evidence Checks (x=376..748, w=372)
    d.box("gate", 376, 290, 372, 276, AMBER, "#fff8eb")
    d.text("gate-step", "03 逐项核对客观记录", 398, 310, 332, 21, AMBER)
    d.text("gate-1", "① 查文件差异：5 秒生效、重试仍为 3", 398, 350, 336, 19, INK)
    d.text("gate-2", "② 查测试断言：同时锁住新值与保留项", 398, 394, 336, 19, INK)
    d.text("gate-3", "③ 查边界记录：改动不越界，无推送", 398, 438, 336, 19, INK)
    d.text("gate-note", "缺记录的条目标「待核对」，不标已完成", 398, 496, 336, 19, MUTED)

    # Right Outcomes (x=844..1128, w=284)
    d.box("rework", 844, 134, 284, 142, RED, "#fff1ef")
    d.text("rw-title", "打回补改 / 补断言", 866, 154, 240, 22, RED)
    d.text("rw-body", "恢复 retries = 3，\n把保留规则写进测试", 866, 194, 240, 19, MUTED)

    d.box("accept", 844, 338, 284, 228, GREEN, "#e7f7ee")
    d.text("ac-step", "04 可信交付报告", 866, 358, 240, 20, GREEN)
    d.text("ac-title", "结论与证据一一对应", 866, 390, 240, 22, INK)
    d.text(
        "ac-body",
        "• 已改：文件路径与 diff\n• 已测：命令、退出码与断言\n• 待确认：未测的线上环境",
        866,
        434,
        244,
        19,
        MUTED,
    )

    # Arrows
    for key, pts, color, dashed in [
        ("a-req-gate", [(284, 250), (376, 360)], BLUE, False),
        ("a-claim-trap", [(284, 412), (322, 412), (322, 188), (376, 188)], RED, True),
        ("a-claim-gate", [(284, 464), (376, 464)], PURPLE, False),
        ("a-trap-rw", [(748, 188), (844, 188)], RED, True),
        ("a-gate-rw", [(748, 346), (804, 346), (804, 232), (844, 232)], RED, True),
        ("a-gate-ac", [(748, 464), (844, 464)], GREEN, False),
    ]:
        d.arrow(key, pts, color)
        if dashed:
            d.elements[-1]["strokeStyle"] = "dashed"

    d.text("lbl-blind", "轻信总结", 292, 156, 84, 19, RED)
    d.text("lbl-fail", "查出漏项", 752, 356, 84, 19, RED)
    d.text("lbl-pass", "三项齐备", 756, 434, 84, 19, GREEN)

    for element in d.elements:
        if element["type"] in {"rectangle", "arrow"}:
            element["roughness"] = 1
        if element["type"] == "arrow":
            element["strokeWidth"] = 3

    d.save(ROOT / "figures/completion-and-evidence/scene.excalidraw")


if __name__ == "__main__":
    main()
