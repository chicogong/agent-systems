# 跟着 OpenCode 代码看一次工具调用的进度

[返回 OpenCode 首页](README.md) · 固定源码 [`18ef3cc7`](https://github.com/anomalyco/opencode/tree/18ef3cc7c5a25b82114c953a80ccc09f4988f74e)

上一页介绍了工具调用的四个状态。这里继续看一次读取文件的请求：用户消息怎么进入循环，模型的工具调用怎么成为 `ToolPart` 记录，结果又怎样找到原来的记录。

下面先列出阅读顺序，再逐步找源码。伪代码是摘要；实际实现通过流事件和异步服务协作。

```text
SessionPrompt.prompt(input)
  保存用户消息 → loop / runLoop
  选 agent 和 model → SessionTools.resolve → SessionProcessor.process

处理模型流事件：
  tool-input-* → ensureToolCall(callID) → ToolPart.pending
  tool-call    → updateToolCall(callID) → ToolPart.running
  tool-result(success) → completeToolCall(callID) → 若匹配 running part，则 completed
  tool-result(error) / tool-error → failToolCall(callID) → 若匹配 running part，则 error
  结束时仍未完成的调用 → cleanup() → ToolPart.error (interrupted)
```

## 从用户输入开始

`prompt()` 保存用户消息，再调用 `loop()`。`SessionRunState.ensureRunning` 管理这个会话的运行过程；`runLoop` 每轮读出历史和任务，选好 Agent 与模型，准备下一次请求。[保存输入](https://github.com/anomalyco/opencode/blob/18ef3cc7c5a25b82114c953a80ccc09f4988f74e/packages/opencode/src/session/prompt.ts#L1042-L1070) · [启动循环](https://github.com/anomalyco/opencode/blob/18ef3cc7c5a25b82114c953a80ccc09f4988f74e/packages/opencode/src/session/prompt.ts#L1343-L1347) · [准备模型请求](https://github.com/anomalyco/opencode/blob/18ef3cc7c5a25b82114c953a80ccc09f4988f74e/packages/opencode/src/session/prompt.ts#L1081-L1132)

`SessionTools.resolve` 给工具加上插件钩子。正常执行按“插件前置处理→真实工具→插件后置处理”的顺序进行；前面抛出错误时，后面的处理也可能被跳过。`SessionProcessor.process` 负责接收模型逐步返回的事件，交给 `handleEvent`。[工具与钩子](https://github.com/anomalyco/opencode/blob/18ef3cc7c5a25b82114c953a80ccc09f4988f74e/packages/opencode/src/session/tools.ts#L92-L132) · [处理流事件](https://github.com/anomalyco/opencode/blob/18ef3cc7c5a25b82114c953a80ccc09f4988f74e/packages/opencode/src/session/processor.ts#L643-L665)

## 输入正在传来时，先建立记录

`tool-input-start/delta/end` 表示工具输入开始、陆续到达和结束，都可以触发 `ensureToolCall`。程序用调用编号 `callID` 查找记录：已有记录就复用；没有就创建 `pending` 状态的 `ToolPart`，同时记住它属于哪个消息和会话。[接收输入事件](https://github.com/anomalyco/opencode/blob/18ef3cc7c5a25b82114c953a80ccc09f4988f74e/packages/opencode/src/session/processor.ts#L315-L329) · [建立调用记录](https://github.com/anomalyco/opencode/blob/18ef3cc7c5a25b82114c953a80ccc09f4988f74e/packages/opencode/src/session/processor.ts#L216-L253)

完整调用 `tool-call` 到达后，程序把记录改为 `running`，写入参数和开始时间。这里还会检查最近是否反复调用同一个工具，必要时要求 `doom_loop` 许可。收到调用后，程序仍要处理这些执行条件。[记录运行并检查重复调用](https://github.com/anomalyco/opencode/blob/18ef3cc7c5a25b82114c953a80ccc09f4988f74e/packages/opencode/src/session/processor.ts#L331-L382)

## 结果回来时，按编号更新原记录

成功结果交给 `completeToolCall`。找到对应且仍为 `running` 的记录后，它写入 `completed`、输出、附件、元数据和结束时间。错误结果或 `tool-error` 交给 `failToolCall`，同样只更新对应的运行中记录，状态变为 `error`。权限拒绝等错误还可能让处理器结束本轮。[分发结果](https://github.com/anomalyco/opencode/blob/18ef3cc7c5a25b82114c953a80ccc09f4988f74e/packages/opencode/src/session/processor.ts#L383-L420) · [更新成功或错误记录](https://github.com/anomalyco/opencode/blob/18ef3cc7c5a25b82114c953a80ccc09f4988f74e/packages/opencode/src/session/processor.ts#L160-L204)

结束清理时，程序会短暂等待尚未完成的调用；仍没有结果的记录会变成 `error`，并标上 `interrupted: true`，说明它被中断了。阅读错误时，先看原因是工具报错，还是清理时标记的中断。[清理未完成调用](https://github.com/anomalyco/opencode/blob/18ef3cc7c5a25b82114c953a80ccc09f4988f74e/packages/opencode/src/session/processor.ts#L585-L610)

## 整个会话另有一份状态

`SessionStatus` 发布 `busy/retry/idle`（忙碌、重试、空闲）事件。进入空闲时，它删除状态表中的该会话项；查询不存在的项目时默认返回 `idle`。这份状态描述整个会话，`ToolPart` 描述其中一次调用。[会话状态表](https://github.com/anomalyco/opencode/blob/18ef3cc7c5a25b82114c953a80ccc09f4988f74e/packages/opencode/src/session/status.ts#L30-L48) · [发布忙碌与重试状态](https://github.com/anomalyco/opencode/blob/18ef3cc7c5a25b82114c953a80ccc09f4988f74e/packages/opencode/src/session/processor.ts#L639-L691)

还可以在 `runLoop` 结束处找到对未完成工具调用的清理检查。[循环结束检查](https://github.com/anomalyco/opencode/blob/18ef3cc7c5a25b82114c953a80ccc09f4988f74e/packages/opencode/src/session/prompt.ts#L1100-L1129) 本篇依据固定源码，尚未采集真实调用日志；实际事件时间和中断后的恢复效果留待运行检查。
