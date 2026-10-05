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
         title_size: int = 23, detail_size: int = 19) -> None:
    scene.box(name, x, y, w, 118, stroke, fill)
    scene.elements[-1].update(roughness=1, strokeWidth=2)
    scene.text(f"{name}-title", title, x + 16, y + 18, w - 32,
               title_size, INK, 8)
    scene.text(f"{name}-detail", detail, x + 16, y + 56, w - 32,
               detail_size, MUTED, 8)


def arrow(scene: Scene, name: str, x0: int, x1: int, y: int, color: str) -> None:
    scene.arrow(name, [(x0, y), (x1, y)], color)
    scene.elements[-1].update(roughness=1, strokeWidth=3)


def build() -> None:
    d = Scene()
    d.text("title", "Qwen Code：先找工具说明，再请求调用", 34, 25, 850, 30, INK, 8)
    d.text("scope", "普通声明模式；两个入口可用；目标仍隐藏（deferred）", 37, 80, 820, 21, MUTED, 8)

    # Registration and model declaration are distinct states, not call steps.
    d.box("registry-band", 36, 136, 372, 106, "#b9cef0", "#f7faff")
    d.elements[-1].update(roughness=1, strokeWidth=2)
    d.box("declarations-band", 492, 136, 372, 106, "#d2c4fa", "#faf7ff")
    d.elements[-1].update(roughness=1, strokeWidth=2)
    d.text("registered-label", "程序中的工具表", 54, 151, 336, 23, "#2563a6", 8)
    d.text("registered-detail", "ToolRegistry\n含暂时隐藏的工具", 54, 187, 336, 18, INK, 8)
    d.text("not-equal", "两份\n清单", 423, 162, 65, 19, "#9a6700", 8)
    d.text("declarations-label", "交给模型的精简清单", 510, 151, 336, 23, "#6d44c1", 8)
    d.text("declarations-detail", "直接声明（eager）+ 两个入口\ntool_search / tool_call", 510, 187, 336, 18, INK, 8)

    d.text("discover-rail", "找说明 · 返回工具名、用途和参数结构", 37, 270, 810, 24, "#2563a6", 8)
    arrow(d, "discover-a", 264, 324, 368, BLUE)
    arrow(d, "discover-b", 609, 669, 368, VIOLET)
    card(d, "search", 34, 309, 230, BLUE, "#d7ebff",
         "搜索工具说明", "tool_search\n按名称或关键词找")
    card(d, "registry", 324, 309, 285, BLUE, "#d7ebff",
         "筛选可用目标", "ToolRegistry\n读出参数结构")
    card(d, "schema", 669, 309, 230, VIOLET, "#e5dbff",
         "模型拿到说明", "<functions>\nschema：用途与参数")
    d.text("bridge-note", "说明以文本交回，调用另发 tool_call；已知目标也可直接请求", 37, 454, 825, 20, MUTED, 8)

    d.text("dispatch-rail", "发请求 · 检查目标条件与执行权限", 37, 511, 810, 24, "#9a6700", 8)
    arrow(d, "dispatch-a", 264, 324, 609, AMBER)
    arrow(d, "dispatch-b", 609, 669, 609, GREEN)
    card(d, "call", 34, 550, 230, AMBER, "#fff3bf",
         "指定目标与参数", "tool_call\n{name, arguments}")
    card(d, "resolve", 324, 550, 285, AMBER, "#fff3bf",
         "找到并核对目标", "resolveDeferredToolCall\n确认目标可用", detail_size=18)
    card(d, "target", 669, 550, 230, GREEN, "#c3fae8",
         "换成真实工具请求", "CoreToolScheduler\n检查权限后执行")

    d.save(Path(__file__).with_name("scene.excalidraw"))


if __name__ == "__main__":
    build()
