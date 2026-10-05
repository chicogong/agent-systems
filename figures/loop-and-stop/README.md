# 工具之后的四个决策点：文字版

[返回对照正文](../../docs/comparisons/loop-and-stop.md) · [图源](scene.excalidraw) · [SVG](diagram.svg) · [PNG](preview.png)

按行读这张图，每行对应一个项目。工具结果回来后，程序根据新输入和停止条件，安排继续还是结束。中间一列写结果送到哪里，右边一列写各系统接着做、等待或停止的条件。

1. **Pi：看轮间输入和结束条件。** 工具结果（tool result）进入 `runLoop` 的消息。中途调整方向的 steering 在轮间处理，后续消息 follow-up 等原本准备结束时处理；`finishTurn=end` 可优先结束。
2. **mini-SWE-agent：看最后一条消息。** 执行环境的结果进入 `messages`。`DefaultAgent.run()` 保存本轮后查看末条消息：角色为 `exit` 时，返回其中的 `extra`；其他情况继续循环。
3. **OpenCode：先记工具状态，再看会话判断。** 调用结果写入 `ToolPart.completed/error`。随后 `SessionProcessor.process()` 返回 `continue`（继续）、`stop`（停止）或 `compact`（压缩），交给外层循环处理。压缩时先创建压缩任务，再处理后续步骤。
4. **Kimi Code：在步骤之间处理新输入。** 一批工具的 `tool.result` 事件收齐后，`tool_use` 让 `runTurn()` 进入下一步（step）。正在工作时收到的 steer 先暂存，到步骤间再更新输入；没有继续请求、收到取消信号或达到上限时，可结束本回合（turn）。

OpenCode 图中的 `retry` 另指模型流出错后按策略等待再试。它发生在处理器内部，和上述三个返回值分开看。一个工具调用变成 `error` 后，会话是继续、停止还是压缩，要看会话自己的判断条件。

## 对照范围与源码

颜色帮助认出四行，比较时还要看各行范围：Pi 连接核心循环和部分终端应用；mini-SWE-agent 限基类与本地环境；OpenCode 限会话路径；Kimi Code 限一个 turn。模型服务商、命令行接线、并发动作和恢复另行阅读。具体分支和固定版本见[正文表格](../../docs/comparisons/loop-and-stop.md)。本图依据固定源码，尚未做四个系统的同任务运行比较。

2026-09-27 补核 OpenCode 同一固定提交：[`process` 内部重试和出口](https://github.com/anomalyco/opencode/blob/18ef3cc7c5a25b82114c953a80ccc09f4988f74e/packages/opencode/src/session/processor.ts#L641-L695)先处理压缩需要，再根据处理器阻塞或 assistant 消息错误决定停止。[`failToolCall`](https://github.com/anomalyco/opencode/blob/18ef3cc7c5a25b82114c953a80ccc09f4988f74e/packages/opencode/src/session/processor.ts#L186-L205)只在指定拒绝错误与配置条件下设置阻塞；[`外层消费出口`](https://github.com/anomalyco/opencode/blob/18ef3cc7c5a25b82114c953a80ccc09f4988f74e/packages/opencode/src/session/prompt.ts#L1319-L1335)分别处理停止和压缩。这次核对覆盖源码分支，真实模型请求、故障恢复和审批仍需运行检查。
