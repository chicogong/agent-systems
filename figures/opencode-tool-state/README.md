# OpenCode 工具调用状态机：文字版

[返回 OpenCode 剖面](../../docs/systems/opencode/README.md) · [图源](scene.excalidraw) · [SVG](diagram.svg) · [PNG](preview.png)

图从上向下读一条工具调用，以 `callID` 为线索：输入相关流事件可让 `SessionProcessor.ensureToolCall` 创建或复用 `ToolPart.pending`；完整 `tool-call` 事件把它推进至 `running`；匹配且处于 `running` 的调用收到成功 `tool-result` 时进入 `completed`，收到错误结果或 `tool-error` 时进入 `error`。右侧虚线表示清理阶段可把未收束的 `pending` 直接标为 `error`；尚未收束的 `running` 也可由清理进入 `error`，并写入 `interrupted: true`。因此不能断言所有错误都经过正常的结果事件，也不能断言每个错误事件都更新了一个 part。`completed` 与 `error` 是两个终点，不是串行步骤。每个状态变更通过会话服务更新 part。

底部单独标出 session 层 `busy / retry / idle`：它是 `SessionStatus` 发布的状态，不表示三个必经步骤，也不能把 `idle` 当成某个 ToolPart 的完成状态。`retry` 来自模型流处理外层的 `SessionRetry.policy`：只有策略判为可重试且未超过次数上限时才发布，带尝试次数与下次尝试时间；单个 ToolPart 进入 `error` 不自动触发这个状态。工具执行包装中的 `tool.execute.before → item.execute → tool.execute.after` 放在图下作为代码路径说明，不画成另一条 ToolPart 状态箭头。[完整证据定位](../../docs/systems/opencode/code-walkthrough.md) · [重试策略源码](https://github.com/anomalyco/opencode/blob/18ef3cc7c5a25b82114c953a80ccc09f4988f74e/packages/opencode/src/session/retry.ts#L178-L209)

图是固定源码版本 `18ef3cc7c5a25b82114c953a80ccc09f4988f74e` 的**静态机制图**；未运行真实请求、未覆盖 provider 差异、中断恢复和持久化故障。视觉布局故意采用状态机而非 Pi 的分区卡片：此图回答“一个对象如何变状态”，不是“系统有哪些层”。
