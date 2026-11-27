# 跟着 OpenCode 代码走一轮：流式占位、死循环熔断与中断兜底

[返回 OpenCode 首页](README.md) · 固定源码 [`18ef3cc7`](https://github.com/anomalyco/opencode/tree/18ef3cc7c5a25b82114c953a80ccc09f4988f74e)

如果让你手写一个接收大模型流式工具事件的状态机，最容易漏掉三个边界：流式参数分十几个增量分片到达时怎么避免重复建单？模型鬼打墙连续三次（DOOM_LOOP_THRESHOLD = 3）用一模一样的参数调同一个工具时怎么刹住车？网络断流或用户强退的那一瞬间，卡在半空中的 `pending` 和 `running` 调用由谁来善后？

下面我们沿着 `packages/opencode/src/session` 里的真实事件流向，把这整条状态机链路从头拆到尾：

```text
SessionPrompt.prompt(input)
  └─► 落盘用户消息 → loop() / SessionRunState.ensureRunning → runLoop()
        └─► 选定 Agent 与模型 → SessionTools.resolve(挂载前后置插件钩子) → SessionProcessor.process()

SessionProcessor.handleEvent(流事件分发)：
  ├─ tool-input-start/delta/end ──► ensureToolCall(callID)   ──► 幂等创建或复用 ToolPart [pending]
  ├─ tool-call                  ──► updateToolCall(callID)   ──► 写入完整参数 + doom_loop 检查 [running]
  ├─ tool-result (成功)         ──► completeToolCall(callID) ──► 仅匹配 running 记录落定 [completed]
  ├─ tool-result (失败)/error   ──► failToolCall(callID)     ──► 仅匹配 running 记录落定 [error]
  └─ 流结束收尾                 ──► cleanup() 中断收敛       ──► 未完成记录统一盖戳 [error, interrupted: true]
```

## 1. 会话循环拉起与洋葱钩子包装

当用户发来新指令，`SessionPrompt.prompt()` 先把用户消息持久化入库，随后进入 `loop()`，由 `SessionRunState.ensureRunning` 保证同一会话受控运行；进入 `runLoop` 后，每一轮读取最新会话历史，挑好当前 Agent 配置与底层模型，准备发起下一轮流式请求（见[保存输入](https://github.com/anomalyco/opencode/blob/18ef3cc7c5a25b82114c953a80ccc09f4988f74e/packages/opencode/src/session/prompt.ts#L1042-L1070)、[启动循环](https://github.com/anomalyco/opencode/blob/18ef3cc7c5a25b82114c953a80ccc09f4988f74e/packages/opencode/src/session/prompt.ts#L1343-L1347)与[准备模型请求](https://github.com/anomalyco/opencode/blob/18ef3cc7c5a25b82114c953a80ccc09f4988f74e/packages/opencode/src/session/prompt.ts#L1081-L1132)）。

在把工具列表交给模型流之前，`SessionTools.resolve` 为每个工具织好了一层「前置插件钩子 → 真实工具执行 → 后置插件钩子」的包装壳；只要前置钩子抛错，后续真实执行就会被短路拦下。随后，`SessionProcessor.process` 开始逐条拉取模型流式事件并喂给核心分发器 `handleEvent`（见[工具与钩子](https://github.com/anomalyco/opencode/blob/18ef3cc7c5a25b82114c953a80ccc09f4988f74e/packages/opencode/src/session/tools.ts#L92-L132)与[处理流事件](https://github.com/anomalyco/opencode/blob/18ef3cc7c5a25b82114c953a80ccc09f4988f74e/packages/opencode/src/session/processor.ts#L643-L665)）。

## 2. 幂等流式占位与 `doom_loop` 死循环急刹车

在流式生成工具参数的过程中，底层适配器会连续吐出 `tool-input-start`、若干个 `tool-input-delta` 以及 `tool-input-end`。OpenCode 让这三种事件全部汇入同一个幂等入口 `ensureToolCall(callID)`：查表发现该 `callID` 已有记录就直接复用，没有才新建一张状态为 `pending` 的 `ToolPart` 挂到当前助手消息和会话下——哪怕增量事件乱序或密集刷屏，也绝不会生出双胞胎记录（见[接收输入事件](https://github.com/anomalyco/opencode/blob/18ef3cc7c5a25b82114c953a80ccc09f4988f74e/packages/opencode/src/session/processor.ts#L315-L329)与[建立调用记录](https://github.com/anomalyco/opencode/blob/18ef3cc7c5a25b82114c953a80ccc09f4988f74e/packages/opencode/src/session/processor.ts#L216-L253)）。

等到完整参数拼装完毕、`tool-call` 事件正式抵达时，`updateToolCall` 把这张零件单推进到 `running` 状态，记下完整输入与开始时间。紧接着这里埋了一处极其实用的工程护栏——**死循环检测**（`doom_loop`，见[记录运行并检查重复调用](https://github.com/anomalyco/opencode/blob/18ef3cc7c5a25b82114c953a80ccc09f4988f74e/packages/opencode/src/session/processor.ts#L331-L382)）：

- 真实编码场景里，模型偶尔会卡进认知死胡同，比如连续三次用完全相同的参数去调同一个搜索或修改工具，放任不管很快就会烧穿额度。
- OpenCode 在刚切入 `running` 的关口回看最近调用历史，一旦抓到连续重复调用，立刻触发专门的 `doom_loop` 许可拦截，把「要不要允许它继续原地打转」的决定权交回权限层，而不是盲目放行。

## 3. 严格状态守卫对账与双保险中断清扫

当工具执行返回时，为什么不能拿到 `callID` 就无脑覆盖状态？因为在异步流和取消竞态下，迟到的回执可能撞上已经被清理的记录。

因此无论是成功分支 `completeToolCall` 还是失败分支 `failToolCall`，源码都加上了严格的前置状态守卫：**只有根据 `callID` 找到对应记录、且该记录当前确实处于 `running` 状态时**，才允许落定为 `completed`（写入输出、附件、元数据与结束时间）或 `error`（写入错误信息与结束时间；若遇到明确的权限拒绝等硬错误，还会通知处理器提前终止本轮）（见[分发结果](https://github.com/anomalyco/opencode/blob/18ef3cc7c5a25b82114c953a80ccc09f4988f74e/packages/opencode/src/session/processor.ts#L383-L420)与[更新成功或错误记录](https://github.com/anomalyco/opencode/blob/18ef3cc7c5a25b82114c953a80ccc09f4988f74e/packages/opencode/src/session/processor.ts#L160-L204)）。

更关键的是「流突然断了怎么办」。未完成工具调用的中断收敛全部由处理器的 `cleanup()` 统一负责：

1. **处理器收尾清扫与中断标记**：单次流处理结束进入 [`cleanup()`](https://github.com/anomalyco/opencode/blob/18ef3cc7c5a25b82114c953a80ccc09f4988f74e/packages/opencode/src/session/processor.ts#L585-L610) 时，程序会给在途调用留一个短暂宽限窗口；窗口过后仍未拿到结果的在途 `pending` 或 `running` 零件单，一律强制转为 `error` 并打上 `interrupted: true` 标记。排查故障日志时，先看 `interrupted` 字段就能一秒分清「工具自己执行挂了」还是「工具还没跑完就被迫中断了」。
2. **外层循环退出条件判定**：需要澄清的是，外层 `runLoop` 中调用的 [`prompt.ts` L1100-L1129](https://github.com/anomalyco/opencode/blob/18ef3cc7c5a25b82114c953a80ccc09f4988f74e/packages/opencode/src/session/prompt.ts#L1100-L1129)（以及主调度循环 [`prompt.ts` L1221-L1286](https://github.com/anomalyco/opencode/blob/18ef3cc7c5a25b82114c953a80ccc09f4988f74e/packages/opencode/src/session/prompt.ts#L1221-L1286)）是用来判定本轮会话是否已满足循环退出条件（例如是否无需进一步工具调用或用户交互），而不是在循环结束后去二次清扫未完成的 `pending`/`running` 状态；在途零件的中断善后完全由内层 `cleanup()` 严格盖戳收敛。

## 4. 外层 `SessionStatus` 的小巧思：空闲即删键

最后看一眼宏观会话状态表 [`SessionStatus`](https://github.com/anomalyco/opencode/blob/18ef3cc7c5a25b82114c953a80ccc09f4988f74e/packages/opencode/src/session/status.ts#L30-L48) 与处理器里[发布忙碌与重试状态](https://github.com/anomalyco/opencode/blob/18ef3cc7c5a25b82114c953a80ccc09f4988f74e/packages/opencode/src/session/processor.ts#L639-L691)的配合。

一个长期驻留的本地服务可能积累几百上千个历史会话，如果每个会话都在内存状态表里常驻一条 `{ type: "idle" }`，纯属浪费内存。OpenCode 的写法非常干净：内存字典只存当前正处于 `busy` 或 `retry` 的活跃会话；一旦某个会话收工转入 `idle`，**直接把该 `sessionID` 从内存表里 `delete` 掉**，而外部查询任何不存在的 `sessionID` 时一律兜底返回 `{ type: "idle" }`——零垃圾回收负担，重启进程后所有历史会话也天然处于干净的空闲态。

## 来源与边界

本文基于官方仓库固定提交 [`anomalyco/opencode@18ef3cc7c5a25b82114c953a80ccc09f4988f74e`](https://github.com/anomalyco/opencode/tree/18ef3cc7c5a25b82114c953a80ccc09f4988f74e) 的静态源码分析整理，核对范围为 `packages/opencode/src/session` 目录。不同模型服务商流式分片的细微时序差异及外部插件钩子的自定义异常行为需结合具体接入环境核查。
