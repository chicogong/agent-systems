# 图稿约定

每张正式图放在独立目录：`scene.excalidraw` 是可编辑源文件，`diagram.svg` 用于 Markdown，`preview.png` 用于预览，`README.md` 给出文字说明、主张、来源和核验状态。

使用 [excalidraw-agent](https://github.com/chicogong/excalidraw-agent) 绘制和导出。发布前目视检查文字、箭头、边界、留白与移动端可读性。MCP 画布的成功返回只证明已接收，不证明与本地导出视觉一致；需要交互展示时还要检查实际画布。

字体、图形语义和导出验收见[设计原则](STYLE.md)。Pi 图采用 Normal 标题和 Code 节点；其他章节应按问题选择最清楚的形式。MCP 交互画布可能强制替换字体，因此仓库 SVG/PNG 才是对外展示的视觉基准。

概念图可以表达通用模型，但须说明它不是某个项目的内部结构。实现图只标固定源码版本中能核对的组件和路径。

当前图集：[Agent loop 概念图](agent-loop/README.md) · [上下文与记忆概念图](context-vs-memory/README.md) · [工作流、Agent 与多执行者](agent-workflow-multiagent/README.md) · [Pi 分层图](pi-architecture/README.md) · [Pi 扩展资源图](pi-extensions/README.md) · [Codex 执行决策树](codex-exec-approval/README.md) · [OpenCode 工具状态机](opencode-tool-state/README.md) · [mini-SWE-agent 消息循环](mini-swe-loop/README.md) · [Qwen Code 延迟工具双轨](qwen-code-deferred-tools/README.md) · [Letta Code 记忆映射](letta-memory/README.md) · [Mem0 检索漏斗](mem0-retrieval/README.md) · [LangGraph checkpoint 分支](langgraph-checkpoints/README.md) · [OpenHands 事件时序图](openhands-action-events/README.md) · [Browser Use 泳道时序图](browser-use-step/README.md) · [OpenClaw 会话关口](openclaw-session-gates/README.md) · [GPT Researcher 证据汇合](gpt-researcher-evidence/README.md)。

## 视觉校稿进度

本轮又重绘了 GPT Researcher、mini-SWE-agent、Qwen Code、上下文与记忆的旧图，并收紧 OpenHands 时序图的纵向间距与标签避让；Pi 两图的细箭头标签也已放大。各图保留并发汇合、消息账本、双轨、源到上下文、泳道、分层等适合其机制的图形语法，统一的是字体层级、线条、箭头和颜色。独立 QA 在图稿停止写入后核对了 16/16 图源与 PNG/SVG 的导出一致性、13/13 生成脚本的确定性，未发现图中文字裁切或箭头遮挡。此结论仍只是**本地视觉与导出校稿**，不是 MCP 画布像素一致性、移动端或外部读者验收。

印刷清晰度不能只看独立 PNG 的像素数：原图缩进 A4 正文宽度后，小字号注释仍可能难读。每次改图还要检查成书 PDF 的实际含图页；关键节点文字尽量不低于约 7 pt 的印刷尺寸，过长的技术说明移到图下正文。密集图不能靠持续加大 PNG 像素“修复”。

Pi 两张图的最小字已从约 5.6–6.0 pt 提到按 A4 正文宽度估算约 7.1 pt；正式印刷仍需复看实页。OpenCode、LangGraph、Codex、Mem0 与 Agent loop 的少数细注释约 6.1–6.4 pt，留作后续印刷/移动端校稿。每张图独立决定是否需要标题、分区或注释，不做全库机械换色。
