"""Regenerate the two Pi diagrams as readable portrait Excalidraw scenes."""

from pathlib import Path

from diagram_style import BLUE, GREEN, INK, MUTED, ORANGE, PURPLE, Scene

ROOT = Path(__file__).resolve().parents[1]


def finish(d: Scene, path: str) -> None:
    for e in d.elements:
        if e["type"] in {"rectangle", "arrow"}:
            e["roughness"] = 1
        if e["type"] == "arrow":
            e["strokeWidth"] = 3
    d.save(ROOT / path)


def card(d: Scene, key: str, y: int, color: str, fill: str, label: str) -> None:
    d.box(key, 90, y, 530, 50, color, fill)
    d.text(key + "-label", label, 108, y + 9, 495, 22)


def step(d: Scene, key: str, y: int, color: str, label: str, gap: int = 20) -> None:
    d.arrow(key, [(355, y), (355, y + gap)], color)
    d.text(key + "-caption", label, 385, y - 8, 180, 20, color)


def architecture() -> None:
    d = Scene()
    d.text("title", "Pi：接收任务、调用工具、记录会话", 30, 20, 670, 32, INK, 6)
    d.text("subtitle", "应用接任务，核心跑循环，应用记录过程。", 31, 65, 660, 20, MUTED, 6)
    for key, y, color, fill, heading in [
        ("application", 125, BLUE, "#f5f9ff", "A. 应用接收任务与加载资源"),
        ("runtime", 435, PURPLE, "#faf7ff", "B. 循环核心 · pi-agent-core"),
        ("state", 745, GREEN, "#f5fcf8", "C. 应用保存会话 · pi-coding-agent"),
    ]:
        d.box(key + "-panel", 25, y, 670, 295, color, fill)
        d.text(key + "-heading", heading, 45, y + 15, 620, 24, color)
    for key, y, label in [
        ("input", 180, "接收任务 · CLI/TUI · RPC/SDK"),
        ("session", 260, "管理会话 · AgentSession"),
        ("resources", 340, "加载扩展与技能 · Extensions / Skills"),
    ]:
        card(d, key, y, BLUE, "#dcecff", label)
    step(d, "input-to-session", 240, BLUE, "进入")
    step(d, "session-to-resources", 320, BLUE, "加载")
    for key, y, label in [
        ("agent", 490, "保管消息与新输入 · Agent.prompt()"),
        ("loop", 570, "模型与工具循环 · runLoop"),
        ("ai", 650, "联系模型服务 · pi-ai / streamFn"),
    ]:
        card(d, key, y, PURPLE, "#e7ddff", label)
    step(d, "agent-to-loop", 550, PURPLE, "运行")
    step(d, "loop-to-ai", 630, PURPLE, "模型请求")
    for key, y, label in [
        ("message", 800, "循环发来消息结束事件 · message_end"),
        ("subscriber", 880, "接收并处理消息 · AgentSession"),
        ("tree", 960, "追加会话树记录 · SessionManager"),
    ]:
        card(d, key, y, GREEN, "#ddf5e8", label)
    step(d, "message-to-session", 860, GREEN, "订阅")
    step(d, "session-to-tree", 940, GREEN, "追加")
    d.arrow("session-to-agent", [(620, 290), (655, 290), (655, 520), (620, 520)], PURPLE)
    d.text("core-edge", "调用", 560, 452, 65, 20, PURPLE)
    finish(d, "figures/pi-architecture/scene.excalidraw")


def extensions_and_skills() -> None:
    d = Scene()
    d.text("title", "Pi：工作指导与代码扩展", 30, 20, 670, 32, INK, 6)
    d.text("subtitle", "Skill 提供指导；Extension 加载会运行代码，先检查来源。", 31, 65, 660, 20, MUTED, 6)
    for key, y, color, fill, heading in [
        ("skills", 125, BLUE, "#f5f9ff", "A. 读取工作指导 · Skill"),
        ("extensions", 530, PURPLE, "#faf7ff", "B. 加载代码并注册 · ExtensionAPI"),
    ]:
        d.box(key + "-panel", 25, y, 670, 390, color, fill)
        d.text(key + "-heading", heading, 45, y + 15, 620, 24, color)
    for key, y, label in [
        ("skill-0", 180, "包或本地目录 · SKILL.md"),
        ("skill-1", 268, "读取名称、描述、路径 · loadSkills"),
        ("skill-3", 454, "模型 read／用户 /skill:name → 读正文"),
    ]:
        card(d, key, y, BLUE, "#dcecff", label)
    d.box("skill-2", 90, 356, 530, 60, BLUE, "#dcecff")
    d.text("skill-2-label", "模型可选 → 列进系统提示目录\n禁模型调用 → 隐藏目录；用户 /skill:name", 108, 361, 495, 20)
    for i, (y, label) in enumerate([(240, "发现"), (328, "筛选"), (427, "按需")]):
        step(d, f"skill-arrow-{i}", y, BLUE, label, 27)
    for key, y, label in [
        ("ext-0", 585, "加载代码模块 · TS / JS"),
        ("ext-1", 673, "导入模块并初始化 · jiti"),
        ("ext-2", 761, "注册工具／接入事件 · registerTool / on"),
        ("ext-3", 849, "接入工具、事件和命令"),
    ]:
        card(d, key, y, PURPLE, "#e7ddff", label)
    for i, (y, label) in enumerate([(645, "导入"), (733, "注册"), (821, "接入")]):
        step(d, f"ext-arrow-{i}", y, PURPLE, label, 28)
    d.box("bridge-panel", 25, 935, 670, 85, ORANGE, "#fffaf0")
    d.text("bridge-section", "Extension 可用 resources_discover 提供 Skill 路径；\n新增工具通过 Extension 注册，Skill 提供指导。", 45, 949, 630, 20, ORANGE)
    finish(d, "figures/pi-extensions/scene.excalidraw")


if __name__ == "__main__":
    architecture()
    extensions_and_skills()
