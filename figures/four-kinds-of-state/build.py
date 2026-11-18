"""Build the Four Kinds of State ('Memory') 2x2 architectural matrix diagram."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from diagram_style import Scene, INK, MUTED

BLUE, PURPLE, GREEN, AMBER = "#3478e5", "#7c52e0", "#289e62", "#d97706"


def main() -> None:
    d = Scene()
    d.text("title", "把笼统的「记忆」拆回四种工程状态：结构、代价与选型", 28, 22, 1060, 31, INK, 6)
    d.text("subtitle", "四种状态解决四个正交问题；选错存储形态，轻则撑爆系统提示预算，重则在重启恢复时酿成双写事故", 28, 64, 1060, 20, MUTED)

    cards = [
        (
            "c1",
            28,
            114,
            BLUE,
            "#eef5ff",
            "① 对话分支记录 · Pi（JSONL 会话树）",
            "存什么：原始提问、回复、工具回执与父子分支指针",
            "• 写入极轻：顺序追加一行 JSON，零模型开销\n• 怎样进场：沿当前活跃叶子回溯投影线性消息链\n• 擅长与禁区：适合单场试错分叉；不跨月共享知识",
        ),
        (
            "c2",
            572,
            114,
            GREEN,
            "#ebfaf2",
            "② 常驻可编辑文件 · Letta（local MemFS）",
            "存什么：身份约定、项目硬规范（system/*.md）",
            "• 人类可读可手改：像维护 README 一样维护长期默契\n• 怎样进场：常驻区直接编入系统提示，零检索漏召回\n• 擅长与禁区：守几千字核心铁律；忌塞海量流水账",
        ),
        (
            "c3",
            28,
            344,
            PURPLE,
            "#f5f0ff",
            "③ 可检索原子事实库 · Mem0（向量索引）",
            "存什么：从对话提炼的跨月碎片事实与用户偏好卡片",
            "• 重写入换轻读取：写入需调模型抽取事实并消解冲突\n• 怎样进场：按当前问题相似度召回 Top-K 拼入提示\n• 擅长与禁区：扩海量长尾背景；忌赌它守 100% 红线",
        ),
        (
            "c4",
            572,
            344,
            AMBER,
            "#fff8eb",
            "④ 执行进度快照 · LangGraph（StateSnapshot）",
            "存什么：图通道变量值、待唤醒节点 next 与父快照链",
            "• 纯工程存档：每个超步落盘程序现场，非聊天摘要\n• 怎样进场：驱动引擎从审批挂起或崩溃断点精确续跑\n• 致命红线：只回滚图内内存，绝不撤回已发外部副作用",
        ),
    ]

    for key, x, y, color, fill, heading, sub, body in cards:
        d.box(key, x, y, 512, 206, color, fill)
        d.text(f"{key}-h", heading, x + 20, y + 16, 472, 21, color)
        d.text(f"{key}-s", sub, x + 20, y + 52, 472, 19, INK)
        d.text(f"{key}-b", body, x + 20, y + 90, 476, 19, MUTED)

    d.box("combo", 28, 572, 1056, 56, INK, "#f8fafc")
    d.text(
        "combo-t",
        "生产组合：④ 快照兜底长流程断点 + ② 常驻文件锁死红线 + ① 管当场分支 + ③ 按需补跨月背景",
        48,
        590,
        1016,
        19,
        INK,
    )

    for element in d.elements:
        if element["type"] == "rectangle":
            element["roughness"] = 1

    d.save(ROOT / "figures/four-kinds-of-state/scene.excalidraw")


if __name__ == "__main__":
    main()
