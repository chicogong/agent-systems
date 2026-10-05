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

    d.text("title", "一条测试命令：检查许可，运行并核对", 28, 24, 990, 36, INK, 8)
    d.text("subtitle", "示例：修复重复订单后，运行相关测试。", 30, 80, 982, 23, MUTED, 8)
    d.text("claude-label", "Claude Code · 权限规则与可选 Bash 沙箱", 48, 147, 925, 25, VIOLET, 8)
    d.text("codex-label", "Codex · 先决定许可，再选执行沙箱", 48, 467, 925, 25, BLUE, 8)

    d.text("claude-proposal-text", "模型提出\n运行测试", 72, 233, 185, 26, INK, 8)
    d.text("claude-gate-text", "检查权限规则／模式\n按配置使用 Bash 沙箱", 357, 221, 291, 25, INK, 8)
    d.text("claude-result-text", "运行后返回输出\n核对测试结果", 752, 233, 225, 25, INK, 8)

    d.text("codex-proposal-text", "模型提出\nexec_command", 72, 553, 185, 24, INK, 8)
    d.text("codex-gate-text", "核对参数与策略\n审批决定 → 选择沙箱", 357, 541, 291, 25, INK, 8)
    d.text("codex-result-text", "运行后返回输出\n核对测试结果", 752, 553, 225, 25, INK, 8)

    d.text("claude-blocked-text", "许可拒绝／沙箱阻断 → 说明原因", 558, 357, 420, 22, RED, 8)
    d.text("codex-blocked-text", "许可拒绝／沙箱阻断 → 说明原因", 558, 677, 420, 22, RED, 8)

    for element in d.elements:
        if element["type"] == "arrow" and element["strokeStyle"] != "dashed":
            element["strokeWidth"] = 3
        if element["type"] == "rectangle":
            element["roughness"] = 1
    d.save(Path(__file__).with_name("scene.excalidraw"))


if __name__ == "__main__":
    main()
