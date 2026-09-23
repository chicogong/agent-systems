# OpenHands 动作／结果时序图：文字版

[返回 OpenHands 首篇](../../docs/systems/openhands/README.md) · [图源](scene.excalidraw) · [SVG](diagram.svg) · [PNG](preview.png)

四条泳道从左到右是 `LocalConversation`、`Agent`、`Tool`、`EventLog`，时间从上往下。用户消息先成为 `MessageEvent`。`run()` 调用 `Agent.step()`；模型产生工具调用后，Agent **先发** `ActionEvent` 进入事件历史。若需确认，本次运行停在 `WAITING_FOR_CONFIRMATION`。再次获准运行时，Agent 找到当前分支上未匹配的动作，再交给工具执行；无须确认的动作则在同一次 step 中直接进入工具。工具把 `Observation` 返回给 Agent；Agent 包装成 `ObservationEvent` 或错误事件，经会话回调写入事件历史。

图中“再次运行”和“直接执行”是条件路径，不表示一个工具调用总要经历两次 `run()`。用户拒绝会产生 `UserRejectObservation`，不会调用工具。完整来源和例外见[关键代码路径](../../docs/systems/openhands/code-walkthrough.md)。

本图映射官方 SDK 的固定提交 [`6ebd820d10794f1b52bb06ef6c19512888a1401b`](https://github.com/OpenHands/software-agent-sdk/tree/6ebd820d10794f1b52bb06ef6c19512888a1401b) 中同步 LocalConversation + 默认 Agent 的**静态源码路径**，不是运行轨迹；不覆盖 Agent Server、ACP 后端或工具沙箱实现。
