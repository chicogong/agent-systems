"""Generate the native mini-swe-agent message-ledger control-flow scene."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from diagram_style import INK, MUTED, Scene  # noqa: E402


def rule(scene: Scene, name: str, x0: int, x1: int, y: int) -> None:
    scene.arrow(name, [(x0, y), (x1, y)], "#d6d9de")
    scene.elements[-1].update(strokeWidth=1, endArrowhead=None)


def build() -> None:
    d = Scene()
    slate = "#426080"
    violet = "#6c54aa"
    teal = "#24877a"
    amber = "#ac6f1e"
    green = "#2a8054"

    # An append-only-looking ledger is the visual anchor. Its actual persistence
    # is conditional on output_path, as described in the article.
    d.box("ledger", 43, 151, 356, 621, "#9eafc2", "#f8fafc")
    for idx, y in enumerate((243, 323, 403, 483, 563, 643)):
        rule(d, f"ledger-rule-{idx}", 59, 383, y)
    d.box("query", 522, 259, 259, 92, violet, "#f1ebff")
    d.box("execute", 522, 419, 259, 92, teal, "#e8f8f4")
    d.box("stop-check", 522, 586, 259, 104, slate, "#eaf2fb")
    d.box("return", 886, 594, 291, 92, green, "#ebf7ef")
    d.box("exit-sources", 868, 188, 309, 331, "#e7bd7c", "#fffaf0")

    d.arrow("query-to-execute", [(651, 351), (651, 419)], violet)
    d.arrow("execute-to-check", [(651, 511), (651, 586)], teal)
    d.arrow("continue-loop", [(522, 637), (452, 637), (452, 306), (522, 306)], slate)
    d.arrow("stop-to-return", [(781, 637), (886, 637)], green)
    d.arrow("query-appends", [(522, 305), (430, 305), (430, 435), (399, 435)], violet)
    d.arrow("execute-appends", [(522, 460), (430, 460), (430, 515), (399, 515)], teal)

    d.text("title", "mini-swe-agent · 消息账本怎样驱动循环与停止", 40, 23, 1135, 35, INK, 6)
    d.text("subtitle", "DefaultAgent 的控制信号落在 messages 的最后一条：role=exit 才跳出 while True。", 43, 75, 1110, 18, MUTED, 6)
    d.text("ledger-title", "messages[] · 本轮上下文", 63, 174, 310, 22, slate, 6)
    d.text("system-entry", "01   system 模板", 63, 258, 290, 19, INK, 8)
    d.text("user-entry", "02   user(task)", 63, 338, 290, 19, INK, 8)
    d.text("assistant-entry", "03   assistant(action)", 63, 418, 310, 19, violet, 8)
    d.text("observation-entry", "04   observation", 63, 498, 290, 19, teal, 8)
    d.text("repeat-entry", "…    下一轮继续追加", 63, 578, 290, 19, MUTED, 6)
    d.text("exit-entry", "末条 exit → 停止", 63, 658, 290, 20, green, 8)
    d.text("query-label", "query()\n限额检查 → model.query", 542, 276, 223, 19, INK, 8)
    d.text("execute-label", "execute_actions()\nenv.execute → 观察", 542, 435, 223, 19, INK, 8)
    d.text("check-label", "每轮 save() 后\n末条 role == exit ?", 542, 604, 223, 19, INK, 8)
    d.text("return-label", "返回 exit.extra\n不是模型布尔值", 906, 611, 250, 19, INK, 8)
    d.text("continue-label", "否：继续", 454, 554, 100, 15, slate, 6)
    d.text("yes-label", "是", 810, 606, 60, 16, green, 6)
    d.text("exit-title", "exit 消息的来源", 888, 209, 268, 21, amber, 6)
    d.text("exit-1", "Submitted\n本地命令完成哨兵", 888, 263, 265, 18, INK, 8)
    d.text("exit-2", "Limits / Time\n请求模型前检查", 888, 349, 265, 18, INK, 8)
    d.text("exit-3", "RepeatedFormatError\n连续解析失败达阈值", 888, 435, 265, 18, INK, 8)
    d.text("footer", "基类静态源码图 · SWE-agent/mini-swe-agent@04d809ce · mini CLI 默认交互子类，可能在执行前确认", 43, 797, 1125, 15, MUTED, 6)
    d.save(Path(__file__).resolve().parent / "scene.excalidraw")


if __name__ == "__main__":
    build()
