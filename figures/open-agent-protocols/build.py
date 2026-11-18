"""Build the Open Agent Ecosystem Protocols three-layer diagram."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from diagram_style import Scene, INK, MUTED

BLUE, PURPLE, GREEN, AMBER = "#3478e5", "#7c52e0", "#289e62", "#d97706"


def main() -> None:
    d = Scene()
    d.text("title", "开放协作三层标准：仓库约定、纵向工具协议与横向代理委托", 28, 22, 1080, 31, INK, 6)
    d.text("subtitle", "静态项目规则管「进场须知」，MCP 管「自己调工具」，A2A 管「跨边界把活派给独立搭档」", 28, 64, 1080, 20, MUTED)

    # Layer 1 (Top): Static Repo Convention - AGENTS.md
    d.box("repo-layer", 28, 112, 716, 124, AMBER, "#fff8eb")
    d.text("repo-tag", "① 静态仓库约定层 · AGENTS.md / CLAUDE.md", 48, 128, 676, 21, AMBER)
    d.text("repo-h", "就近层级发现：根仓库守全局禁区，子目录给专属构建与单测命令", 48, 160, 676, 20, INK)
    d.text("repo-b", "边界：纯文本开发约定，进系统提示辅助理解；不替代宿主审批与沙箱", 48, 194, 676, 19, MUTED)

    # Center Host & Primary Agent (Left-Center)
    d.box("host-box", 28, 286, 424, 178, BLUE, "#eef5ff")
    d.text("host-tag", "本地宿主与主 Agent（Host + Harness）", 48, 304, 384, 21, BLUE)
    d.text("host-h", "负责上下文组装、审批门禁与状态对账", 48, 338, 384, 20, INK)
    d.text(
        "host-b",
        "• 按目录层级读取 AGENTS.md\n• 审核工具行为注解与用户授权\n• 区分同步短调用与长耗时外部委托",
        48,
        374,
        384,
        19,
        MUTED,
    )

    # Arrow from Repo Layer down to Host
    d.arrow("arr-repo", [(238, 236), (238, 286)], AMBER)
    d.text("lbl-repo", "启动/进目录按需读取", 252, 250, 220, 19, AMBER)

    # Right Side (Horizontal): A2A Peer Agent
    d.box("a2a-box", 596, 264, 520, 218, PURPLE, "#f5f0ff")
    d.text("a2a-tag", "③ 横向跨代理协作层 · A2A 协议", 618, 282, 476, 21, PURPLE)
    d.text("a2a-h", "远端独立黑盒 Agent（隐藏内部提示与私有工具）", 618, 316, 480, 20, INK)
    d.text(
        "a2a-b",
        "• 能力名片：/.well-known/agent-card.json\n• 异步任务：submitted → working → completed\n• 中途挂起：input-required / auth-required\n• 进度通道：SSE 流式推送或 Webhook 回调",
        618,
        352,
        480,
        19,
        MUTED,
    )

    # Horizontal arrows between Host and A2A
    d.arrow("arr-a2a-req", [(452, 344), (596, 344)], PURPLE)
    d.text("lbl-a2a-req", "派发异步 Task", 464, 316, 128, 19, PURPLE)
    d.arrow("arr-a2a-res", [(596, 404), (452, 404)], PURPLE)
    d.elements[-1]["strokeStyle"] = "dashed"
    d.text("lbl-a2a-res", "状态流与回执", 466, 414, 128, 19, PURPLE)

    # Bottom Layer (Vertical): MCP 2025-11-25 Tool & Resource Layer
    d.box("mcp-box", 28, 516, 1088, 132, GREEN, "#ebfaf2")
    d.text("mcp-tag", "② 纵向工具与资源连接层 · MCP（2025-11-25 规范）", 48, 532, 640, 21, GREEN)
    d.text("mcp-c1", "Streamable HTTP 统一传输\n兼容短响应与流式服务端推送", 48, 568, 316, 19, INK)
    d.text("mcp-c2", "OAuth 2.1 资源服务器鉴权\nPKCE 校验，禁止盲目透传令牌", 396, 568, 326, 19, INK)
    d.text("mcp-c3", "Annotations 与 Elicitation\n行为提示仅供参考；缺参发起追问", 752, 568, 344, 19, INK)

    # Vertical arrows between Host and MCP
    d.arrow("arr-mcp-down", [(176, 464), (176, 516)], GREEN)
    d.text("lbl-mcp-down", "tools/call", 64, 478, 106, 19, GREEN)
    d.arrow("arr-mcp-up", [(298, 516), (298, 464)], GREEN)
    d.elements[-1]["strokeStyle"] = "dashed"
    d.text("lbl-mcp-up", "结果或追问请求", 312, 478, 160, 19, GREEN)

    for element in d.elements:
        if element["type"] in {"rectangle", "arrow"}:
            element["roughness"] = 1
        if element["type"] == "arrow":
            element["strokeWidth"] = 3

    d.save(ROOT / "figures/open-agent-protocols/scene.excalidraw")


if __name__ == "__main__":
    main()
