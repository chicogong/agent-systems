# Pi 分层图的文字版

[返回 Pi 讲解](../../docs/systems/pi/README.md) · [图源](scene.excalidraw) · [SVG](diagram.svg) · [PNG](preview.png)

让 Pi 读取一个文件时，可以沿图中的 A、B、C 看三部分怎样合作：应用接收任务，核心安排模型与工具工作，应用再保存过程。

- **A：从入口接到任务。** CLI/TUI 是终端命令和交互界面，RPC/SDK 供其他程序接入。`pi-coding-agent` 是应用外壳，里面的 `AgentSession` 管理当前会话，组织代码扩展（Extensions）和工作指导（Skills）等资源，再调用 `Agent.prompt()` 交出任务。
- **B：模型和工具一轮轮合作。** `Agent` 保管当前消息和等待处理的输入；`runLoop` 安排模型请求与工具调用。`pi-ai` 用流式接口联系模型服务商（provider），逐步接收回复。有工具调用时，程序执行工具，把结果交给下一轮模型。
- **C：把消息记进会话。** 核心发出 `message_end`（一条消息已结束）事件，`AgentSession` 收到后，把消息交给 `SessionManager`。后者保留消息的父子关系，组织成会话树。

图中的 C 由 coding-agent 应用负责。`SessionManager` 可以只用内存；启用文件保存时，才会写 JSONL（每行一条记录的文件），首次写盘还可能延后。其他应用只接入运行核心时，可以自行选择保存方式。

本图按固定源码 `898ab804` 整理，尚未采集这条流程的实际运行记录。箭头对应的函数见[Pi 讲解](../../docs/systems/pi/README.md)与[可选代码导读](../../docs/systems/pi/code-walkthrough.md)。
