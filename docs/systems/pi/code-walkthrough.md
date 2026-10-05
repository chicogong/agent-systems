# 跟着 Pi 代码走一轮

[返回 Pi 首页](README.md) · 固定源码版本 [`898ab804`](https://github.com/earendil-works/pi/tree/898ab804050730e9dcefb4443875d5a932aa6a32)

继续用“读取文件，再根据内容工作”这个任务看代码。主线很简单：Pi 接收任务，准备模型输入，执行模型要求的工具，再把工具结果交给下一轮。下面按这条主线找到对应函数。

本文依据固定版本的静态源码；伪代码只是便于阅读的摘要，尚未运行验证。

## 1. 接收任务，整理要给模型的消息

`Agent.prompt()` 把输入准备成用户消息，交给 `runAgentLoop`。已有任务正在运行时，第二个 `prompt()` 会被拒绝；新输入应放进队列，或等当前任务结束。[任务入口](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/agent/src/agent.ts#L367-L442)

`runLoop` 负责一轮轮工作。模型回复中有工具调用时，程序还要执行工具、送回结果，所以一项任务可能请求模型多次。循环准备收尾时，还会查看是否有用户排队的后续输入。[循环安排](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/agent/src/agent-loop.ts#L162-L320)

每次联系模型前，先运行已配置的 `prepareRequest`，再用 `transformContext` 调整当前消息，用 `convertToLlm` 转成模型接口接受的格式。流式接口会逐步接收模型输出。[准备这一轮](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/agent/src/agent-loop.ts#L181-L241) · [组成模型输入](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/agent/src/agent-loop.ts#L380-L406)

## 2. 检查工具调用，再执行并交回结果

程序先找到模型要求的工具，核对参数，再运行已配置的前置钩子 `beforeToolCall`。钩子是允许应用插入处理逻辑的函数；这个钩子可以拦下调用。通过后，才执行工具并运行后置钩子 `afterToolCall`。工具找不到、参数不对或被拦下时，程序直接生成错误结果，跳过执行和后置钩子。[执行前的检查](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/agent/src/agent-loop.ts#L703-L771) · [执行与结果处理](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/agent/src/agent-loop.ts#L773-L861)

这些钩子由宿主应用选择配置。应用注册了哪些工具、设置了哪些检查，以及进程能访问哪些资源，共同决定实际权限；Pi 核心没有因此自动获得沙箱隔离。[可配置的 AgentOptions](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/agent/src/agent.ts#L113-L140)

模型一次要求多个工具时，默认可以并行执行。全局配置或其中一个工具要求顺序执行时，整批会改为顺序执行。并行路径等待结果后，仍按原调用次序写入。两个工具同时改同一文件时，实际修改仍可能冲突。[默认模式](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/agent/src/agent.ts#L244-L250) · [选择执行模式](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/agent/src/agent-loop.ts#L505-L520) · [收集并行结果](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/agent/src/agent-loop.ts#L583-L657)

如果模型输出因长度限制被截断，工具参数可能还没生成完整。程序会给整批调用生成失败结果，留给后续处理。[输出截断处理](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/agent/src/agent-loop.ts#L475-L499)

## 3. 把途中补充的话放进合适的一轮

`steer()` 把调整方向的输入放进 steering 队列，在首次模型请求前和回合之间处理。`followUp()` 把后续输入放进另一个队列，等本次运行准备结束时处理。两条队列都存在当前进程内存里。[放入队列](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/agent/src/agent.ts#L142-L173) · [取出 steering](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/agent/src/agent-loop.ts#L174-L215) · [取出 follow-up](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/agent/src/agent-loop.ts#L279-L320)

终端 coding-agent 还会保存会话：`AgentSession` 收到消息结束事件 `message_end` 后，把常规消息交给 `SessionManager`。它把带有父子关系的消息组织成会话树，可保存为 JSONL 文件，再挑出当前分支的内容给模型。[交给会话管理器](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/coding-agent/src/core/agent-session.ts#L921-L943) · [会话树](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/coding-agent/src/core/session-manager.ts#L976-L1005) · [整理当前分支](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/coding-agent/src/core/session-manager.ts#L543-L582)

把主线放在一起看：

```text
prompt(input) → runLoop
  每次模型请求前：transformContext → convertToLlm → streamFn
  若有完整工具调用：核对参数/前置检查 → [通过后 execute/后置处理] → 工具结果
  回合间：检查 steering；本来要结束时：检查 follow-up
  coding-agent 收到 message_end → SessionManager 保存消息/整理当前分支
```

箭头帮助你跟读流程。最后一行由终端应用订阅事件完成，位于 `runLoop` 外部。常规消息会追加到会话记录，其他处理也可能[重写会话文件](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/coding-agent/src/core/session-manager.ts#L1124-L1134)。

## 4. 继续还是结束，由哪些条件决定

工具抛出的异常会变成带 `isError` 的结果消息，让模型知道哪里出了问题，再决定下一步。后置钩子可以调整结果；它抛错时也会生成错误结果。模型接下来是否重试，要看后续决策。非空批次中，所有已完成调用的结果都带 `terminate: true` 时，批次才要求结束。[处理工具错误](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/agent/src/agent-loop.ts#L773-L814) · [处理后置钩子](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/agent/src/agent-loop.ts#L816-L861) · [整批结束条件](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/agent/src/agent-loop.ts#L685-L687)

应用还可以用 `finishTurn` 决定收尾：返回 `end` 时立即发结束事件 `agent_end`，跳过后续 follow-up 检查；返回 `continue` 时，如果工具结果和排队消息都没有带来下一轮，就再用已有消息请求一次模型。准备下一轮花了时间时，程序也会补查此前没有取到的 steering 输入。[回合收尾](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/agent/src/agent-loop.ts#L279-L320) · [准备之后再看新输入](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/agent/src/agent-loop.ts#L181-L207)

重新调用 `continue()` 也需要合适的消息。最后一条是模型回复时，它先取 steering，再取 follow-up；没有新输入就报错。底层普通继续入口要求已有消息，并拒绝直接以模型回复作为末尾。送到模型接口时，转换后的最后一条还应是用户输入或工具结果；这个格式要求由转换后的消息决定。[Agent.continue()](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/agent/src/agent.ts#L380-L408) · [底层继续入口](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/agent/src/agent-loop.ts#L62-L99)

## 5. 模型报错、消息太长或用户取消

模型回复以 `error` 或 `aborted`（报错或取消）结束时，底层循环发出本轮和整次运行的结束事件，并跳过回复中的工具调用。异常抛到 `Agent` 外层时，它会生成说明错误或取消的模型消息，再发结束事件。[底层处理](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/agent/src/agent-loop.ts#L240-L255) · [外层异常处理](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/agent/src/agent.ts#L503-L550)

终端应用可以在底层运行结束后重试部分模型错误。`AgentSession` 检查错误类型、重试开关和次数，等待一段时间后再继续。失败尝试仍保存在原始历史中，但用 `context_edit` 标记，下一次送给模型的消息会省略它。[选择是否重试](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/coding-agent/src/core/agent-session.ts#L1468-L1529) · [整理重试消息](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/coding-agent/src/core/agent-session.ts#L1015-L1031) · [等待后再试](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/coding-agent/src/core/agent-session.ts#L3375-L3419)

消息超出模型可接收的大小，叫“上下文溢出”。终端应用把它交给另一套压缩恢复流程：启用自动压缩时，判断能否先缩短消息再继续；溢出后的这种重试最多一次。某些回复已成功完成时，只做压缩，为后续工作腾出空间。[区分错误类型](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/coding-agent/src/core/agent-session.ts#L3322-L3329) · [压缩与继续](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/coding-agent/src/core/agent-session.ts#L2599-L2696)

用户取消时，`Agent.abort()` 发出取消信号；终端应用的 `abort()` 还会停止重试等待、压缩等操作，并等当前工作转为空闲。已经改过的文件或已发出的网络请求，仍需单独检查结果，取消信号不会自动把它们还原。[核心取消](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/agent/src/agent.ts#L332-L349) · [终端应用取消](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/coding-agent/src/core/agent-session.ts#L2072-L2092)

## 6. 保存了什么，与下一轮看什么

终端应用先保存常规消息，接着根据当前会话分支整理模型输入。整理时可以使用压缩摘要，也可以按 `context_edit` 省略一些旧消息。这个从完整记录整理当前输入的过程，在代码里叫“投影”。模型请求前，`transformContext` 和 `convertToLlm` 还可以继续调整消息。

所以，查一段旧内容时，可以顺着三个地方读：完整会话记录、当前分支整理出的消息、最终交给模型的消息。某条记录保留在历史里，下一轮也可能已经省略它。[保存消息](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/coding-agent/src/core/agent-session.ts#L921-L943) · [会话父子关系](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/coding-agent/src/core/session-manager.ts#L976-L985) · [整理当前分支](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/coding-agent/src/core/session-manager.ts#L543-L582) · [最终模型消息](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/agent/src/agent-loop.ts#L380-L406)

这些会话保存、压缩和重试策略属于 coding-agent 应用。只接入 `pi-agent-core` 的程序，需要自行选择相应策略；实际持久化、恢复效果和不同模型服务的行为仍待运行验证。
