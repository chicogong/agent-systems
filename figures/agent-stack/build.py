"""A task crosses interface, harness, model, skill and tool boundaries."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from diagram_style import Scene  # noqa: E402

INK = "#203044"
MUTED = "#516173"
BLUE = "#4a9eed"
PURPLE = "#8b5cf6"
GREEN = "#18a76b"
ORANGE = "#e58d12"


def label(d: Scene, name: str, value: str, x: int, y: int, width: int,
          size: int = 24, color: str = INK):
    d.text(name, value, x, y, width, size, color, 8)


def box(d: Scene, name: str, x: int, y: int, width: int, height: int,
        color: str, fill: str, text: str, size: int = 24):
    d.box(name, x, y, width, height, color, fill)
    d.elements[-1]["roughness"] = 2
    d.elements[-1]["strokeWidth"] = 2.5
    lines = text.splitlines()
    text_height = len(lines) * size * 1.25
    label(d, name + "-label", text, x + 16,
          int(y + (height - text_height) / 2), width - 30, size)


def arrow(d: Scene, name: str, points: list[tuple[int, int]], color: str,
          dashed: bool = False):
    d.arrow(name, points, color)
    d.elements[-1]["roughness"] = 2
    d.elements[-1]["strokeWidth"] = 3
    d.elements[-1]["strokeStyle"] = "dashed" if dashed else "solid"


def build():
    d = Scene()

    # The pale boundary denotes orchestration, not a claim that every product
    # has one literal process or class named Harness.
    d.box("harness-boundary", 256, 103, 614, 542, "#85b7a7", "#f5fbf8")
    d.elements[-1]["opacity"] = 65
    d.elements[-1]["roughness"] = 1
    d.elements[-1]["strokeWidth"] = 2
    d.elements[-1]["strokeStyle"] = "dashed"
    label(d, "harness-name", "Harness · 运行与控制", 279, 119, 550, 25, "#217055")

    box(d, "cli", 34, 276, 180, 92, BLUE, "#d9ecff", "CLI / IDE\n接收任务", 23)
    arrow(d, "request", [(214, 320), (295, 320)], BLUE)

    box(d, "skill", 312, 187, 222, 74, GREEN, "#dcf8ec", "Skill · 流程知识", 22)
    arrow(d, "skill-to-context", [(405, 261), (405, 315)], GREEN, True)
    label(d, "skill-edge", "按需读", 421, 274, 112, 18, GREEN)

    box(d, "context", 294, 316, 185, 93, BLUE, "#d9ecff", "装配上下文", 23)
    arrow(d, "context-to-model", [(479, 363), (540, 363)], PURPLE)
    box(d, "model", 540, 316, 157, 93, PURPLE, "#e5d8ff", "生成式模型\n建议下一步", 21)
    arrow(d, "model-to-gate", [(697, 363), (737, 363)], PURPLE)
    box(d, "gate", 737, 308, 115, 108, ORANGE, "#ffe2b8", "权限\n与路由", 22)

    arrow(d, "gate-to-local", [(852, 332), (926, 282)], ORANGE)
    box(d, "local", 926, 234, 187, 95, BLUE, "#d9ecff", "本地工具\n执行 / 验证", 22)

    arrow(d, "gate-to-mcp", [(852, 393), (928, 464)], ORANGE)
    box(d, "mcp", 928, 464, 187, 95, GREEN, "#dcf8ec", "MCP Server\n工具 / 资源", 21)

    # Feedback is deliberately one loop: results are observations, not a
    # second authority that can bypass the harness.
    arrow(d, "observation", [(1113, 282), (1145, 282), (1145, 579),
                              (389, 579), (389, 409)], PURPLE)
    arrow(d, "remote-result", [(1115, 512), (1145, 512)], PURPLE)
    d.elements[-1]["endArrowhead"] = None
    label(d, "observation-text", "工具结果 → 下一轮观察", 514, 597, 382, 20, MUTED)

    label(d, "margin-note", "同一项任务；界面、模型、知识与连接都可替换。", 45, 688, 1030, 22, MUTED)
    d.save(Path(__file__).with_name("scene.excalidraw"))


if __name__ == "__main__":
    build()
