"""Build an A4-readable comparison of one proposed local test command.

The two lanes are teaching projections, not recorded product traces. Codex's
gate maps to the pinned Rust exec_command path; Claude's gate maps to docs.
"""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from diagram_style import Scene  # noqa: E402

INK = "#1e293b"
MUTED = "#475569"
BLUE = "#2563eb"
VIOLET = "#7c3aed"
GREEN = "#16803d"
RED = "#a73f31"


def main() -> None:
    d = Scene()

    d.box("claude-lane", 24, 132, 1008, 302, VIOLET, "#faf7ff")
    d.box("codex-lane", 24, 452, 1008, 302, BLUE, "#f5f9ff")

    # Sequence lines are behind cards; short dashed branches mark conditions.
    for prefix, y, color in (("claude", 266, VIOLET), ("codex", 586, BLUE)):
        d.arrow(f"{prefix}-proposal-to-gate", [(274, y), (336, y)], color)
        d.arrow(f"{prefix}-gate-to-result", [(666, y), (730, y)], color)
        d.arrow(f"{prefix}-blocked", [(501, y + 69), (501, y + 107), (548, y + 107)], RED)
        d.elements[-1]["strokeStyle"] = "dashed"

    d.box("claude-proposal", 52, 214, 222, 104, VIOLET, "#ede4ff")
    d.box("claude-gate", 336, 197, 330, 138, VIOLET, "#e7d9ff")
    d.box("claude-result", 730, 214, 270, 104, GREEN, "#e0f5e9")
    d.box("codex-proposal", 52, 534, 222, 104, BLUE, "#dfecff")
    d.box("codex-gate", 336, 517, 330, 138, BLUE, "#cfe1ff")
    d.box("codex-result", 730, 534, 270, 104, GREEN, "#e0f5e9")

    d.text("title", "同一测试命令，谁让它执行？", 28, 24, 990, 36, INK, 8)
    d.text("subtitle", "示意任务：修订单幂等 Bug；两行均非实测轨迹。", 30, 80, 982, 23, MUTED, 8)
    d.text("claude-label", "Claude Code · 官方文档行为", 48, 147, 925, 25, VIOLET, 8)
    d.text("codex-label", "Codex · 固定源码普通命令路径", 48, 467, 925, 25, BLUE, 8)

    d.text("claude-proposal-text", "模型提出\n运行测试", 72, 233, 185, 26, INK, 8)
    d.text("claude-gate-text", "工具权限规则 / 模式\n可选 Bash 沙箱", 357, 221, 291, 25, INK, 8)
    d.text("claude-result-text", "获准后执行\n返回结果并核对", 752, 233, 225, 25, INK, 8)

    d.text("codex-proposal-text", "模型提出\nexec_command", 72, 553, 185, 24, INK, 8)
    d.text("codex-gate-text", "Handler → 策略\n审批 → 首次沙箱", 357, 541, 291, 25, INK, 8)
    d.text("codex-result-text", "允许后执行\n返回结果并核对", 752, 553, 225, 25, INK, 8)

    d.text("claude-blocked-text", "拒绝 / 阻断 → 记录未完成", 558, 357, 420, 22, RED, 8)
    d.text("codex-blocked-text", "拒绝 / 阻断 → 记录未完成", 558, 677, 420, 22, RED, 8)

    for element in d.elements:
        if element["type"] == "arrow" and element["strokeStyle"] != "dashed":
            element["strokeWidth"] = 3
        if element["type"] == "rectangle":
            element["roughness"] = 1
    d.save(Path(__file__).with_name("scene.excalidraw"))


if __name__ == "__main__":
    main()
