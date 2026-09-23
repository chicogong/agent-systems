"""Regenerate Pi's editable figures from the fixed-source chapter design."""

from pathlib import Path

from diagram_style import BLUE, GREEN, INK, MUTED, ORANGE, PURPLE, Scene


ROOT = Path(__file__).resolve().parents[1]


def architecture() -> None:
    d = Scene()
    d.box("application-panel", 30, 140, 1180, 182, "#b8d4ff", "#f5f9ff")
    d.box("runtime-panel", 30, 347, 1180, 202, "#d7c8ff", "#faf7ff")
    d.box("state-panel", 30, 574, 1180, 179, "#bce8d1", "#f5fcf8")

    d.arrow("input-to-session", [(340, 238), (455, 238)], BLUE)
    d.arrow("session-to-resources", [(742, 238), (850, 238)], BLUE)
    d.arrow("session-to-agent", [(598, 284), (598, 399), (203, 399), (203, 428)], PURPLE)
    d.arrow("agent-to-loop", [(340, 469), (455, 469)], PURPLE)
    d.arrow("loop-to-ai", [(742, 469), (850, 469)], PURPLE)
    d.arrow("message-to-session", [(340, 664), (455, 664)], GREEN)
    d.arrow("session-to-tree", [(742, 664), (850, 664)], GREEN)

    for name, x, y, color, fill in [
        ("input", 70, 197, BLUE, "#dcecff"),
        ("session", 455, 197, BLUE, "#dcecff"),
        ("resources", 850, 197, BLUE, "#dcecff"),
        ("agent", 70, 428, PURPLE, "#e7ddff"),
        ("loop", 455, 428, PURPLE, "#e7ddff"),
        ("ai", 850, 428, PURPLE, "#e7ddff"),
        ("message", 70, 623, GREEN, "#ddf5e8"),
        ("subscriber", 455, 623, GREEN, "#ddf5e8"),
        ("tree", 850, 623, GREEN, "#ddf5e8"),
    ]:
        d.box(name, x, y, 270 if x == 70 else 287 if x == 455 else 286, 84, color, fill)

    d.text("title", "Pi：运行核心与 coding-agent 外壳", 35, 25, 1140, 37, INK, 6)
    d.text("subtitle", "运行循环、扩展资源和磁盘会话分属不同层，不画成一个 Agent 黑箱。", 36, 78, 1120, 19, MUTED, 6)
    d.text("a", "A. 应用入口与资源", 55, 153, 350, 22, BLUE)
    d.text("b", "B. 模型与工具循环", 55, 360, 350, 22, PURPLE)
    d.text("c", "C. coding-agent 的持久化旁路", 55, 586, 590, 22, GREEN)
    d.text("input-edge", "进入", 362, 210, 70, 15, BLUE)
    d.text("resource-edge", "加载", 755, 210, 70, 15, BLUE)
    d.text("core-edge", "调用", 609, 319, 70, 15, PURPLE)
    d.text("loop-edge", "运行", 362, 441, 70, 15, PURPLE)
    d.text("provider-edge", "模型请求", 754, 441, 95, 15, PURPLE)
    d.text("event-edge", "订阅", 362, 635, 70, 15, GREEN)
    d.text("storage-edge", "写入", 755, 635, 70, 15, GREEN)

    d.text("input-label", "输入方式\nCLI / TUI · RPC / SDK", 88, 210, 234, 18)
    d.text("session-label", "pi-coding-agent\nAgentSession", 473, 210, 250, 20)
    d.text("resources-label", "资源编排\nExtensions · Skills", 868, 210, 250, 20)
    d.text("agent-label", "Agent.prompt()\n内存消息与待处理队列", 88, 441, 234, 19)
    d.text("loop-label", "runLoop\n模型回合 · 工具结果", 473, 441, 250, 20)
    d.text("ai-label", "pi-ai\nprovider streamFn", 868, 441, 250, 20)
    d.text("message-label", "AgentEvent\nmessage_end", 88, 636, 234, 20)
    d.text("subscriber-label", "AgentSession\n订阅并处理消息", 473, 636, 250, 20)
    d.text("tree-label", "SessionManager\nJSONL 会话树", 868, 636, 250, 20)
    d.text("footer", "固定源码 898ab804；C 是 coding-agent 的实现，不是 pi-agent-core 的通用存储。", 40, 775, 1145, 16, MUTED, 6)
    d.save(ROOT / "figures/pi-architecture/scene.excalidraw")


def extensions_and_skills() -> None:
    d = Scene()
    d.box("skills-panel", 30, 145, 1180, 235, "#b8d4ff", "#f5f9ff")
    d.box("extensions-panel", 30, 406, 1180, 235, "#d7c8ff", "#faf7ff")
    d.box("bridge-panel", 30, 667, 1180, 120, "#ffe1a7", "#fffaf0")

    for row, y, color, fill in [
        ("skill", 222, BLUE, "#dcecff"),
        ("ext", 483, PURPLE, "#e7ddff"),
    ]:
        for index, x in enumerate((57, 354, 651, 948)):
            d.box(f"{row}-{index}", x, y, 239, 97, color, fill)
        for index, x in enumerate((296, 593, 890)):
            d.arrow(f"{row}-arrow-{index}", [(x, y + 49), (x + 56, y + 49)], color)

    d.text("title", "Pi：Skill 与 Extension 扩展的是不同层", 35, 25, 1150, 37, INK, 6)
    d.text("subtitle", "Skill 提供按需指令；Extension 在进程内接入代码能力。Pi Package 可同时分发两者。", 36, 80, 1140, 19, MUTED, 6)
    d.text("skill-section", "A. Skill：描述先入提示，正文按需读取", 55, 161, 810, 22, BLUE)
    d.text("ext-section", "B. Extension：加载模块并注册行为", 55, 422, 810, 22, PURPLE)
    d.text("bridge-section", "交叉点：Extension 可通过 resources_discover 提供 Skill 路径；Skill 自身没有 registerTool API。", 55, 696, 1110, 20, ORANGE)
    for row, y, color, captions in [
        ("skill", 235, BLUE, ("发现", "目录", "按需")),
        ("ext", 496, PURPLE, ("导入", "注册", "接入")),
    ]:
        for index, (x, caption) in enumerate(zip((297, 594, 891), captions)):
            d.text(f"{row}-edge-{index}", caption, x, y, 60, 14, color)

    d.text("skill-0-label", "Package / 本地目录\nSKILL.md", 72, 239, 205, 19)
    d.text("skill-1-label", "loadSkills\n读名称 · 描述 · 路径", 369, 239, 205, 19)
    d.text("skill-2-label", "system prompt\n只列出目录信息", 666, 239, 205, 19)
    d.text("skill-3-label", "模型 read 或 /skill\n按需加载正文", 963, 239, 205, 19)
    d.text("ext-0-label", "Package / 本地模块\nTS / JS", 72, 500, 205, 19)
    d.text("ext-1-label", "jiti 导入\ndefault factory", 369, 500, 205, 19)
    d.text("ext-2-label", "ExtensionAPI\nregisterTool · on", 666, 500, 205, 19)
    d.text("ext-3-label", "运行时接入\n工具 · 事件 · 命令", 963, 500, 205, 19)
    d.text("footer", "固定源码 898ab804；Skill 可附带脚本，但脚本由模型经已有工具调用，不是 Skill 自动执行。", 40, 809, 1140, 16, MUTED, 6)
    d.save(ROOT / "figures/pi-extensions/scene.excalidraw")


if __name__ == "__main__":
    architecture()
    extensions_and_skills()
