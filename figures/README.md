# 图稿约定

每张正式图放在独立目录：`scene.excalidraw` 是可编辑源文件，`diagram.svg` 用于 Markdown，`preview.png` 用于预览，`README.md` 给出文字说明、主张、来源和核验状态。

使用 [excalidraw-agent](https://github.com/chicogong/excalidraw-agent) 绘制和导出。发布前目视检查文字、箭头、边界、留白与移动端可读性。MCP 画布的成功返回只证明已接收，不证明与本地导出视觉一致；需要交互展示时还要检查实际画布。

字体、图形语义和导出验收见[设计原则](STYLE.md)。Pi 图采用 Normal 标题和 Code 节点；其他章节应按问题选择最清楚的形式。MCP 交互画布可能强制替换字体，因此仓库 SVG/PNG 才是对外展示的视觉基准。

概念图可以表达通用模型，但须说明它不是某个项目的内部结构。实现图只标固定源码版本中能核对的组件和路径。

当前图集：[Agent loop 概念图](agent-loop/README.md) · [上下文与记忆概念图](context-vs-memory/README.md) · [Pi 分层图](pi-architecture/README.md) · [Pi 扩展资源图](pi-extensions/README.md) · [Codex 执行决策树](codex-exec-approval/README.md) · [OpenCode 工具状态机](opencode-tool-state/README.md) · [mini-SWE-agent 消息循环](mini-swe-loop/README.md) · [Qwen Code 延迟工具双轨](qwen-code-deferred-tools/README.md) · [Letta Code 记忆映射](letta-memory/README.md) · [Mem0 检索漏斗](mem0-retrieval/README.md) · [LangGraph checkpoint 分支](langgraph-checkpoints/README.md) · [OpenHands 事件时序图](openhands-action-events/README.md) · [Browser Use 泳道时序图](browser-use-step/README.md) · [OpenClaw 会话关口](openclaw-session-gates/README.md) · [GPT Researcher 证据汇合](gpt-researcher-evidence/README.md)。
