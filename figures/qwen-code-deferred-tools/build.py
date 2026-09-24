"""Generate an editable two-rail map of Qwen Code's deferred-tool bridge."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from diagram_style import Scene  # noqa: E402


INK = "#14213d"
MUTED = "#475569"
BLUE = "#4a9eed"
VIOLET = "#8b5cf6"
AMBER = "#f59e0b"
GREEN = "#16a34a"


def card(scene: Scene, name: str, x: int, y: int, w: int,
         stroke: str, fill: str, title: str, detail: str,
         title_size: int = 23) -> None:
    scene.box(name, x, y, w, 118, stroke, fill)
    scene.elements[-1].update(roughness=1, strokeWidth=2)
    scene.text(f"{name}-title", title, x + 16, y + 18, w - 32,
               title_size, INK, 8)
    scene.text(f"{name}-detail", detail, x + 16, y + 64, w - 32,
               20, MUTED, 8)


def arrow(scene: Scene, name: str, x0: int, x1: int, y: int, color: str) -> None:
    scene.arrow(name, [(x0, y), (x1, y)], color)
    scene.elements[-1].update(roughness=1, strokeWidth=3)


def build() -> None:
    d = Scene()
    d.text("title", "Qwen Code：延迟工具的发现与执行", 34, 25, 850, 30, INK, 8)
    d.text("scope", "普通声明模式 · 仍隐藏的 deferred 目标", 37, 80, 820, 21, MUTED, 8)

    # Registration and model declaration are distinct states, not call steps.
    d.box("registry-band", 36, 136, 372, 92, "#b9cef0", "#f7faff")
    d.elements[-1].update(roughness=1, strokeWidth=2)
    d.box("declarations-band", 492, 136, 372, 92, "#d2c4fa", "#faf7ff")
    d.elements[-1].update(roughness=1, strokeWidth=2)
    d.text("registered-label", "ToolRegistry 已注册", 54, 151, 336, 23, "#2563a6", 8)
    d.text("registered-detail", "目标可被发现", 54, 188, 336, 20, INK, 8)
    d.text("not-equal", "≠", 436, 164, 42, 32, "#9a6700", 8)
    d.text("declarations-label", "模型当前声明", 510, 151, 336, 23, "#6d44c1", 8)
    d.text("declarations-detail", "eager + tool_search / tool_call", 510, 188, 336, 20, INK, 8)

    d.text("discover-rail", "发现 · schema 作为文本返回", 37, 270, 810, 24, "#2563a6", 8)
    arrow(d, "discover-a", 264, 324, 368, BLUE)
    arrow(d, "discover-b", 609, 669, 368, VIOLET)
    card(d, "search", 34, 309, 230, BLUE, "#d7ebff",
         "tool_search(query)", "检索隐藏目标", 21)
    card(d, "registry", 324, 309, 285, BLUE, "#d7ebff",
         "ToolRegistry", "筛选目标与 schema")
    card(d, "schema", 669, 309, 230, VIOLET, "#e5dbff",
         "<functions> schema", "模型读到参数形状", 20)
    d.text("bridge-note", "schema 文本 ≠ 模型声明；调用另发 tool_call", 37, 454, 825, 20, MUTED, 8)

    d.text("dispatch-rail", "执行 · 解析并检查目标策略", 37, 511, 810, 24, "#9a6700", 8)
    arrow(d, "dispatch-a", 264, 324, 609, AMBER)
    arrow(d, "dispatch-b", 609, 669, 609, GREEN)
    card(d, "call", 34, 550, 230, AMBER, "#fff3bf",
         "tool_call", "{name, arguments}")
    card(d, "resolve", 324, 550, 285, AMBER, "#fff3bf",
         "resolveDeferredToolCall", "检查目标与上下文", 21)
    card(d, "target", 669, 550, 230, GREEN, "#c3fae8",
         "CoreToolScheduler", "改写为真实工具调用", 20)

    d.save(Path(__file__).with_name("scene.excalidraw"))


if __name__ == "__main__":
    build()
