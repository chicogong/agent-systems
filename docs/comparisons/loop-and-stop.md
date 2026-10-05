# 一轮工具调用后，谁决定下一步？

[返回横向对照](README.md)

资料助手读完一份材料后，还要决定是否继续读下一份、整理答案，或等待你的补充。编码助手也一样：命令返回后，程序把结果送回循环，再决定继续还是结束。下面对照 Pi、mini-SWE-agent、OpenCode 和 Kimi Code，把这个判断在各自源码里找出来。

图中的 steering / steer 可以理解为忙时插入的新指令，follow-up 是后续消息。回合（turn）和步骤（step）在各项目中的范围略有不同，下面会结合具体流程说明。

![四种循环的续跑与停止闸口](../../figures/loop-and-stop/diagram.svg)

[图的文字版](../../figures/loop-and-stop/README.md) · [可编辑图源](../../figures/loop-and-stop/scene.excalidraw) · [PNG 预览](../../figures/loop-and-stop/preview.png)

| 固定范围 | 触发：谁决定下一步 | 状态：看什么 | 工具结果写回 | 停止、拒绝与等待 |
| --- | --- | --- | --- | --- |
| [Pi 核心循环](../systems/pi/code-walkthrough.md) | `runLoop`；`finishTurn` 可改判。 | 消息、工具批次、steering / follow-up 队列。 | tool result；执行失败标 `isError`。 | `finishTurn=end` 优先停；steering 等轮间，follow-up 等结束点。 |
| [mini-SWE 基类](../systems/mini-swe-agent/code-walkthrough.md) | `run()` 每轮检查消息尾部。 | `messages[-1].role`。 | 环境 observation 追加到 `messages`。 | 尾部 `exit` 返回；格式错误可反馈再试，一般异常重抛。 |
| [OpenCode 会话](../systems/opencode/code-walkthrough.md) | processor 返回结果；`runLoop` 再判断。 | `ToolPart` 状态与会话状态分开。 | `tool-result/error` 收束 part。 | `stop` 结束；模型流故障可在 processor 内退避重试；`compact` 转压缩。 |
| [Kimi Code 单 turn](../systems/kimi-code/code-walkthrough.md) | `runTurn`；非 `tool_use` 时问停止回调。 | steer 缓冲、步数、取消信号。 | 工具批次排空 `tool.result` 事件。 | `tool_use` 续步；steer 等步边界；取消/上限可终止。 |

## 怎样读这些差别

Pi 和 Kimi Code 都会接收忙时的新输入。Pi 明分 steering 与 follow-up 两条队列，分别在轮间和结束点处理；Kimi Code 先把活动 turn 的 steer 放进 `steerBuffer`，再在下一 step 或停止回调处刷新。它们都在安排“新指令什么时候参与下一步”，只是等待点不同。

另外两套路径更适合从状态读起：mini-SWE-agent 的基类查看最后一条消息是否为 `exit`；OpenCode 同时记录一个工具调用的状态和整个会话的处理结果。这样读，函数名背后的工作就清楚了：**记录结果 → 检查新输入与停止条件 → 继续或交回控制权**。

可以做一次纸笔推演：命令返回权限错误后，用户又发来一条补充指令。分别沿四行表格标出错误记在哪里、新指令在哪里等待、下一次模型请求前经过哪个判断。你的产物是四条标过判断点的路径；未读到的 CLI 或提供商分支写“待查”即可。

## 源码定位（可选深入）

