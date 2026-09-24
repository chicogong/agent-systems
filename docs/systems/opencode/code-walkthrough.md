# 跟着 OpenCode 代码看一次 ToolPart 状态变化

[返回 OpenCode 首页](README.md) · 固定源码 [`18ef3cc7`](https://github.com/anomalyco/opencode/tree/18ef3cc7c5a25b82114c953a80ccc09f4988f74e)

以下伪代码只压缩阅读顺序，**不是原项目代码**。OpenCode 的实现使用 Effect、流事件和会话服务；这里不把异步事件硬说成单一同步调用栈。

```text
SessionPrompt.prompt(input)
  保存用户消息 → loop / runLoop
  选 agent 和 model → SessionTools.resolve → SessionProcessor.process

处理模型流事件：
  tool-input-* → ensureToolCall(callID) → ToolPart.pending
  tool-call    → updateToolCall(callID) → ToolPart.running
  tool-result(success) → completeToolCall(callID) → 若匹配 running part，则 completed
  tool-result(error) / tool-error → failToolCall(callID) → 若匹配 running part，则 error
  未收束调用    → cleanup() → ToolPart.error (interrupted)
```

1. `prompt()` 保存用户消息并调用 `loop()`。后者借助 `SessionRunState.ensureRunning` 管理同一 session 的运行者；`runLoop` 每轮读取历史和任务，按 agent/model 组装下一次模型请求。[prompt](https://github.com/anomalyco/opencode/blob/18ef3cc7c5a25b82114c953a80ccc09f4988f74e/packages/opencode/src/session/prompt.ts#L1042-L1070) · [loop](https://github.com/anomalyco/opencode/blob/18ef3cc7c5a25b82114c953a80ccc09f4988f74e/packages/opencode/src/session/prompt.ts#L1343-L1347) · [runLoop](https://github.com/anomalyco/opencode/blob/18ef3cc7c5a25b82114c953a80ccc09f4988f74e/packages/opencode/src/session/prompt.ts#L1081-L1132)
2. `SessionTools.resolve` 的工具包装会调用插件前置钩子、实际工具、后置钩子；`SessionProcessor.process` 对 `llm.stream` 产生的事件执行 `handleEvent`。这里的前后置钩子属于**工具执行包装**，并不等于 `ToolPart` 的三个状态。[工具包装](https://github.com/anomalyco/opencode/blob/18ef3cc7c5a25b82114c953a80ccc09f4988f74e/packages/opencode/src/session/tools.ts#L92-L132) · [流处理](https://github.com/anomalyco/opencode/blob/18ef3cc7c5a25b82114c953a80ccc09f4988f74e/packages/opencode/src/session/processor.ts#L643-L665)
3. `tool-input-start/delta/end` 都可调用 `ensureToolCall`；该函数按 `callID` 复用已有 part，没有时写入 `pending`，并建立 `callID → partID/messageID/sessionID` 的临时映射。[输入事件](https://github.com/anomalyco/opencode/blob/18ef3cc7c5a25b82114c953a80ccc09f4988f74e/packages/opencode/src/session/processor.ts#L315-L329) · [ensureToolCall](https://github.com/anomalyco/opencode/blob/18ef3cc7c5a25b82114c953a80ccc09f4988f74e/packages/opencode/src/session/processor.ts#L216-L253)
4. `tool-call` 分支同样先确保 part 存在，再把它设为 `running`、写入参数和开始时间。它也检查最近重复调用并可能要求 `doom_loop` 许可，所以“收到完整调用就必然成功执行”不是正确结论。[tool-call 分支](https://github.com/anomalyco/opencode/blob/18ef3cc7c5a25b82114c953a80ccc09f4988f74e/packages/opencode/src/session/processor.ts#L331-L382)
5. `tool-result` 按结果类型分流；成功结果规范化后交给 `completeToolCall`，为匹配的 `running` part 写入 `completed`、输出、元数据、附件及结束时间；错误结果或 `tool-error` 交给 `failToolCall`，仅在匹配且仍为 `running` 时写 `error`。权限拒绝等错误还可令处理器停止本轮。清理阶段等待未收束调用，仍存在的 part 会写成带 `interrupted: true` 的 `error`，不能与正常结果分支混为一谈。[结果分支](https://github.com/anomalyco/opencode/blob/18ef3cc7c5a25b82114c953a80ccc09f4988f74e/packages/opencode/src/session/processor.ts#L383-L420) · [状态写入](https://github.com/anomalyco/opencode/blob/18ef3cc7c5a25b82114c953a80ccc09f4988f74e/packages/opencode/src/session/processor.ts#L160-L204) · [清理](https://github.com/anomalyco/opencode/blob/18ef3cc7c5a25b82114c953a80ccc09f4988f74e/packages/opencode/src/session/processor.ts#L585-L610)
6. `SessionStatus` 另外维护 session 的当前状态并发布 `busy/retry/idle` 事件；进入 `idle` 时删除该 session 的状态表项，查询缺项默认返回 `idle`。它不是工具状态机；一个 session 可以处于 `busy`，其内部某个 ToolPart 仍在 `pending` 或 `running`。[SessionStatus](https://github.com/anomalyco/opencode/blob/18ef3cc7c5a25b82114c953a80ccc09f4988f74e/packages/opencode/src/session/status.ts#L30-L48) · [处理器 busy/retry](https://github.com/anomalyco/opencode/blob/18ef3cc7c5a25b82114c953a80ccc09f4988f74e/packages/opencode/src/session/processor.ts#L639-L691)

最后一项中“可以”表示两套源码状态模型并存的结构性推断，**不是**运行时抓到的同时态。有关中断后的孤儿工具调用，`runLoop` 有显式清理标记检查；本篇不推断其所有边界结果。[循环结束检查](https://github.com/anomalyco/opencode/blob/18ef3cc7c5a25b82114c953a80ccc09f4988f74e/packages/opencode/src/session/prompt.ts#L1100-L1129)
