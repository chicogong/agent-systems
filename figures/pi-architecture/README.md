# Pi 分层图的文字版

[返回 Pi 剖面](../../docs/systems/pi/README.md) · [图源](scene.excalidraw) · [SVG](diagram.svg) · [PNG](preview.png)

A 层是应用入口：CLI/TUI、RPC/SDK 等方式进入 coding-agent，由 `AgentSession` 组织资源。B 层是运行核心：`Agent.prompt()` 进入 `runLoop`，后者处理模型和工具回合，经 `pi-ai` 的流式接口向 provider 请求。C 层是 coding-agent 的持久化旁路：Agent 事件到达 `message_end` 时，`AgentSession` 让 `SessionManager` 记录 JSONL 会话树。C 不是 agent-core 内置的通用存储。

每个箭头的固定源码定位和边界说明见[Pi 剖面](../../docs/systems/pi/README.md)与[代码导读](../../docs/systems/pi/code-walkthrough.md)。本图是静态源码图，不是运行轨迹。
