"""Build a native Excalidraw decision map for Codex's exec_command path."""

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from diagram_style import Scene  # noqa: E402


INK = "#202735"
MUTED = "#596375"
TEAL = "#087d86"
VIOLET = "#7354c3"
AMBER = "#bd760d"
RED = "#c44c54"
GREEN = "#22885a"


def line(scene: Scene, name: str, points: list[tuple[int, int]], color: str, dashed=False):
    scene.arrow(name, points, color)
    scene.elements[-1]["strokeWidth"] = 3
    if dashed:
        scene.elements[-1]["strokeStyle"] = "dashed"


def tile(scene: Scene, name: str, x: int, y: int, w: int, h: int,
         stroke: str, fill: str, title: str, detail: str):
    scene.box(name, x, y, w, h, stroke, fill)
    scene.elements[-1]["strokeWidth"] = 2
    scene.text(f"{name}-title", title, x + 19, y + 15, w - 38, 24, stroke, 6)
    scene.text(f"{name}-detail", detail, x + 19, y + 53, w - 38, 18, INK, 6)


def build():
    d = Scene()
    # A decision map, not Pi's layered architecture layout: the branch shape
    # makes the stop and conditional retry paths visible before prose.
    d.text("title", "Codex：一条命令怎样通过执行边界？", 56, 33, 1180, 37, INK, 6)
    d.text("subtitle", "exec_command 的审批决定、首次沙箱尝试和停止路径（固定源码 c44deff7）", 58, 89, 1150, 19, MUTED, 6)

    d.text("stage-1", "01  进入工具", 69, 148, 250, 19, TEAL, 8)
    d.text("stage-2", "02  决策闸门", 379, 148, 250, 19, VIOLET, 8)
    d.text("stage-3", "03  执行与返回", 494, 550, 300, 19, GREEN, 8)

    tile(d, "model", 65, 182, 245, 106, TEAL, "#eaf7f6",
         "模型请求", "exec_command(cmd)")
    tile(d, "handler", 375, 182, 245, 106, TEAL, "#eaf7f6",
         "Handler 预处理", "环境 · 参数 · 权限")
    tile(d, "policy", 685, 182, 245, 106, VIOLET, "#f2edfb",
         "ExecPolicy", "规则 + 策略 → 决定")
    line(d, "model-handler", [(310, 235), (375, 235)], TEAL)
    line(d, "handler-policy", [(620, 235), (685, 235)], VIOLET)

    # Three outcomes are spatially distinct; Skip does not mean unsandboxed.
    tile(d, "skip", 100, 372, 275, 110, GREEN, "#edf8f0",
         "Skip", "无普通审批 ≠ 无沙箱")
    tile(d, "ask", 505, 372, 275, 110, AMBER, "#fff7e6",
         "NeedsApproval", "批准 → 继续；拒绝 → 停")
    tile(d, "forbid", 910, 372, 275, 110, RED, "#fff0ef",
         "Forbidden", "执行前停止")
    line(d, "policy-skip", [(730, 288), (730, 333), (237, 333), (237, 372)], GREEN)
    line(d, "policy-ask", [(805, 288), (805, 335), (643, 335), (643, 372)], AMBER)
    line(d, "policy-forbid", [(885, 288), (885, 335), (1048, 335), (1048, 372)], RED)

    tile(d, "attempt", 490, 594, 410, 112, VIOLET, "#f2edfb",
         "选择沙箱 · 第一次尝试", "ToolOrchestrator → UnifiedExecRuntime")
    line(d, "skip-attempt", [(237, 482), (237, 649), (490, 649)], GREEN)
    line(d, "ask-attempt", [(643, 482), (643, 594)], AMBER)

    tile(d, "success", 95, 794, 270, 102, GREEN, "#edf8f0",
         "成功", "返回输出或进程会话")
    tile(d, "denied", 490, 794, 270, 102, RED, "#fff0ef",
         "沙箱拒绝", "可能直接返回拒绝")
    tile(d, "retry", 885, 794, 315, 102, AMBER, "#fff7e6",
         "条件满足才重试", "可能再次审批 · 第二次尝试")
    line(d, "attempt-success", [(550, 706), (550, 747), (230, 747), (230, 794)], GREEN)
    line(d, "attempt-denied", [(740, 706), (740, 749), (625, 749), (625, 794)], RED)
    line(d, "denied-retry", [(760, 846), (885, 846)], AMBER, dashed=True)
    d.text("conditional", "仅符合重试条件", 767, 810, 125, 16, AMBER, 6)
    d.text("footer", "来源：Codex Rust core 静态源码。网络审批、平台后端、apply_patch 拦截另论；虚线仅表示条件路径。", 58, 928, 1160, 16, MUTED, 6)
    d.save(Path(__file__).with_name("scene.excalidraw"))


if __name__ == "__main__":
    build()
