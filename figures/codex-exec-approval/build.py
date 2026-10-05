"""Build a native Excalidraw decision map for Codex's exec_command path."""

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from diagram_style import Scene  # noqa: E402


INK = "#14213d"
MUTED = "#475569"
TEAL = "#06b6d4"
VIOLET = "#8b5cf6"
AMBER = "#f59e0b"
RED = "#ef4444"
GREEN = "#16a34a"


def line(scene: Scene, name: str, points: list[tuple[int, int]], color: str, dashed=False):
    scene.arrow(name, points, color)
    scene.elements[-1].update(strokeWidth=3, roughness=1)
    if dashed:
        scene.elements[-1]["strokeStyle"] = "dashed"


def tile(scene: Scene, name: str, x: int, y: int, w: int, h: int,
         stroke: str, fill: str, title: str, detail: str, detail_size: int = 22):
    scene.box(name, x, y, w, h, stroke, fill)
    scene.elements[-1].update(strokeWidth=2, roughness=1)
    scene.text(f"{name}-title", title, x + 19, y + 13, w - 38, 25, stroke, 8)
    multi_line = "\n" in detail
    scene.text(f"{name}-detail", detail, x + 19, y + (49 if multi_line else 56),
               w - 38, 21 if multi_line else detail_size, INK, 8)


def build():
    d = Scene()
    # A decision map, not Pi's layered architecture layout: the branch shape
    # makes the stop and conditional retry paths visible before prose.
    d.text("title", "Codex：先决定许可，再选择沙箱运行", 56, 33, 1180, 35, INK, 8)
    d.text("subtitle", "普通命令 exec_command：检查请求 → 审批决定 → 执行尝试", 58, 89, 1150, 22, MUTED, 8)

    d.text("stage-1", "01  进入工具", 69, 148, 250, 22, TEAL, 8)
    d.text("stage-2", "02  作出审批决定", 379, 148, 250, 22, VIOLET, 8)
    d.text("stage-3", "03  执行与返回", 935, 550, 275, 22, GREEN, 8)

    tile(d, "model", 65, 182, 260, 112, TEAL, "#c9f4f4",
         "提出运行命令", "exec_command(cmd)", detail_size=21)
    tile(d, "handler", 375, 182, 260, 112, TEAL, "#c9f4f4",
         "核对请求", "Handler\n环境／参数／权限")
    tile(d, "policy", 685, 182, 260, 112, VIOLET, "#d0bfff",
         "决定执行许可", "ExecPolicy\n检查规则与策略")
    line(d, "model-handler", [(325, 235), (375, 235)], TEAL)
    line(d, "handler-policy", [(635, 235), (685, 235)], VIOLET)

    # Three outcomes are spatially distinct; Skip does not mean unsandboxed.
    tile(d, "skip", 100, 372, 275, 110, GREEN, "#c3fae8",
         "免普通询问", "Skip\n仍按配置选执行范围")
    tile(d, "ask", 505, 372, 275, 110, AMBER, "#fff3bf",
         "等待批准", "NeedsApproval\n批准继续／拒绝停止")
    tile(d, "forbid", 910, 372, 275, 110, RED, "#ffe3e3",
         "禁止执行", "Forbidden\n执行前返回")
    line(d, "policy-skip", [(730, 294), (730, 316), (237, 316), (237, 372)], GREEN)
    line(d, "policy-ask", [(805, 294), (805, 345), (643, 345), (643, 372)], AMBER)
    line(d, "policy-forbid", [(885, 294), (885, 330), (1048, 330), (1048, 372)], RED)

    tile(d, "attempt", 490, 594, 410, 112, VIOLET, "#e5dbff",
         "选择沙箱并首次运行", "执行编排器选择运行时")
    line(d, "skip-attempt", [(237, 482), (237, 649), (490, 649)], GREEN)
    line(d, "ask-attempt", [(643, 482), (643, 594)], AMBER)
    d.text("approved", "批准", 660, 530, 80, 22, "#9a6700", 8)

    tile(d, "success", 95, 794, 270, 102, GREEN, "#c3fae8",
         "返回执行结果", "输出或进程会话")
    tile(d, "denied", 490, 794, 270, 102, RED, "#ffe3e3",
         "沙箱拒绝访问", "未满足重试条件则返回")
    tile(d, "retry", 885, 794, 315, 102, AMBER, "#fff3bf",
         "符合条件后重试", "必要时再审批，然后运行")
    line(d, "attempt-success", [(550, 706), (550, 747), (230, 747), (230, 794)], GREEN)
    line(d, "attempt-denied", [(740, 706), (740, 749), (625, 749), (625, 794)], RED)
    line(d, "denied-retry", [(760, 846), (885, 846)], AMBER, dashed=True)
    d.text("conditional", "可重试", 774, 807, 110, 22, "#9a6700", 8)
    d.save(Path(__file__).with_name("scene.excalidraw"))


if __name__ == "__main__":
    build()
