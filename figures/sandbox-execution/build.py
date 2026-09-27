"""Build one execution boundary, not a product ranking or security guarantee."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from diagram_style import Scene, INK, MUTED

BLUE, PURPLE, GREEN, AMBER = "#4a9eed", "#8b5cf6", "#16a34a", "#f59e0b"


def main() -> None:
    d = Scene()
    d.box("boundary", 325, 80, 485, 280, PURPLE, "#f7f3ff")
    d.elements[-1]["strokeStyle"] = "dashed"
    for name, x, y, w, h, stroke, fill in [
        ("contract", 25, 160, 235, 150, BLUE, "#a5d8ff"),
        ("tool", 355, 170, 425, 90, PURPLE, "#d0bfff"),
        ("ledger", 915, 160, 270, 155, GREEN, "#c3fae8"),
        ("validate", 915, 415, 270, 110, GREEN, "#c3fae8"),
        ("cleanup", 335, 415, 360, 100, BLUE, "#eaf3ff"),
        ("remote", 390, 575, 390, 115, AMBER, "#ffd8a8"),
    ]:
        d.box(name, x, y, w, h, stroke, fill)
    d.arrow("contract-to-tool", [(260, 215), (355, 215)], BLUE)
    d.arrow("tool-to-ledger", [(780, 215), (915, 215)], GREEN)
    d.arrow("ledger-to-check", [(1050, 315), (1050, 415)], GREEN)
    d.arrow("finish", [(515, 360), (515, 415)], BLUE)
    d.arrow("allowed-egress", [(810, 325), (855, 325), (855, 632), (780, 632)], AMBER)
    d.elements[-1]["strokeStyle"] = "dashed"

    d.text("question", "隔离执行，不等于撤销外部动作", 25, 20, 1150, 31, INK, 6)
    for name, value, x, y, w, size, color, font in [
        ("contract-title", "资源合同", 48, 179, 185, 25, BLUE, 6),
        ("contract-detail", "任务最小权限\n输入 · 输出 · 时限", 48, 224, 196, 21, INK, 8),
        ("boundary-title", "执行环境", 349, 99, 350, 25, PURPLE, 6),
        ("tool-title", "工具执行", 378, 184, 355, 24, INK, 8),
        ("tool-detail", "只取得合同允许的资源", 378, 224, 370, 21, INK, 8),
        ("resources", "文件 · 出网 · 进程 / 资源", 350, 284, 440, 22, PURPLE, 8),
        ("identity", "凭据、浏览器登录态另设最小权限", 350, 324, 450, 21, MUTED, 6),
        ("collect", "收集观察", 788, 174, 115, 21, GREEN, 8),
        ("ledger-title", "结果账本", 938, 179, 220, 25, GREEN, 6),
        ("ledger-detail", "退出状态 · 日志\n产物 · 错误", 938, 224, 225, 22, INK, 8),
        ("check-arrow", "环境外验收", 1070, 364, 125, 21, GREEN, 8),
        ("validate-title", "检查产物与证据", 938, 434, 230, 23, INK, 8),
        ("validate-detail", "通过 / 返工 / 停止", 938, 477, 230, 21, INK, 8),
        ("cleanup-title", "结束环境", 358, 432, 300, 24, BLUE, 6),
        ("cleanup-detail", "停止 / 保留 / 销毁按合同", 358, 475, 320, 21, INK, 8),
        ("egress-label", "被允许的出网", 878, 560, 210, 21, AMBER, 8),
        ("remote-title", "远端业务状态", 414, 593, 334, 25, AMBER, 6),
        ("remote-detail", "发布、发送、写入可能已经发生", 414, 637, 338, 21, INK, 8),
        ("no-undo", "清理本地环境 ≠ 回滚远端结果", 335, 725, 650, 24, AMBER, 6),
    ]:
        d.text(name, value, x, y, w, size, color, font)
    for element in d.elements:
        if element["type"] in {"rectangle", "arrow"}:
            element["roughness"] = 1
            element["strokeWidth"] = 3 if element["type"] == "arrow" else 2
    d.save(Path(__file__).with_name("scene.excalidraw"))


if __name__ == "__main__":
    main()
