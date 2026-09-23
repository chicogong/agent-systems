"""Build the local-MemFS memory map from native Excalidraw elements."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from diagram_style import Scene  # noqa: E402

BLUE = "#4a9eed"
GREEN = "#16a34a"
INK = "#14213d"
MUTED = "#475569"
ORANGE = "#f59e0b"
PURPLE = "#8b5cf6"


def main() -> None:
    d = Scene()
    d.text("title", "Letta Code：记忆存放处 ≠ 当前上下文", 38, 25, 1170, 33, INK, 8)
    d.text("subtitle", "以 local MemFS v1 为例：先区分磁盘中的长期状态，再看哪些内容进入本轮提示。", 40, 78, 1160, 19, MUTED, 8)

    # Two-column placement map, then a short lifecycle strip. This is
    # intentionally not the layered pipeline used by the Pi diagrams.
    d.box("disk-panel", 36, 143, 559, 488, "#bfd5f5", "#f5f9ff")
    d.box("context-panel", 632, 143, 559, 488, "#d7c8ff", "#faf7ff")
    d.text("disk-head", "01  持久状态：MemFS 与历史", 62, 166, 500, 24, BLUE)
    d.text("context-head", "02  模型本轮可见的上下文", 658, 166, 500, 24, PURPLE)

    d.box("core", 72, 235, 480, 104, BLUE, "#a5d8ff")
    d.text("core-title", "system/*.md", 94, 255, 425, 25, INK)
    d.text("core-body", "核心记忆块：身份、偏好、索引", 94, 292, 430, 18, MUTED, 8)

    d.box("external", 72, 385, 480, 104, GREEN, "#c3fae8")
    d.text("external-title", "外部文件 / skills", 94, 405, 430, 25, INK)
    d.text("external-body", "正文在外部；需要时再读取", 94, 442, 430, 18, MUTED, 8)

    d.box("history", 72, 535, 480, 66, ORANGE, "#fff3bf")
    d.text("history-label", "会话历史 / recall：另一路状态", 94, 554, 430, 21, INK)

    d.box("prompt", 668, 235, 480, 156, PURPLE, "#d0bfff")
    d.text("prompt-title", "system prompt", 690, 256, 424, 26, INK)
    d.text("prompt-body", "基础指令 + 核心记忆块\n外部文件正文不默认内联", 690, 299, 420, 19, INK, 8)

    d.box("window", 668, 451, 480, 150, PURPLE, "#e5dbff")
    d.text("window-title", "当前 conversation", 690, 471, 424, 25, INK)
    d.text("window-body", "最近消息 + 较早消息的摘要\n需要旧信息时检索 recall", 690, 511, 420, 19, INK, 8)

    d.arrow("core-to-prompt", [(552, 286), (609, 286), (609, 280), (668, 280)], BLUE)
    d.arrow("external-to-window", [(552, 437), (608, 437), (608, 500), (668, 500)], GREEN)
    d.arrow("history-to-window", [(552, 567), (668, 567)], ORANGE)
    d.text("core-edge", "默认在场", 555, 243, 100, 18, BLUE)
    d.text("external-edge", "工具读取", 560, 461, 95, 18, GREEN)
    d.text("history-edge", "检索 / 摘要", 554, 535, 110, 18, ORANGE)

    d.box("lifecycle", 36, 678, 1155, 176, "#cbd5e1", "#f8fafc")
    d.text("life-head", "修改记忆后，何时可见？路径不同", 62, 695, 650, 22, INK, 8)
    d.text("tool-write", "memory() 工具写入", 72, 733, 285, 18, BLUE, 8)
    d.arrow("tool-commit-arrow", [(331, 750), (392, 750)], BLUE)
    d.text("tool-commit", "commitMemoryWrite 提交", 410, 733, 400, 18, BLUE, 8)
    d.text("worker-merge", "memory worker 合并", 72, 770, 300, 18, PURPLE, 8)
    d.arrow("worker-sync-arrow", [(331, 787), (392, 787)], PURPLE)
    d.text("worker-sync", "同步", 410, 770, 100, 18, PURPLE, 8)
    d.arrow("worker-recompile-arrow", [(490, 787), (551, 787)], PURPLE)
    d.text("worker-recompile", "能力允许时重编译提示", 569, 770, 430, 18, PURPLE, 8)
    d.text("life-foot", "已编译的当前回合提示不会被文件编辑即时改写；不是每条写入都走同一重编译路径。", 72, 817, 1050, 18, MUTED, 8)
    d.text("scope", "图示范围：local MemFS v1；API-backed v2 的目录布局另见正文。", 40, 877, 1150, 18, MUTED, 8)

    for element in d.elements:
        if element["type"] == "rectangle":
            element["roughness"] = 1
        elif element["type"] == "arrow":
            element.update(roughness=1, strokeWidth=3)

    d.save(Path(__file__).with_name("scene.excalidraw"))


if __name__ == "__main__":
    main()
