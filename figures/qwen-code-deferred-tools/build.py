"""Generate a two-pass 'discover then dispatch' Excalidraw route map."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from diagram_style import INK, MUTED, Scene  # noqa: E402


def station(scene: Scene, name: str, number: str, x: int, y: int, stroke: str, fill: str) -> None:
    element = scene._base(name, "ellipse", x, y, 66, 66)
    element.update(strokeColor=stroke, backgroundColor=fill, strokeWidth=2)
    scene.elements.append(element)
    scene.text(name + "-number", number, x + 20, y + 14, 30, 29, stroke, 6)


def build() -> None:
    d = Scene()
    blue = "#286da5"
    orange = "#af6d20"
    green = "#267b5b"
    gray = "#657382"

    d.box("visibility-strip", 40, 139, 1080, 104, "#cbd5de", "#f8fafc")
    d.arrow("discover-a", [(206, 332), (450, 332)], blue)
    d.arrow("discover-b", [(516, 332), (800, 332)], blue)
    d.arrow("dispatch-a", [(206, 557), (450, 557)], orange)
    d.arrow("dispatch-b", [(516, 557), (800, 557)], orange)

    for name, number, x, y, stroke, fill in [
        ("search", "1", 140, 299, blue, "#e9f3fb"),
        ("registry", "2", 450, 299, blue, "#e9f3fb"),
        ("schema", "3", 800, 299, blue, "#e9f3fb"),
        ("call", "4", 140, 524, orange, "#fff1df"),
        ("resolve", "5", 450, 524, orange, "#fff1df"),
        ("target", "6", 800, 524, green, "#eaf6ed"),
    ]:
        station(d, name, number, x, y, stroke, fill)

    d.text("title", "Qwen Code · 延迟工具的两段桥", 40, 25, 1090, 35, INK, 6)
    d.text("subtitle", "发现 schema 与执行目标是两次不同工具调用；注册、可见、可调用也不是同一件事。", 42, 77, 1050, 18, MUTED, 6)
    d.text("registered", "ToolRegistry：目标已注册、可被发现", 65, 158, 454, 20, gray, 6)
    d.text("not-equal", "≠", 530, 166, 50, 30, orange, 6)
    d.text("declared", "模型声明：eager 工具 + tool_search / tool_call", 606, 158, 475, 20, gray, 6)
    d.text("visibility", "前提：目标仍是 hidden deferred；可见 / 预加载 / CodeModeOnly 另有路径", 65, 205, 1000, 15, MUTED, 6)

    d.text("discover-rail", "发现轨道 · 只读", 60, 259, 300, 20, blue, 6)
    d.text("search-label", "tool_search(query)", 93, 382, 255, 18, INK, 8)
    d.text("registry-label", "Registry 隐藏候选", 409, 382, 274, 18, INK, 8)
    d.text("schema-label", "<functions> schema", 758, 382, 310, 18, INK, 8)

    d.text("separator", "模型读到 schema，但声明列表不因此刷新；另发 tool_call 才进入执行轨道。", 60, 446, 1040, 17, gray, 6)
    d.text("dispatch-rail", "执行轨道 · 目标策略", 60, 481, 330, 20, orange, 6)
    d.text("call-label", "tool_call {name,args}", 83, 608, 300, 18, INK, 8)
    d.text("resolve-label", "resolveDeferredToolCall", 397, 608, 340, 18, INK, 8)
    d.text("target-label", "Scheduler → 真实工具", 762, 608, 320, 18, INK, 8)
    d.text("footer", "静态源码图 · QwenLM/qwen-code@b9840886 · 目标仍须过上下文策略、权限与审批，未做运行实测", 42, 687, 1080, 15, MUTED, 6)
    d.save(Path(__file__).resolve().parent / "scene.excalidraw")


if __name__ == "__main__":
    build()
