"""Build the long-session state & compaction diagram."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from diagram_style import Scene, INK, MUTED

BLUE, PURPLE, GREEN, AMBER, SLATE = "#3578e5", "#7c52e0", "#289e62", "#d97706", "#475569"


def main() -> None:
    d = Scene()
    d.text("title", "长会话不迷路：四种状态各管一事，按需装入下一轮窗口", 28, 24, 1060, 33, INK, 6)
    d.text("subtitle", "聊天越长注意力越稀释；把「原始记录、压缩摘要、长期记忆、执行快照」分开存放，再组装高信噪比输入", 28, 68, 1060, 20, MUTED)

    # Left: Growing session stream (x=28..280, w=252)
    d.box("raw-turn", 28, 184, 252, 304, SLATE, "#f1f5f9")
    d.text("raw-step", "01 持续增长的过程", 48, 204, 212, 20, SLATE)
    d.text("raw-title", "多轮对话与工具日志", 48, 238, 212, 23, INK)
    d.text(
        "raw-body",
        "• 第 1–30 轮历史消息\n• 大段文件与搜索输出\n• 途中定下的关键约束\n• 做到一半的多步流程",
        48,
        282,
        212,
        19,
        MUTED,
    )
    d.text("raw-warn", "全塞入窗口 → 注意力稀释", 48, 426, 216, 19, "#b45309")

    # Middle: Four distinct state lanes (x=348..704, w=356)
    lanes = [
        ("lane-tree", 118, BLUE, "#eaf3ff", "① 会话分支记录 Transcript", "保留完整消息与分支（Pi JSONL）", "取近期片段", 162),
        ("lane-compact", 244, PURPLE, "#f3eeff", "② 压缩摘要 Compaction", "把早期长对话浓缩成精简摘要", "代旧长日志", 264),
        ("lane-mem", 370, GREEN, "#e7f7ee", "③ 长期记忆 Memory", "跨任务规则与事实（Letta / Mem0）", "常驻或检索", 346),
        ("lane-ckpt", 496, AMBER, "#fff6e5", "④ 进度检查点 Checkpoint", "图执行阶段快照（LangGraph）", "断点续跑", 464),
    ]
    for key, y, stroke, fill, heading, desc, edge_lbl, lbl_y in lanes:
        d.box(key, 348, y, 356, 104, stroke, fill)
        d.text(f"{key}-h", heading, 368, y + 16, 320, 21, INK)
        d.text(f"{key}-d", desc, 368, y + 54, 320, 19, MUTED)
        d.text(f"{key}-el", edge_lbl, 718, lbl_y, 112, 19, stroke)

    # Right: Next-turn working context (x=844..1100, w=256)
    d.box("workbench", 844, 162, 256, 364, BLUE, "#eff6ff")
    d.text("wb-step", "02 本轮工作台", 866, 184, 212, 20, BLUE)
    d.text("wb-title", "本轮模型输入", 866, 218, 212, 24, INK)
    d.text(
        "wb-body",
        "• 系统指令与核心记忆\n• 早期讨论压缩摘要\n• 当前分支近期消息\n• 按需召回的参考事实",
        866,
        264,
        216,
        19,
        MUTED,
    )
    d.text("wb-foot", "检查点留在宿主调度层：\n先核对外部动作再续跑", 866, 434, 216, 19, AMBER)

    # Arrows from raw to 4 lanes
    for key, y_end, color in [
        ("in-1", 170, BLUE),
        ("in-2", 296, PURPLE),
        ("in-3", 422, GREEN),
        ("in-4", 548, AMBER),
    ]:
        d.arrow(key, [(280, 336), (348, y_end)], color)

    # Arrows from lanes to workbench
    for key, y_start, y_end, color, dashed in [
        ("out-1", 170, 236, BLUE, False),
        ("out-2", 296, 300, PURPLE, False),
        ("out-3", 422, 364, GREEN, True),
        ("out-4", 548, 466, AMBER, True),
    ]:
        d.arrow(key, [(704, y_start), (844, y_end)], color)
        if dashed:
            d.elements[-1]["strokeStyle"] = "dashed"

    for element in d.elements:
        if element["type"] in {"rectangle", "arrow"}:
            element["roughness"] = 1
        if element["type"] == "arrow":
            element["strokeWidth"] = 3

    d.save(ROOT / "figures/compaction-and-memory/scene.excalidraw")


if __name__ == "__main__":
    main()
