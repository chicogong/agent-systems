"""Generate a conceptual fan-in figure: stored state versus current context."""

from pathlib import Path

from diagram_style import INK, MUTED, Scene


ROOT = Path(__file__).resolve().parents[1]
GRAY = "#778392"
AMBER = "#bd7720"
BLUE = "#2775c4"


def main() -> None:
    d = Scene()
    d.box("stores", 30, 153, 492, 438, "#bdc5ce", "#f7f9fb")
    d.box("session", 60, 208, 430, 73, GRAY, "#ffffff")
    d.box("summary", 60, 304, 430, 73, GRAY, "#ffffff")
    d.box("memory", 60, 400, 430, 73, GRAY, "#ffffff")
    d.box("knowledge", 60, 496, 430, 73, GRAY, "#ffffff")
    d.box("assembler", 626, 246, 238, 288, AMBER, "#fff4dd")
    d.box("context", 929, 306, 259, 169, BLUE, "#e6f3ff")

    for name, y, label in [
        ("session", 244, "挑选"),
        ("summary", 340, "引用"),
        ("memory", 436, "检索"),
        ("knowledge", 532, "检索"),
    ]:
        d.arrow(f"{name}-to-assembly", [(490, y), (626, y)], GRAY)
        d.elements[-1]["strokeStyle"] = "dashed"
        d.text(f"{name}-edge", label, 523, y - 24, 92, 15, GRAY, 6)
    d.arrow("assembly-to-context", [(864, 389), (929, 389)], BLUE)

    d.text("title", "存着 ≠ 这轮模型看见", 33, 25, 1160, 37, INK, 6)
    d.text("subtitle", "上下文是一次请求的输入；会话、摘要、长期记忆和知识库是可能的来源。", 34, 82, 1140, 19, MUTED, 6)
    d.text("stores-title", "可用来源（不自动全量进入）", 52, 169, 440, 20, GRAY, 6)
    d.text("session-label", "会话记录  transcript", 79, 231, 395, 20, INK, 8)
    d.text("summary-label", "压缩摘要  summary", 79, 327, 395, 20, INK, 8)
    d.text("memory-label", "长期记忆  memory", 79, 423, 395, 20, INK, 8)
    d.text("knowledge-label", "外部知识  retrieval", 79, 519, 395, 20, INK, 8)
    d.text("assembler-title", "上下文装配", 648, 277, 195, 25, AMBER, 6)
    d.text("assembler-body", "取当前任务所需片段\n加入指令与新输入\n受窗口预算约束", 648, 330, 195, 19, INK, 6)
    d.text("context-title", "本轮模型输入", 950, 331, 220, 25, BLUE, 6)
    d.text("context-body", "仅装配后的内容\n模型此刻可见", 950, 390, 220, 19, INK, 6)
    d.text("footer", "教学抽象：具体系统可能没有其中某一层；箭头表示选择/检索，不代表自动读取或成功记住。", 38, 620, 1145, 17, MUTED, 6)
    d.save(ROOT / "figures/context-vs-memory/scene.excalidraw")


if __name__ == "__main__":
    main()
