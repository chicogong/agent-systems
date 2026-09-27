# 工具之后的四个决策点：文字版

[返回对照正文](../../docs/comparisons/loop-and-stop.md) · [图源](scene.excalidraw) · [SVG](diagram.svg) · [PNG](preview.png)

图按行读，不是四个项目串行执行的流程。每行先给出固定源码切面，再从“工具结果写回”走向该系统自己的控制闸口：

1. **Pi**：tool result 进入 `runLoop` 的消息路径。steering 等轮间，follow-up 等本来将结束时；`finishTurn=end` 可优先结束。
2. **mini-SWE-agent**：环境观察进入 `messages`；`DefaultAgent.run()` 在一轮保存后看最后消息，非 `exit` 再循环，`exit` 则返回其 `extra`。
3. **OpenCode**：流事件把结果写成 `ToolPart.completed/error`；`SessionProcessor.process()` 只返回 `continue / stop / compact`，由外层循环处理。`stop` 会退出外层循环；`compact` 创建压缩任务后再处理；`continue` 允许循环继续。图中的“流内 retry”指模型流处理器内按策略退避，**不是**与上述三种出口并列的返回值。调用级 `ToolPart.error` 本身既不等于会话停止，也不自动授权重试。
4. **Kimi Code**：工具批次排空 `tool.result` 事件；`tool_use` 后 `runTurn()` 进入下一 step。活动 turn 收到的 steer 在 step 边界刷新；无继续请求、取消或上限可能结束当前 turn。

方框颜色仅帮助辨认四行，不表示性能或证据强弱。图省略了各项目的 provider、CLI、并行工具副作用和恢复路径；具体停止/拒绝分支及固定 SHA 见[正文表格](../../docs/comparisons/loop-and-stop.md)。四行均是 2026-09-23 核对的**固定源码静态切面**，不是一条实际运行轨迹。mini-SWE-agent 行特指基类加本地环境；Kimi Code 行限单个 turn；Pi 行含部分 coding-agent 外壳；OpenCode 行限 session 路径，因此证据粒度不等。

2026-09-27 重开同一 OpenCode 固定提交核对：[`process` 内部重试和出口](https://github.com/anomalyco/opencode/blob/18ef3cc7c5a25b82114c953a80ccc09f4988f74e/packages/opencode/src/session/processor.ts#L641-L695)先处理需压缩状态，再依据处理器阻塞或 assistant 消息错误决定停止；这里的错误不是任意 `ToolPart.error`。[`failToolCall`](https://github.com/anomalyco/opencode/blob/18ef3cc7c5a25b82114c953a80ccc09f4988f74e/packages/opencode/src/session/processor.ts#L186-L205)只在特定拒绝错误与配置条件下设置阻塞；[`外层消费出口`](https://github.com/anomalyco/opencode/blob/18ef3cc7c5a25b82114c953a80ccc09f4988f74e/packages/opencode/src/session/prompt.ts#L1319-L1335)把停止与压缩分开。此次返修只修正图内的层级歧义，没有运行真实 provider、故障恢复或审批路径。
