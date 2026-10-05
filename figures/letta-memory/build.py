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
    d.text("title", "Letta Code：常用信息随提示，长资料按需读", 38, 23, 1170, 34, INK, 8)
    d.text("subtitle", "local MemFS v1 · 三类材料，各有取用方式", 40, 77, 1150, 23, MUTED, 8)

    # Storage and visibility are separate columns. Arrow meanings live in
    # their nodes so the narrow gutter stays clear at book-page size.
    d.box("disk-panel", 36, 145, 559, 482, "#bfd5f5", "#f5f9ff")
    d.box("context-panel", 632, 145, 559, 482, "#d7c8ff", "#faf7ff")
    d.text("disk-head", "01  保存的材料", 62, 168, 500, 27, BLUE)
    d.text("context-head", "02  本轮交给模型的材料", 658, 168, 500, 27, PURPLE)

    d.box("core", 72, 237, 480, 112, BLUE, "#a5d8ff")
    d.text("core-title", "system/ 下的 Markdown", 94, 255, 425, 27, INK)
    d.text("core-body", "含子目录 · 默认加入系统提示", 94, 302, 430, 23, MUTED, 8)

    d.box("external", 72, 390, 480, 112, GREEN, "#c3fae8")
    d.text("external-title", "外部文件 / Skill 流程", 94, 408, 430, 27, INK)
    d.text("external-body", "按需通过工具读取", 94, 455, 430, 23, MUTED, 8)

    d.box("history", 72, 541, 480, 65, ORANGE, "#fff3bf")
    d.text("history-label", "会话历史 / recall 检索", 94, 557, 430, 25, INK)

    d.box("prompt", 668, 237, 480, 154, PURPLE, "#d0bfff")
    d.text("prompt-title", "系统提示 system prompt", 690, 255, 424, 27, INK)
    d.text("prompt-body", "基础指令 + 核心记忆块\n不默认放入外部文件正文", 690, 301, 425, 23, INK, 8)

    d.box("window", 668, 444, 480, 162, PURPLE, "#e5dbff")
    d.text("window-title", "本轮对话消息 conversation", 690, 461, 424, 27, INK)
    d.text("window-body", "近期消息 + 较早消息摘要\n旧信息用 recall 检索", 690, 508, 425, 23, INK, 8)

    d.arrow("core-to-prompt", [(552, 292), (668, 292)], BLUE)
    d.arrow("external-to-window", [(552, 446), (609, 446), (609, 484), (668, 484)], GREEN)
    d.arrow("history-to-window", [(552, 573), (668, 573)], ORANGE)

    d.box("lifecycle", 36, 673, 1155, 179, "#cbd5e1", "#f8fafc")
    d.text("life-head", "改了记忆后，两条路径各自更新", 62, 690, 1080, 27, INK, 8)
    d.text("tool-write", "用 memory() 写文件", 72, 736, 330, 23, BLUE, 8)
    d.arrow("tool-commit-arrow", [(363, 751), (418, 751)], BLUE)
    d.text("tool-commit", "提交修改 commitMemoryWrite", 436, 736, 660, 23, BLUE, 8)
    d.text("worker-merge", "memory worker 合并记忆", 72, 779, 330, 23, PURPLE, 8)
    d.arrow("worker-sync-arrow", [(363, 794), (418, 794)], PURPLE)
    d.text("worker-sync", "同步", 436, 779, 95, 23, PURPLE, 8)
    d.arrow("worker-recompile-arrow", [(508, 794), (563, 794)], PURPLE)
    d.text("worker-recompile", "支持时重建系统提示", 581, 779, 540, 23, PURPLE, 8)
    d.text("life-foot", "文件编辑后，已准备好的系统提示仍保留原内容", 72, 819, 1050, 23, MUTED, 8)

    for element in d.elements:
        if element["type"] == "rectangle":
            element["roughness"] = 1
        elif element["type"] == "arrow":
            element.update(roughness=1, strokeWidth=3)

    d.save(Path(__file__).with_name("scene.excalidraw"))


if __name__ == "__main__":
    main()
