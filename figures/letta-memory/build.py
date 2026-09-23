"""Build the local-MemFS memory map from native Excalidraw elements."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from diagram_style import BLUE, GREEN, INK, MUTED, ORANGE, PURPLE, Scene  # noqa: E402


def main() -> None:
    d = Scene()
    d.text("title", "Letta Code：记忆存放处 ≠ 当前上下文", 38, 25, 1170, 35, INK, 6)
    d.text("subtitle", "以 local MemFS v1 为例：先区分磁盘中的长期状态，再看哪些内容进入本轮提示。", 40, 78, 1160, 19, MUTED, 6)

    # Two-column placement map, then a short lifecycle strip. This is
    # intentionally not the layered pipeline used by the Pi diagrams.
    d.box("disk-panel", 36, 143, 559, 488, "#b8d4ff", "#f5f9ff")
    d.box("context-panel", 632, 143, 559, 488, "#d7c8ff", "#faf7ff")
    d.text("disk-head", "01  持久状态：MemFS 与历史", 62, 166, 500, 24, BLUE)
    d.text("context-head", "02  模型本轮可见的上下文", 658, 166, 500, 24, PURPLE)

    d.box("core", 72, 235, 480, 104, BLUE, "#dcecff")
    d.text("core-title", "system/*.md", 94, 255, 425, 25, INK)
    d.text("core-body", "核心记忆块：身份、偏好、索引", 94, 292, 430, 18, MUTED, 6)

    d.box("external", 72, 385, 480, 104, GREEN, "#ddf5e8")
    d.text("external-title", "外部文件 / skills", 94, 405, 430, 25, INK)
    d.text("external-body", "正文在外部；需要时再读取", 94, 442, 430, 18, MUTED, 6)

    d.box("history", 72, 535, 480, 66, ORANGE, "#fff2d5")
    d.text("history-label", "会话历史 / recall：另一路状态", 94, 554, 430, 21, INK)

    d.box("prompt", 668, 235, 480, 156, PURPLE, "#e9e0ff")
    d.text("prompt-title", "system prompt", 690, 256, 424, 26, INK)
    d.text("prompt-body", "基础指令 + 核心记忆块\n外部文件正文不默认内联", 690, 299, 420, 19, MUTED, 6)

    d.box("window", 668, 451, 480, 150, PURPLE, "#f0ebff")
    d.text("window-title", "当前 conversation", 690, 471, 424, 25, INK)
    d.text("window-body", "最近消息 + 较早消息的摘要\n需要旧信息时检索 recall", 690, 511, 420, 19, MUTED, 6)

    d.arrow("core-to-prompt", [(552, 286), (609, 286), (609, 280), (668, 280)], BLUE)
    d.arrow("external-to-window", [(552, 437), (608, 437), (608, 500), (668, 500)], GREEN)
    d.arrow("history-to-window", [(552, 567), (668, 567)], ORANGE)
    d.text("core-edge", "默认在场", 555, 243, 100, 15, BLUE)
    d.text("external-edge", "工具读取", 560, 461, 95, 15, GREEN)
    d.text("history-edge", "检索 / 摘要", 554, 535, 110, 15, ORANGE)

    d.box("lifecycle", 36, 678, 1155, 150, "#cdd6e0", "#fbfcfe")
    d.text("life-head", "03  修改记忆后，何时生效？", 62, 695, 560, 23, INK)
    d.text("life-a", "编辑 MemFS 文件", 72, 751, 258, 21, BLUE)
    d.text("life-b", "提交到 Git", 397, 751, 210, 21, BLUE)
    d.text("life-c", "同步 / 重新编译提示", 670, 751, 300, 21, PURPLE)
    d.arrow("life-arrow-1", [(295, 769), (374, 769)], BLUE)
    d.arrow("life-arrow-2", [(565, 769), (647, 769)], PURPLE)
    d.text("life-foot", "不会在编辑的同一推理回合立刻改写已经装载的提示。", 72, 793, 1050, 17, MUTED, 6)
    d.text("scope", "图示范围：Letta Code 1f55d3dc 的 local MemFS v1；API-backed v2 的目录布局另见正文。", 40, 852, 1150, 16, MUTED, 6)

    d.save(Path(__file__).with_name("scene.excalidraw"))


if __name__ == "__main__":
    main()
