# Pi 分层图的文字版

[返回 Pi 剖面](../../docs/systems/pi/README.md) · [图源](scene.excalidraw) · [SVG](diagram.svg) · [PNG](preview.png)

A 层是应用入口：CLI/TUI、RPC/SDK 等方式进入 coding-agent，由 `AgentSession` 组织 Extensions、Skills 等资源，并调用 B 层的 `Agent.prompt()`。B 层是运行核心：`Agent.prompt()` 进入 `runLoop`，后者处理模型和工具回合，经 `pi-ai` 的流式接口向 provider 请求。C 层是 coding-agent 的会话记录：Agent 事件到达 `message_end` 时，`AgentSession` 向 `SessionManager` 追加消息，维护会话树。`SessionManager` 也可纯内存运行；启用持久化时才可能写入 JSONL，首次写盘可能延后。C 不是 agent-core 内置的通用存储。

本图按固定源码 898ab804 绘制。每个箭头的源码定位和边界说明见[Pi 剖面](../../docs/systems/pi/README.md)与[代码导读](../../docs/systems/pi/code-walkthrough.md)。本图是静态源码图，不是运行轨迹。
