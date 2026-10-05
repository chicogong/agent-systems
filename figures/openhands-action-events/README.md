# OpenHands 动作／结果时序图：文字版

[返回 OpenHands 首篇](../../docs/systems/openhands/README.md) · [图源](scene.excalidraw) · [SVG](diagram.svg) · [PNG](preview.png)

模型提出修改文件时，OpenHands 先记录“准备做什么”，允许执行后，再记录“做完拿到什么”。图的四列分别是会话管理器 `LocalConversation`、Agent、工具 `Tool` 和事件清单 `EventLog`，时间从上往下走。

先看主路径：

1. `send_message()` 把用户输入记为 `MessageEvent`（消息事件）。`run()` 开始工作，调用 `Agent.step()`。
2. 模型提出工具调用，Agent 先生成 `ActionEvent`（动作事件），写进事件清单。图中“动作先入账”就是先记下这件待办动作。
3. 程序检查确认条件。无须确认时，同一步就把动作交给工具；需要确认时，先走下面的等待分支。
4. 工具返回 `Observation`（观察结果）。Agent 把它整理成 `ObservationEvent`（结果事件）；图中的 `ValueError` 则整理成 `AgentErrorEvent`（错误事件）。会话回调接收这些事件，写进清单，与原动作对应起来。

**需要用户确认时，先停在虚线框内。** 会话进入 `WAITING_FOR_CONFIRMATION`（等待确认），本次 `run()` 在执行工具前结束。接入 SDK 的宿主程序必须先取得用户批准，再调用 `run()`；这条同步路径把再次调用视为批准。Agent 随后找出当前分支里还没有结果的动作，继续执行。图中“获准后再次 run()”强调的就是这个先后顺序。

用户拒绝时，程序写入 `UserRejectObservation`（用户拒绝的结果），跳过工具执行。无需确认的动作则直接走主路径，无须经过两次 `run()`。[函数和具体条件](../../docs/systems/openhands/code-walkthrough.md)

多个工具并行工作时，结果事件仍可按原次序记录，实际修改文件或远端数据的先后要看工具执行过程。

本图依据官方 SDK 固定提交 [`6ebd820d10794f1b52bb06ef6c19512888a1401b`](https://github.com/OpenHands/software-agent-sdk/tree/6ebd820d10794f1b52bb06ef6c19512888a1401b)，只讲同步 `LocalConversation` 与默认 Agent 的这条流程，尚未采集运行记录。Agent Server、ACP 后端和工具沙箱实现留在图外。