- **Pi** · `earendil-works/pi@898ab804050730e9dcefb4443875d5a932aa6a32`：[回合与队列决策](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/agent/src/agent-loop.ts#L162-L320)、[工具结果和前置拒绝](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/agent/src/agent-loop.ts#L703-L861)、[整批结果的 `terminate` 判断](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/agent/src/agent-loop.ts#L685-L687)。`finishTurn=end` 优先于自然结束点的 follow-up。`terminate` 检查针对整批已收束结果，其中可能有执行前形成的错误结果；它影响后续循环，单凭该标记不能断言工具都执行成功或 Agent 最终结束。coding-agent 还在 [`message_end` 记录常规消息](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/coding-agent/src/core/agent-session.ts#L921-L943)，这是外层职责。
- **mini-SWE-agent** · `SWE-agent/mini-swe-agent@04d809ceab9df28f9adaed044884180159172930`：[循环、异常与尾部判定](https://github.com/SWE-agent/mini-swe-agent/blob/04d809ceab9df28f9adaed044884180159172930/src/minisweagent/agents/default.py#L88-L157)、[本地提交哨兵](https://github.com/SWE-agent/mini-swe-agent/blob/04d809ceab9df28f9adaed044884180159172930/src/minisweagent/environments/local.py#L24-L56)。限额、成功提交、连续格式错误达阈值可产生 `exit`；一般异常先记录再抛出。[默认 CLI 的交互子类](https://github.com/SWE-agent/mini-swe-agent/blob/04d809ceab9df28f9adaed044884180159172930/src/minisweagent/agents/interactive.py#L58-L94)另有人工确认，表格未覆盖。
- **OpenCode** · `anomalyco/opencode@18ef3cc7c5a25b82114c953a80ccc09f4988f74e`：[外层退出检查](https://github.com/anomalyco/opencode/blob/18ef3cc7c5a25b82114c953a80ccc09f4988f74e/packages/opencode/src/session/prompt.ts#L1081-L1132)、[processor 结果进入 loop](https://github.com/anomalyco/opencode/blob/18ef3cc7c5a25b82114c953a80ccc09f4988f74e/packages/opencode/src/session/prompt.ts#L1272-L1335)、[ToolPart 结果与清理](https://github.com/anomalyco/opencode/blob/18ef3cc7c5a25b82114c953a80ccc09f4988f74e/packages/opencode/src/session/processor.ts#L383-L420)、[停止和退避](https://github.com/anomalyco/opencode/blob/18ef3cc7c5a25b82114c953a80ccc09f4988f74e/packages/opencode/src/session/processor.ts#L641-L695)、[可重试故障判定与上限](https://github.com/anomalyco/opencode/blob/18ef3cc7c5a25b82114c953a80ccc09f4988f74e/packages/opencode/src/session/retry.ts#L85-L205)。`ToolPart` 的 `completed/error` 与会话的 `busy/retry/idle` 是两层；未收束 part 可在[清理](https://github.com/anomalyco/opencode/blob/18ef3cc7c5a25b82114c953a80ccc09f4988f74e/packages/opencode/src/session/processor.ts#L585-L610)时记为 interrupted error。单个 part `error` 不自动令 session 停止或重试。
- **Kimi Code** · `MoonshotAI/kimi-code@75a894e9ad5e8d49509664b3daaa1bbc9bb39432`：[通用循环](https://github.com/MoonshotAI/kimi-code/blob/75a894e9ad5e8d49509664b3daaa1bbc9bb39432/packages/agent-core/src/loop/run-turn.ts#L74-L128)、[工具批次与 step 封口](https://github.com/MoonshotAI/kimi-code/blob/75a894e9ad5e8d49509664b3daaa1bbc9bb39432/packages/agent-core/src/loop/turn-step.ts#L123-L176)、[steer 的缓冲与刷新](https://github.com/MoonshotAI/kimi-code/blob/75a894e9ad5e8d49509664b3daaa1bbc9bb39432/packages/agent-core/src/agent/turn/index.ts#L578-L657)。新 steer 在活动 turn 中先[入缓冲](https://github.com/MoonshotAI/kimi-code/blob/75a894e9ad5e8d49509664b3daaa1bbc9bb39432/packages/agent-core/src/agent/turn/index.ts#L130-L143)，不立即取消 step。工具[授权回调](https://github.com/MoonshotAI/kimi-code/blob/75a894e9ad5e8d49509664b3daaa1bbc9bb39432/packages/agent-core/src/agent/turn/index.ts#L658-L692)位于执行前；拒绝后的完整消息路径尚未核对。

## 遇到错误时怎样读，以及本篇范围

- **先辨认错误类型。** Pi 的工具错误可成为 `isError` 结果，供后续判断；mini-SWE-agent 分别处理格式错误和一般异常；OpenCode 对策略接受的模型流故障延迟后再试（退避重试）；Kimi Code 本篇只追到工具批次、停止与授权关口，拒绝消息如何呈现仍待核对。
- **覆盖范围不等。** Pi 行连接 agent-core 与部分 coding-agent 外壳；mini-SWE-agent 只覆盖 `DefaultAgent`/本地环境，默认 CLI 的交互子类另算；OpenCode 只读 `session` 路径，未审计所有 provider、MCP 和插件；Kimi Code 只读 `agent-core` 的单个 turn，未追踪 CLI 输入接线、外层 goal 运行或持久化恢复。
- **证据类型。** 四篇于 2026-09-23 核对，均为固定源码阅读，尚无同任务运行轨迹；并发工具副作用、人工等待时长、取消竞态、故障恢复和发布版本对应关系仍待实测。“可继续”描述源码中的允许分支，速度、可靠性和实际完成率需另做比较。
