# OpenClaw：一条请求怎样找到会话

[返回 OpenClaw 首篇](../../docs/systems/openclaw/README.md) · [图源](scene.excalidraw) · [SVG](diagram.svg) · [PNG](preview.png)

你有两段助手会话，一段维护项目，一段整理资料。新任务到来时，Gateway（请求网关）先找到它应该接入的会话，再确认请求者有权在那里开始工作。图从左到右展示这段准备过程。

## 跟着请求往右走

1. **读请求，检查开始前条件。** `agent RPC` 是一次远程调用请求，明确带上 `sessionKey`（会话标识），还可能包含 `agentId`（助手标识）。网关从连接上下文识别调用者身份，图中用 `caller` 标注；它不属于用户填写的 RPC 请求字段。网关结合这份身份检查参数和 `preflight`（运行前条件）。
2. **检查 1：确认会话属于哪个助手。** 图中的“确认归属”对应 `owner`（会话所属助手）的检查。程序根据会话标识的前缀、已保存的记录和可选 `agentId` 核对归属。
3. **检查 2：检查目标能否使用。** 核对目标约束与会话可用状态，并保留去重标识。图中的 `reserveDedupe` 对应保留标识这一步。
4. **检查 3：准备最终要操作的会话。** `prepareAgentSession()` 把请求目标整理为内部使用的 `canonicalKey` 与 `canonicalSessionAgentId`，分别表示最终会话和所属助手。
5. **检查 4：对最终目标检查权限。** 程序确认请求者可以创建或修改这段会话。通过后，才交给 `admission / dispatch`（图中的“接纳、派发”，即接入运行调度）处理后续工作。

图下方的说明是在提醒这个顺序：请求先给出一个会话名字，权限检查再针对系统整理后的实际目标；检查通过后，后续调度和运行才有机会开始。

## 红色出口分别表示哪里需要停下

格式错误或助手归属冲突，要先修正请求；目标约束冲突或会话不可用，停止向该目标推进；准备会话失败，先处理准备问题；没有创建或修改权限，则停在授权检查处。各出口对应不同阶段，查错时沿它所在的位置往前看。

## 版本与范围

本图来自官方 [`openclaw/openclaw@b373c9a9bcd4954ccdab963e3ed71336302b82be`](https://github.com/openclaw/openclaw/tree/b373c9a9bcd4954ccdab963e3ed71336302b82be) 的 Gateway `agent` RPC **显式 `sessionKey`** 源码路径。图根据代码说明流程，尚未启动网关验证。

`chat.send`、各渠道入站、未给 key 或只给 `sessionId` 的请求、实际 Agent 运行外壳、消息投递与重试，需另看相应入口。逐步来源见[代码导读](../../docs/systems/openclaw/code-walkthrough.md)。
