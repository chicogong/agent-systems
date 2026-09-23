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


def card(scene: Scene, name: str, x: int, y: int, w: int, h: int,
         stroke: str, fill: str, title: str, detail: str) -> None:
    scene.box(name, x, y, w, h, stroke, fill)
    scene.elements[-1].update(roughness=1, strokeWidth=2)
    scene.text(f"{name}-title", title, x + 19, y + 17, w - 38, 21, INK, 8)
    scene.text(f"{name}-detail", detail, x + 19, y + 57, w - 38, 17, MUTED, 8)


def arrow(scene: Scene, name: str, x0: int, x1: int, y: int, color: str) -> None:
    scene.arrow(name, [(x0, y), (x1, y)], color)
    scene.elements[-1].update(roughness=1, strokeWidth=3)


def build() -> None:
    d = Scene()
    d.text("title", "Qwen Code：延迟工具为何分为发现与执行？", 49, 28, 1170, 35, INK, 8)
    d.text("subtitle", "普通声明模式：已注册、模型可见、可调用是三件事；仅画仍隐藏的 deferred 目标。", 52, 83, 1140, 18, MUTED, 8)

    # The premise is a visibility distinction, not an additional call path.
    d.box("registry-band", 52, 160, 510, 99, "#b9cef0", "#f7faff")
    d.elements[-1].update(roughness=1, strokeWidth=2)
    d.box("declarations-band", 650, 160, 510, 99, "#d2c4fa", "#faf7ff")
    d.elements[-1].update(roughness=1, strokeWidth=2)
    d.text("registered-label", "ToolRegistry", 75, 176, 460, 21, "#2563a6", 8)
    d.text("registered-detail", "目标已注册，可被发现", 75, 214, 460, 18, INK, 8)
    d.text("not-equal", "≠", 588, 190, 50, 30, "#9a6700", 8)
    d.text("declarations-label", "模型当前声明", 673, 176, 460, 21, "#6d44c1", 8)
    d.text("declarations-detail", "eager 工具 + tool_search / tool_call", 673, 214, 460, 18, INK, 8)

    d.text("discover-rail", "发现 · 把 schema 作为文本返回", 58, 303, 800, 22, "#2563a6", 8)
    arrow(d, "discover-a", 365, 447, 404, BLUE)
    arrow(d, "discover-b", 760, 842, 404, VIOLET)
    card(d, "search", 58, 344, 307, 121, BLUE, "#d7ebff",
         "tool_search(query)", "查仍隐藏的 deferred 目标")
    card(d, "registry", 447, 344, 313, 121, BLUE, "#d7ebff",
         "ToolRegistry", "筛选目标与 schema")
    card(d, "schema", 842, 344, 314, 121, VIOLET, "#e5dbff",
         "<functions> schema", "模型读到参数形状")
    d.text("bridge-note", "读到 schema ≠ 刷新模型声明；若要调用，模型另发 tool_call。", 60, 483, 1070, 18, MUTED, 8)

    d.text("dispatch-rail", "执行 · 对目标重新做策略检查", 58, 550, 800, 22, "#9a6700", 8)
    arrow(d, "dispatch-a", 365, 447, 651, AMBER)
    arrow(d, "dispatch-b", 760, 842, 651, GREEN)
    card(d, "call", 58, 591, 307, 121, AMBER, "#fff3bf",
         "tool_call", "{name, arguments}")
    card(d, "resolve", 447, 591, 313, 121, AMBER, "#fff3bf",
         "resolveDeferredToolCall", "检查 hidden / context")
    card(d, "target", 842, 591, 314, 121, GREEN, "#c3fae8",
         "CoreToolScheduler", "改写请求 → 真实工具")
    d.text("footer", "两条轨道是机制拆解，不表示独立线程或每次都先调用 tool_search。", 55, 750, 1130, 17, MUTED, 8)

    d.save(Path(__file__).with_name("scene.excalidraw"))


if __name__ == "__main__":
    build()
