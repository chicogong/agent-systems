# 跟着 OpenHands SDK 走完一条事件闭环

[返回 OpenHands 首篇](README.md) · [固定 SDK 源码](https://github.com/OpenHands/software-agent-sdk/tree/6ebd820d10794f1b52bb06ef6c19512888a1401b)

如果在接入 OpenHands SDK 时，外层服务看到 `run()` 返回就顺手再调一次 `run()`，会发生什么？答案是：原本停下来等待人工审批的高危工具调用，会被立刻放行执行。

为什么会这样？顺着同步 `LocalConversation.run()` 与默认 `Agent.step()` 的真实调用链走一遍，就能看清事件入账、确认挂起、批次执行与异常收尾的每一处咬合细节。

```text
send_message() → MessageEvent → _on_event() [先 append_event 落账，再广播订阅者]
LocalConversation.run() 循环调用 Agent.step()
  ├─ 分支 A：当前分支存在未配对 ActionEvent → 直接 _execute_actions() 清偿待办
  └─ 分支 B：无待办动作 → Agent._step() 从 state.view 构造消息请求模型
       ├─ 工具名或参数格式非法 → 发出 AgentErrorEvent（通过 tool_call_id 配对）
       └─ 校验通过 → _get_action_event() 发出 ActionEvent
            ├─ 需要确认 → 状态设为 WAITING_FOR_CONFIRMATION，本次 run() 立即退出
            │    ├─ 宿主获批后再次调用 run() → 清除等待状态，下一轮走分支 A 执行动作
            │    └─ 宿主调用 reject_pending_actions() → 发出 UserRejectObservation（通过 action_id 配对），跳过执行
            └─ 无需确认 → _execute_actions() 调工具（在 FinishTool 处截断批次后并行执行） → 按原动作顺序发出 ObservationEvent（通过 action_id 配对） / AgentErrorEvent
```

## 1. 事件入账：为什么先写存储、再发通知

用户输入通过 `send_message()` 包装成 `MessageEvent` 送入 `_on_event()`。默认的会话回调严守「**先持久化，后广播**」：先调用 `ConversationState.append_event()` 写入事件流，再依次触发外部订阅者。这样一旦底层存储写盘报错，流程当场中断，外部监听者不会拿到未落账的脏状态。

源码里有一处排查显示问题时容易忽略的例外：如果配置了本地可视化器（`visualizer`），它会在 `append_event()` **之前**先行渲染输出，阅读终端回显顺序时要留意这一先后差异。[用户输入](https://github.com/OpenHands/software-agent-sdk/blob/6ebd820d10794f1b52bb06ef6c19512888a1401b/openhands-sdk/openhands/sdk/conversation/impl/local_conversation.py#L1808-L1870) · [保存和通知](https://github.com/OpenHands/software-agent-sdk/blob/6ebd820d10794f1b52bb06ef6c19512888a1401b/openhands-sdk/openhands/sdk/conversation/impl/local_conversation.py#L415-L468)

## 2. 步进入口：先清偿历史欠账，再请求模型

`LocalConversation.run()` 启动主循环后，每轮调用一次 `agent.step()`。`step()` 并不会一上来就调大模型，而是先检查当前活动分支里有没有「已记下 `ActionEvent`、却还没有配对结果」的悬空动作：

- **有未配对动作**：说明上一轮在确认门禁或中断处停了下来，本轮必须先把这批待办动作执行完，补齐对应的观察事件，才允许推进后续轮次。[运行循环](https://github.com/OpenHands/software-agent-sdk/blob/6ebd820d10794f1b52bb06ef6c19512888a1401b/openhands-sdk/openhands/sdk/conversation/impl/local_conversation.py#L1903-L2010) · [先处理待办动作](https://github.com/OpenHands/software-agent-sdk/blob/6ebd820d10794f1b52bb06ef6c19512888a1401b/openhands-sdk/openhands/sdk/agent/agent.py#L645-L661)
- **没有待办动作**：进入 `Agent._step()`，从 `state.view` 把事件流投影成模型消息列表并发起推理。模型返回工具调用后，程序先核对工具是否注册、JSON 参数能否反序列化为目标动作类型；一旦格式非法，不抛未捕获异常炸毁循环，而是原地生成 `AgentErrorEvent` 回填给下一轮模型自纠。[准备并请求模型](https://github.com/OpenHands/software-agent-sdk/blob/6ebd820d10794f1b52bb06ef6c19512888a1401b/openhands-sdk/openhands/sdk/agent/agent.py#L677-L735) · [核对工具调用](https://github.com/OpenHands/software-agent-sdk/blob/6ebd820d10794f1b52bb06ef6c19512888a1401b/openhands-sdk/openhands/sdk/agent/agent.py#L1163-L1346)

## 3. 确认门禁：挂起靠状态退出，批准靠宿主守门

通过校验的工具调用先经 `_get_action_event()` 构造并发出 `ActionEvent`。紧接着 `_handle_tool_calls()` 询问安全与确认策略：一旦需要人工确认，就把会话执行状态切换为 `WAITING_FOR_CONFIRMATION`，外层 `run()` 检测到该状态后立刻跳出循环，工具一行代码也不会执行。[记录动作](https://github.com/OpenHands/software-agent-sdk/blob/6ebd820d10794f1b52bb06ef6c19512888a1401b/openhands-sdk/openhands/sdk/agent/agent.py#L1348-L1382) · [检查用户确认](https://github.com/OpenHands/software-agent-sdk/blob/6ebd820d10794f1b52bb06ef6c19512888a1401b/openhands-sdk/openhands/sdk/agent/response_dispatch.py#L163-L190) · [停在等待确认](https://github.com/OpenHands/software-agent-sdk/blob/6ebd820d10794f1b52bb06ef6c19512888a1401b/openhands-sdk/openhands/sdk/conversation/impl/local_conversation.py#L2006-L2010)

这就解释了开头的陷阱：在同步路径的设计里，SDK 没有另外发明一张「批准票据事件」，而是直接约定**处于 `WAITING_FOR_CONFIRMATION` 时再次调用 `run()` 即代表宿主已拿到用户批准**。`run()` 入口会把等待状态改回运行态，随后 `get_unmatched_actions(active_branch())` 捞出刚才挂起的 `ActionEvent` 投入执行；反之，如果用户拒绝，宿主必须调用 `reject_pending_actions()`，为每个待办动作补上一条 `UserRejectObservation`，把悬空的动作账目平掉。[这一约定的注释](https://github.com/OpenHands/software-agent-sdk/blob/6ebd820d10794f1b52bb06ef6c19512888a1401b/openhands-sdk/openhands/sdk/agent/agent.py#L652-L661) · [继续运行](https://github.com/OpenHands/software-agent-sdk/blob/6ebd820d10794f1b52bb06ef6c19512888a1401b/openhands-sdk/openhands/sdk/conversation/impl/local_conversation.py#L1977-L1995) · [找出待办动作](https://github.com/OpenHands/software-agent-sdk/blob/6ebd820d10794f1b52bb06ef6c19512888a1401b/openhands-sdk/openhands/sdk/conversation/state.py#L677-L716) · [记录用户拒绝](https://github.com/OpenHands/software-agent-sdk/blob/6ebd820d10794f1b52bb06ef6c19512888a1401b/openhands-sdk/openhands/sdk/conversation/impl/local_conversation.py#L2610-L2648)

## 4. 批次执行与循环终止：事件保序，副作用未必保序

进入 `_execute_actions()` 后，每个动作连同当前 `conversation` 上下文交给对应工具执行。正常返回的 `Observation` 被包装为 `ObservationEvent`（通过 `action_id` 与原动作配对）；若执行期抛出 `ValueError`，则捕获并转为 `AgentErrorEvent`（通过 `tool_call_id` 与模型调用配对）。

在将批次动作投入并发执行池之前，OpenHands 会先对动作列表进行**截断处理**：如果模型在一次响应中返回了多个工具调用，且其中包含了结束任务的 `FinishTool`，执行器会在 `FinishTool` 处立即截断批次，直接忽略排在 `FinishTool` 之后的任何多余工具调用，然后再把保留下来的动作派发给底层并发执行。当模型一次提出多个可并行工具调用时，SDK 允许并发执行工具，但在**写回结果事件时严格按原 `ActionEvent` 的顺序依次发出**。这样事件流与模型上下文的因果配对永远整洁有序；但排查问题时要注意，如果两个并发工具同时读写外部磁盘文件，真实文件系统的修改先后仍取决于操作系统调度。[执行一批动作](https://github.com/OpenHands/software-agent-sdk/blob/6ebd820d10794f1b52bb06ef6c19512888a1401b/openhands-sdk/openhands/sdk/agent/agent.py#L229-L365) · [执行并整理单个结果](https://github.com/OpenHands/software-agent-sdk/blob/6ebd820d10794f1b52bb06ef6c19512888a1401b/openhands-sdk/openhands/sdk/agent/agent.py#L1384-L1446)

除等待确认外，`run()` 还会在每轮边界检查其余停止条件：外部请求暂停、死循环卡住检测（stuck）、触达费用预算或最大轮数上限都会让循环停下；未预期异常会将状态置为 `ERROR` 并记录 `ConversationErrorEvent`。有意思的是，即便 Agent 自己宣布 `FINISHED`，结束钩子（stop hook）仍有机会做最后验收——如果验收未过并注入新反馈，会话状态会被拉回 `RUNNING` 继续下一轮修复。[查看停止条件](https://github.com/OpenHands/software-agent-sdk/blob/6ebd820d10794f1b52bb06ef6c19512888a1401b/openhands-sdk/openhands/sdk/conversation/impl/local_conversation.py#L1933-L2059)

## 来源与边界

本篇导读依据 [`OpenHands/software-agent-sdk@6ebd820d10794f1b52bb06ef6c19512888a1401b`](https://github.com/OpenHands/software-agent-sdk/tree/6ebd820d10794f1b52bb06ef6c19512888a1401b) 静态核对同步 `LocalConversation.run()` 与 `Agent.step()` 路径。异步 `arun()`、远程 Agent Server、ACP 协议接入以及外部工具在进程崩溃后的重试幂等性，不在本篇覆盖范围内。
