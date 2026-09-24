# 跟着 Pi 代码走一轮

[返回 Pi 首页](README.md) · 固定源码版本 [`898ab804`](https://github.com/earendil-works/pi/tree/898ab804050730e9dcefb4443875d5a932aa6a32)

以下是便于阅读的**逻辑摘要**，不是原项目源码复制，也不覆盖所有 provider、异常和插件分支。本文的行为描述仅来自固定版本的静态实现，尚未做故障注入或跨 provider 运行验证。

## 30 秒范围

- **本篇只追**：固定版本里从 `Agent.prompt()` → `runLoop` / 工具批次，到 coding-agent `SessionManager` 会话投影的一条控制路径。
- **不覆盖**：全部 provider、插件、故障注入或跨部署的运行验证；也不把编码外壳的恢复策略外推为 agent-core 合同。
- **固定 commit**：[`898ab804`](https://github.com/earendil-works/pi/tree/898ab804050730e9dcefb4443875d5a932aa6a32)

1. `Agent.prompt()` 准备用户消息并进入 `runAgentLoop`。若已有运行，它拒绝第二个 `prompt()`，提示改用队列或等待结束。[入口](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/agent/src/agent.ts#L367-L442)
2. `runLoop` 启动回合。它有处理模型与工具的内层循环，也有在自然结束点检查 follow-up 的外层循环；因此“模型只回复一次”和“本次 Agent 运行结束”不是同一概念。[循环](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/agent/src/agent-loop.ts#L162-L320)
3. 每次请求模型前，先执行可选 `prepareRequest`；再变换 Agent 内部上下文，通过 `convertToLlm` 形成模型可理解的消息，交由流式接口处理。[回合准备](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/agent/src/agent-loop.ts#L181-L241) · [请求边界](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/agent/src/agent-loop.ts#L380-L406)
4. 对工具调用，先定位工具、处理并校验参数，运行可选 `beforeToolCall`；只有通过准备的调用才执行工具并经过 `afterToolCall`。找不到工具、校验失败或前置拦截则直接生成错误结果，不进入后置钩子。[前置处理](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/agent/src/agent-loop.ts#L703-L771) · [执行与后置](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/agent/src/agent-loop.ts#L773-L861)
5. 默认批次模式为并行；全局设置或其中一个工具要求顺序模式时，整批顺序执行。并行路径等待后按原调用顺序写入结果，但这不保证外部副作用没有竞争。输出长度截断时，整批工具调用都会形成失败结果，不拿可能不完整的参数执行。[默认模式](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/agent/src/agent.ts#L244-L250) · [执行模式](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/agent/src/agent-loop.ts#L505-L520) · [并行收集](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/agent/src/agent-loop.ts#L583-L657) · [截断处理](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/agent/src/agent-loop.ts#L475-L499)
6. `steer()` 和 `followUp()` 进入两条进程内队列，不是磁盘记忆。steering 在首次请求前及回合间取出；follow-up 在本次运行原本准备结束时取出。[队列](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/agent/src/agent.ts#L142-L173) · [调度](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/agent/src/agent-loop.ts#L174-L215) · [结束点](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/agent/src/agent-loop.ts#L279-L320)
7. coding-agent 的 `AgentSession` 订阅事件，在 `message_end` 把常规消息交给 `SessionManager`；后者维护可持久化为 JSONL 的会话树，并投影当前分支给模型上下文。这是 coding-agent 的实现，不是 agent-core 的普遍存储合同。[写入](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/coding-agent/src/core/agent-session.ts#L921-L943) · [会话树](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/coding-agent/src/core/session-manager.ts#L976-L1005) · [上下文投影](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/coding-agent/src/core/session-manager.ts#L543-L582)

把其中最关键的控制关系压缩成伪代码：

```text
prompt(input) → runLoop
  每次模型请求前：transformContext → convertToLlm → streamFn
  若有完整的 toolCall：校验/前置拦截 → [获准才 execute/后置处理] → toolResult
  回合间：检查 steering；本来要结束时：检查 follow-up
  coding-agent 收到 message_end → SessionManager 记录/投影当前分支
```

这里的箭头表示阅读顺序，不是逐行调用栈；尤其最后一行属于应用层的事件订阅，不在 `runLoop` 内部。

这里的“追加”描述常规消息路径，不应推断文件永远只追加：`SessionManager` 还存在[重写文件路径](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/coding-agent/src/core/session-manager.ts#L1124-L1134)。尚未运行故障注入测试，因此不声称恢复或持久化行为在所有边界条件下已验证。

## 再看三个容易误读的控制点

**一，工具错误不自动等于 Agent 失败。**`tool.execute()` 抛错会被包装成 `isError` 的 tool result，仍通过结果消息进入后续上下文；`afterToolCall` 可调整执行后的结果，若该钩子抛错也会转成错误结果。单个工具失败后，模型可能看到错误并再作选择，但这不等于系统保证重试。只有当前批次中**每个已完成调用**的结果都带 `terminate: true`，批次判定才要求结束；单个 `terminate` 不足以推断整批必停。[工具执行](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/agent/src/agent-loop.ts#L773-L814) · [后置钩子](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/agent/src/agent-loop.ts#L816-L861) · [批次结束条件](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/agent/src/agent-loop.ts#L685-L687)

**二，结束前有明确优先级。**`finishTurn` 若返回 `end`，底层 loop 直接发 `agent_end`，不再走自然停止点的 follow-up 检查。若返回 `continue`，只有没有工具调用或队列消息带来下一轮时，才补一次“只用已有上下文”的回合。耗时的 `prepareNextTurn` 之后，还会在先前未取到 steering 时再检查队列，避免等待期间输入被忽略。[回合决策](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/agent/src/agent-loop.ts#L279-L320) · [准备期间的 steering](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/agent/src/agent-loop.ts#L181-L207)

**三，`continue()` 不是任意重放。**若 Agent 当前最后一条是 assistant，`continue()` 先尝试取 steering，再取 follow-up；两者都没有就报错。普通 continuation 入口至少要有消息，且不允许以 assistant 作为尾消息；真正送到 provider 前，注释还要求经 `convertToLlm` 转换后的尾消息是 user 或 tool result，这一点底层入口无法提前验证。[`Agent.continue()`](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/agent/src/agent.ts#L380-L408) · [底层入口与注释](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/agent/src/agent-loop.ts#L62-L99)

## 错误发生在哪一层，恢复就在哪一层

| 情况 | 固定版本源码中的处理 | 别外推为 |
| --- | --- | --- |
| 流式模型回复以 `error` 或 `aborted` 停止 | 底层 loop 发 `turn_end` 与 `agent_end`，不执行其中的工具调用；若 `Agent` 外层捕获抛出的异常，它会合成一条错误/取消的 assistant 消息并发结束事件。[底层分支](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/agent/src/agent-loop.ts#L240-L255) · [异常兜底](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/agent/src/agent.ts#L503-L550) | 核心循环保证自动重试所有模型错误。 |
| 可重试的模型错误 | coding-agent 的 `AgentSession` 在**底层运行结束后**检查错误、重试开关与次数，等待可取消的退避；失败尝试留在原始历史，但通过 `context_edit` 从下一次模型投影中省略，再调用 `Agent.continue()`。[后运行处理](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/coding-agent/src/core/agent-session.ts#L1468-L1529) · [恢复省略](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/coding-agent/src/core/agent-session.ts#L1015-L1031) · [退避](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/coding-agent/src/core/agent-session.ts#L3375-L3419) | 所有嵌入 `pi-agent-core` 的应用都具备这套策略。 |
| 上下文溢出或可恢复的截断 | coding-agent 不把溢出归入普通瞬时错误重试；启用自动压缩时，它们进入压缩/恢复判断。溢出后“压缩并继续”的尝试有一次限制，成功完成的回复可只压缩、不重发。[错误分类](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/coding-agent/src/core/agent-session.ts#L3322-L3329) · [压缩开关及分支](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/coding-agent/src/core/agent-session.ts#L2599-L2696) | 压缩无损，或任何溢出都能救回。 |
| 用户取消 | `Agent.abort()` 发当前运行的取消信号；coding-agent 的 `abort()` 还取消重试等待、压缩等操作并等到空闲。[核心取消](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/agent/src/agent.ts#L332-L349) · [外壳取消](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/coding-agent/src/core/agent-session.ts#L2072-L2092) | 传递 `AbortSignal` 就能立刻撤销任意第三方工具的外部副作用。 |

这里的权限边界同样要谨慎：`beforeToolCall` 是一个**可选钩子**，并非内置沙箱。具体哪些动作被允许，取决于宿主如何注册工具、配置钩子及部署进程权限。[`AgentOptions`](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/agent/src/agent.ts#L113-L140) 这是由接口与调用路径得出的工程判断，不是对某个部署环境的安全审计。

## 存储、投影、模型输入是三份不同视图

coding-agent 的 `AgentSession` 在 `message_end` 把常规消息交给 `SessionManager`；会话条目带父子关系，当前分支的上下文由投影函数重建，可以应用压缩摘要与 `context_edit`。因此“原始记录还在”和“下一次会发给模型”是两个问题；而 `pi-agent-core` 的 `transformContext` / `convertToLlm` 又可在模型请求边界进一步改变消息。[消息写入](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/coding-agent/src/core/agent-session.ts#L921-L943) · [会话树](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/coding-agent/src/core/session-manager.ts#L976-L985) · [上下文投影](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/coding-agent/src/core/session-manager.ts#L543-L582) · [模型边界](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/agent/src/agent-loop.ts#L380-L406)
