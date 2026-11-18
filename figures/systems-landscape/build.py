"""Build the 16-system architectural problem map for docs/systems/README.md."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from diagram_style import Scene, INK, MUTED

BLUE, PURPLE, GREEN, AMBER = "#3578e5", "#7c52e0", "#289e62", "#d97706"


def main() -> None:
    d = Scene()
    d.text("title", "16 个开源系统怎么选读：按你想解决的工程问题对号入座", 28, 24, 948, 32, INK, 6)
    d.text("subtitle", "不排热门榜单；每个项目只解剖它最具代表性的一条架构设计路径", 28, 68, 948, 19, MUTED)

    quadrants = [
        (
            "q1", 28, 114, 462, 266, BLUE, "#eaf3ff",
            "01 循环内核与忙时控制",
            "一轮怎么转？中途插话怎么接？状态怎么记？",
            "• Pi：三包解耦 + steer / followUp 双队列\n"
            "• mini-SWE-agent：百行代码跑通消息驱动循环\n"
            "• OpenCode：单次工具状态与会话状态分层\n"
            "• Kimi Code：忙时输入缓冲与 step 边界刷新\n"
            "• DSH：插件化服务装配与受控工具批次",
        ),
        (
            "q2", 514, 114, 462, 266, AMBER, "#fff6e5",
            "02 权限门禁、沙箱与交互界面",
            "谁批准动作？爆炸半径怎么锁？网页怎么看？",
            "• Codex：审批策略与沙箱执行双层解耦\n"
            "• OpenHands：SDK 事件流与隔离运行环境\n"
            "• Browser Use：DOM 索引、视觉截图与动作闭环\n"
            "• Qwen Code：延迟加载海量工具（先搜后调）",
        ),
        (
            "q3", 28, 404, 462, 252, GREEN, "#e7f7ee",
            "03 长期记忆、压缩与知识沉淀",
            "聊长了怎么省窗口？经验怎么跨会话留存？",
            "• Letta Code：本地核心记忆块与提示重编译\n"
            "• Hermes：短记忆快照、按需 Skill 与任务后复盘\n"
            "• Mem0：从对话提取事实并按范围向量检索\n"
            "• MiMo Code：成功水位线检查点与溢出重建",
        ),
        (
            "q4", 514, 404, 462, 252, PURPLE, "#f3eeff",
            "04 状态快照、常驻会话与多源编排",
            "中断怎么续跑？多人多源任务由谁兜底协调？",
            "• LangGraph：Pregel 图状态快照与分支回溯\n"
            "• OpenClaw：常驻网关中的显式会话键与串行门禁\n"
            "• GPT Researcher：本地文档与联网检索混合证据链",
        ),
    ]

    for key, x, y, w, h, stroke, fill, heading, question, items in quadrants:
        d.box(key, x, y, w, h, stroke, fill)
        d.text(f"{key}-h", heading, x + 20, y + 16, w - 40, 23, stroke)
        d.text(f"{key}-q", question, x + 20, y + 50, w - 40, 18, INK)
        d.text(f"{key}-items", items, x + 20, y + 88, w - 36, 18, MUTED)

    for element in d.elements:
        if element["type"] == "rectangle":
            element["roughness"] = 1

    d.save(ROOT / "figures/systems-landscape/scene.excalidraw")


if __name__ == "__main__":
    main()
