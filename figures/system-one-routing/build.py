"""Build the System-1 fast routing + 3-zone harness gate diagram."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from diagram_style import Scene, INK, MUTED

BLUE, PURPLE, GREEN, AMBER, SLATE = "#3478e5", "#7c52e0", "#289e62", "#d97706", "#475569"


def main() -> None:
    d = Scene()
    d.text("title", "快慢思考协同：小模型出有界信号，宿主三段式门控拍板", 28, 22, 1080, 31, INK, 6)
    d.text("subtitle", "把窄域意图分流交给毫秒级 System-1 模型，把灰区刹车、超时降级与工具授权留在确定性代码里", 28, 64, 1080, 20, MUTED)

    # Col 1: User Request + Candidate Directory (x=28..264, w=236)
    d.box("in-box", 28, 174, 240, 260, SLATE, "#f1f5f9")
    d.text("in-step", "01 原始输入", 48, 194, 200, 20, SLATE)
    d.text("in-title", "请求与候选摘要", 48, 228, 200, 22, INK)
    d.text(
        "in-body",
        "• 当前自然语言请求\n• 50+ Skill 简述字典\n• 不塞长正文与工具\n• 异常走超时降级旁路",
        48,
        270,
        200,
        19,
        MUTED,
    )

    # Col 2: System-1 Bounded Model (x=312..592, w=280)
    d.box("s1-box", 312, 174, 280, 260, PURPLE, "#f5f0ff")
    d.text("s1-step", "02 System-1 判断模型", 332, 194, 240, 20, PURPLE)
    d.text("s1-title", "有界原语打分（Jev）", 332, 228, 240, 22, INK)
    d.text(
        "s1-body",
        "• Noul：是否需挂载\n• Choice：最佳键与分布\n• 只吐受限 JSON 信号\n• 锁定版本防阈值漂移",
        332,
        270,
        240,
        19,
        MUTED,
    )

    d.arrow("a-in-s1", [(268, 304), (312, 304)], PURPLE)

    # Col 3: Harness 3-Zone Gate + System-2 Outcomes (x=648..1116, w=468)
    d.box("z-low", 648, 118, 468, 110, SLATE, "#f8fafc")
    d.text("z-low-h", "① 低分直通区（need ≤ 0.20）", 668, 134, 428, 20, SLATE)
    d.text("z-low-b", "判定无需 Skill → 直通主对话，省下上下文预算", 668, 168, 428, 19, INK)

    d.box("z-mid", 648, 250, 468, 110, AMBER, "#fff8eb")
    d.text("z-mid-h", "② 灰区刹车复核（0.20 < need < 0.90）", 668, 266, 428, 20, AMBER)
    d.text("z-mid-b", "宿主拒绝硬猜 → 请用户点选澄清，守住方向准确", 668, 300, 428, 19, INK)

    d.box("z-high", 648, 382, 468, 134, GREEN, "#ebfaf2")
    d.text("z-high-h", "③ 高确信装载区 → 唤醒 System-2 主模型", 668, 398, 428, 20, GREEN)
    d.text(
        "z-high-b",
        "按需注入命中的单个 Skill 正文完成深层推理；\n后续写盘与外部动作仍须穿过宿主审批与沙箱",
        668,
        434,
        428,
        19,
        INK,
    )

    # Arrows from System-1 to 3 Harness Gates
    d.arrow("a-s1-z1", [(592, 252), (648, 173)], SLATE)
    d.arrow("a-s1-z2", [(592, 304), (648, 305)], AMBER)
    d.arrow("a-s1-z3", [(592, 356), (648, 444)], GREEN)

    # Fallback dashed path at bottom
    d.box("fallback-bar", 28, 538, 1088, 62, BLUE, "#eef5ff")
    d.text(
        "fallback-txt",
        "宿主兜底通道：若 System-1 接口超时或报错，捕获异常直接回退常规主流程，绝不因前置路由故障卡死对话",
        48,
        558,
        1048,
        19,
        BLUE,
    )
    d.arrow("a-fb", [(452, 434), (452, 538)], BLUE)
    d.elements[-1]["strokeStyle"] = "dashed"

    for element in d.elements:
        if element["type"] in {"rectangle", "arrow"}:
            element["roughness"] = 1
        if element["type"] == "arrow":
            element["strokeWidth"] = 3

    d.save(ROOT / "figures/system-one-routing/scene.excalidraw")


if __name__ == "__main__":
    main()
