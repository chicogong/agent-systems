"""Build a gate/exit map for OpenClaw Gateway's explicit-session agent RPC."""

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from diagram_style import Scene  # noqa: E402


INK = "#223046"
MUTED = "#5e6b7d"
BLUE = "#286cb4"
PURPLE = "#7058bb"
AMBER = "#af7415"
TEAL = "#178077"
GREEN = "#278455"
RED = "#ba5252"


def gate(scene: Scene, name: str, x: int, w: int, color: str,
         step: str, title: str, detail: str):
    scene.box(name, x, 247, w, 190, color, "#ffffff")
    scene.elements[-1]["roundness"] = None
    scene.elements[-1]["strokeWidth"] = 2
    scene.box(f"{name}-bar", x, 247, w, 9, color, color)
    scene.elements[-1]["roundness"] = None
    scene.elements[-1]["strokeWidth"] = 0
    scene.text(f"{name}-step", step, x + 13, 263, w - 26, 24, color, 8)
    scene.text(f"{name}-title", title, x + 13, 298, w - 26, 29, color, 6)
    scene.text(f"{name}-detail", detail, x + 13, 340, w - 26, 24, INK, 6)


def arrow(scene: Scene, name: str, points: list[tuple[int, int]], color: str,
          dashed: bool = False):
    scene.arrow(name, points, color)
    scene.elements[-1]["strokeWidth"] = 3
    scene.elements[-1]["strokeStyle"] = "dashed" if dashed else "solid"


def build():
    d = Scene()
    d.text("title", "OpenClaw Gateway：先认准会话，再启动运行", 42, 28, 1260, 36, INK, 6)
    d.text("subtitle", "仅展示 agent RPC 携带显式 sessionKey 的路由／授权关口", 44, 82, 1240, 24, MUTED, 6)

    # A single routing rail with explicit rejection exits; not an architecture stack.
    d.text("preflight", "Gateway 参数验证 + preflight", 54, 187, 420, 24, MUTED, 6)
    gate(d, "request", 40, 175, BLUE, "INPUT", "agent RPC", "sessionKey\nagentId?\ncaller")
    gate(d, "owner", 245, 200, PURPLE, "GATE 01", "解析 owner", "key 前缀 / store\n核对 agentId")
    gate(d, "target", 475, 200, AMBER, "GATE 02", "检查目标", "约束 / 可用性\nreserveDedupe")
    gate(d, "canonical", 705, 200, TEAL, "GATE 03", "规范化会话", "canonicalKey\n授权前规范化")
    gate(d, "authorize", 935, 200, GREEN, "GATE 04", "授权真实目标", "session creation\n+ mutation")
    gate(d, "handoff", 1165, 148, BLUE, "NEXT", "交给运行", "admission /\ndispatch")

    for name, x1, x2, color in [
        ("a1", 215, 245, PURPLE),
        ("a2", 445, 475, AMBER),
        ("a3", 675, 705, TEAL),
        ("a4", 905, 935, GREEN),
        ("a5", 1135, 1165, BLUE),
    ]:
        arrow(d, name, [(x1, 335), (x2, 335)], color)

    for name, x, w, text in [
        ("stop-owner", 245, 200, "格式错误 /\nowner 冲突"),
        ("stop-target", 475, 200, "约束冲突 /\n会话不可用"),
        ("stop-canonical", 705, 200, "无法准备目标会话"),
        ("stop-authorize", 935, 200, "无创建 /\n修改权限"),
    ]:
        arrow(d, f"{name}-arrow", [(x + w // 2, 437), (x + w // 2, 495)], RED)
        d.text(name, text, x + 2, 510, w - 4, 24, RED, 6)

    d.box("legend", 44, 614, 1269, 72, "#d9e3ed", "#f6f9fc")
    d.elements[-1]["strokeWidth"] = 1
    d.text("legend-text", "请求中的 key ≠ 规范化后的授权目标；路由通过 ≠ agent 已执行。",
           67, 632, 1200, 24, INK, 6)
    d.save(Path(__file__).with_name("scene.excalidraw"))


if __name__ == "__main__":
    build()
