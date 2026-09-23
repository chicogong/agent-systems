# 跟着 Pi 代码走一轮

[返回 Pi 首页](README.md) · 固定源码版本 [`898ab804`](https://github.com/earendil-works/pi/tree/898ab804050730e9dcefb4443875d5a932aa6a32)

以下是便于阅读的**逻辑摘要**，不是原项目源码复制，也不覆盖所有 provider、异常和插件分支。

1. `Agent.prompt()` 准备用户消息并进入 `runAgentLoop`。[入口](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/agent/src/agent.ts#L367-L442)
2. `runLoop` 启动回合。它有处理模型与工具的内层循环，也有在自然结束点检查 follow-up 的外层循环；因此“模型只回复一次”和“本次 Agent 运行结束”不是同一概念。[循环](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/agent/src/agent-loop.ts#L162-L320)
3. 每次请求模型前，可变换 Agent 内部上下文，再通过 `convertToLlm` 形成模型可理解的消息，交由流式接口处理。[请求准备](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/agent/src/agent-loop.ts#L380-L406)
4. 对工具调用，先定位工具、处理并校验参数，运行 `beforeToolCall`；获准后执行工具并处理进度，最后经过 `afterToolCall` 得到 tool result。[前置处理](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/agent/src/agent-loop.ts#L703-L771) · [执行与后置](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/agent/src/agent-loop.ts#L773-L860)
5. 默认批次可并行执行；全局设置或其中一个工具要求顺序模式时，整批顺序执行。输出长度截断的工具调用不会拿不完整参数去执行，而会形成失败结果。[执行模式](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/agent/src/agent-loop.ts#L505-L520) · [截断处理](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/agent/src/agent-loop.ts#L475-L499)
6. `steer()` 和 `followUp()` 进入两条内存队列，不是磁盘记忆。steering 在回合间取出；follow-up 在本次运行原本准备结束时取出。[队列](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/agent/src/agent.ts#L142-L173) · [调度](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/agent/src/agent-loop.ts#L294-L306)
7. coding-agent 的 `AgentSession` 订阅事件，在 `message_end` 把消息追加到 `SessionManager`；后者维护 JSONL 会话树并投影当前分支给模型上下文。这是 coding-agent 的实现，不是 agent-core 的普遍存储合同。[写入](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/coding-agent/src/core/agent-session.ts#L921-L943) · [会话树](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/coding-agent/src/core/session-manager.ts#L977-L985) · [上下文投影](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/coding-agent/src/core/session-manager.ts#L543-L582)

把其中最关键的控制关系压缩成伪代码：

```text
prompt(input) → runLoop
  每次模型请求前：transformContext → convertToLlm → streamFn
  若有完整的 toolCall：校验/前置拦截 → execute → 后置处理 → toolResult
  回合间：检查 steering；本来要结束时：检查 follow-up
  coding-agent 收到 message_end → SessionManager 记录/投影当前分支
```

这里的箭头表示阅读顺序，不是逐行调用栈；尤其最后一行属于应用层的事件订阅，不在 `runLoop` 内部。

这里的“追加”描述常规消息路径，不应推断文件永远只追加：`SessionManager` 还存在[重写文件路径](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/coding-agent/src/core/session-manager.ts#L1124-L1134)。尚未运行故障注入测试，因此不声称恢复或持久化行为在所有边界条件下已验证。
