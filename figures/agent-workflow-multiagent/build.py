"""Concept map: next-step control and executor count are separate axes."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from diagram_style import Scene  # noqa: E402

INK = "#213047"
MUTED = "#586679"
BLUE = "#357be4"
PURPLE = "#8156db"
GREEN = "#258b69"
ORANGE = "#d8891e"


def box(d: Scene, name: str, x: int, y: int, w: int, h: int,
        label: str, stroke: str, fill: str):
    d.box(name, x, y, w, h, stroke, fill)
    d.elements[-1]["roughness"] = 1
    d.elements[-1]["strokeWidth"] = 2
    d.text(name + "-text", label, x + 15, y + 21, w - 30, 23, INK, 6)


def arrow(d: Scene, name: str, points: list[tuple[int, int]], color: str,
          dashed: bool = False):
    d.arrow(name, points, color)
    d.elements[-1]["strokeWidth"] = 3
    d.elements[-1]["strokeStyle"] = "dashed" if dashed else "solid"
    d.elements[-1]["roughness"] = 1


def build():
    d = Scene()
    d.text("title", "谁决定下一步？", 46, 28, 680, 37, INK, 6)
    d.text("subtitle", "同一个任务可以换控制方式；执行者数量是另一维度", 47, 82, 1160, 23, MUTED, 6)

    d.text("workflow", "预设工作流  ·  路径由程序编排", 48, 158, 630, 25, BLUE, 6)
    box(d, "w1", 50, 207, 224, 89, "运行测试", BLUE, "#e8f3ff")
    box(d, "w2", 354, 207, 224, 89, "解析失败日志", BLUE, "#e8f3ff")
    box(d, "w3", 658, 207, 224, 89, "生成补丁", BLUE, "#e8f3ff")
    box(d, "w4", 962, 207, 224, 89, "校验结果", BLUE, "#e8f3ff")
    for i, x in enumerate((274, 578, 882)):
        arrow(d, f"wa{i}", [(x + 8, 252), (x + 74, 252)], BLUE)
    d.text("w-note", "模型可以参与单步；阶段与分支仍由程序限定", 51, 313, 1110, 21, MUTED, 6)

    d.text("agent", "单 Agent  ·  模型根据观察选择下一步", 48, 380, 730, 25, PURPLE, 6)
    box(d, "a1", 50, 430, 224, 98, "目标与边界", PURPLE, "#f1eaff")
    box(d, "a2", 354, 430, 224, 98, "模型选择动作", PURPLE, "#f1eaff")
    box(d, "a3", 658, 430, 224, 98, "宿主校验 / 执行", ORANGE, "#fff1d7")
    box(d, "a4", 962, 430, 224, 98, "观察 / 验证", GREEN, "#e6f7ed")
    for i, (x, color) in enumerate(((274, PURPLE), (578, ORANGE), (882, GREEN))):
        arrow(d, f"aa{i}", [(x + 8, 479), (x + 74, 479)], color)
    arrow(d, "feedback", [(1065, 528), (1065, 566), (465, 566), (465, 528)], PURPLE)
    d.text("feedback-label", "未完成 / 反馈进入下一轮", 604, 572, 520, 22, PURPLE, 6)

    d.text("multi", "多执行者  ·  拆分与合并是额外问题", 48, 650, 730, 25, GREEN, 6)
    box(d, "m1", 50, 702, 236, 98, "协调者\n拆分 / 对账", GREEN, "#e6f7ed")
    box(d, "m2", 412, 685, 220, 79, "执行者 A", BLUE, "#e8f3ff")
    box(d, "m3", 412, 782, 220, 79, "执行者 B", PURPLE, "#f1eaff")
    box(d, "m4", 766, 702, 236, 98, "合并证据\n处理冲突", GREEN, "#e6f7ed")
    arrow(d, "m-a", [(286, 733), (412, 733)], BLUE)
    arrow(d, "m-b", [(286, 769), (349, 769), (349, 820), (412, 820)], PURPLE)
    arrow(d, "m-c", [(632, 733), (766, 733)], BLUE)
    arrow(d, "m-d", [(632, 820), (693, 820), (693, 769), (766, 769)], PURPLE)
    d.text("m-note", "每个执行者内部仍可采用工作流或 Agent；多个 ≠ 自动更好", 51, 888, 1160, 21, MUTED, 6)

    d.save(Path(__file__).with_name("scene.excalidraw"))


if __name__ == "__main__":
    build()
