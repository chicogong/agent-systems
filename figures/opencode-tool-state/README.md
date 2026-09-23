# OpenCode 工具调用状态机：文字版

[返回 OpenCode 剖面](../../docs/systems/opencode/README.md) · [图源](scene.excalidraw) · [SVG](diagram.svg) · [PNG](preview.png)

图沿时间从左向右读。一条工具调用以 `callID` 为线索：输入相关流事件可让 `SessionProcessor.ensureToolCall` 创建或复用 `ToolPart.pending`；完整 `tool-call` 事件把它推进至 `running`；成功 `tool-result` 进入 `completed`，错误结果、`tool-error`，或清理阶段未收束的调用进入 `error`。`completed` 与 `error` 是两个终点，不是串行步骤。每个状态变更通过会话服务更新 part。

底部单独标出 session 层 `busy / retry / idle`：它是 `SessionStatus` 发布的状态，不能把其 `idle` 当成某个 ToolPart 的完成状态。工具执行包装中的 `tool.execute.before → item.execute → tool.execute.after` 放在图下作为代码路径说明，不画成另一条 ToolPart 状态箭头。[完整证据定位](../../docs/systems/opencode/code-walkthrough.md)

图是固定源码版本 `18ef3cc7c5a25b82114c953a80ccc09f4988f74e` 的**静态机制图**；未运行真实请求、未覆盖 provider 差异、中断恢复和持久化故障。视觉布局故意采用状态机而非 Pi 的分区卡片：此图回答“一个对象如何变状态”，不是“系统有哪些层”。
