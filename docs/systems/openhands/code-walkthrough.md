# 跟着 OpenHands SDK 走一条事件路径

[返回 OpenHands 首篇](README.md) · [固定 SDK 源码](https://github.com/OpenHands/software-agent-sdk/tree/6ebd820d10794f1b52bb06ef6c19512888a1401b)

这是帮助阅读的控制流摘要，不是项目源码复制。范围限定于同步 `LocalConversation.run()` 调默认 `Agent.step()`；`arun()`、ACP 代理和 Agent Server 路径需另行核对。

1. `send_message()` 把用户输入变成 `MessageEvent`，送进 `_on_event`。`LocalConversation` 的回调链以 `ConversationState.append_event()` 为存储关口，外部订阅回调在其后；若存储失败，后续订阅回调不会被调用。可选的本地 visualizer 则在存储前显示，不能与外部订阅混为一谈。[输入事件](https://github.com/OpenHands/software-agent-sdk/blob/6ebd820d10794f1b52bb06ef6c19512888a1401b/openhands-sdk/openhands/sdk/conversation/impl/local_conversation.py#L1808-L1870) · [回调链](https://github.com/OpenHands/software-agent-sdk/blob/6ebd820d10794f1b52bb06ef6c19512888a1401b/openhands-sdk/openhands/sdk/conversation/impl/local_conversation.py#L415-L468)
2. `run()` 设置运行态，在循环里调用 `agent.step()`；`step()` 先检查当前分支上的未匹配 `ActionEvent`。若有，先执行它们并返回，不会在这一步先调用 LLM。[run 循环](https://github.com/OpenHands/software-agent-sdk/blob/6ebd820d10794f1b52bb06ef6c19512888a1401b/openhands-sdk/openhands/sdk/conversation/impl/local_conversation.py#L1903-L2010) · [未匹配动作优先](https://github.com/OpenHands/software-agent-sdk/blob/6ebd820d10794f1b52bb06ef6c19512888a1401b/openhands-sdk/openhands/sdk/agent/agent.py#L645-L661)
3. 若没有待处理动作，`Agent._step()` 从当前 `state.view` 准备模型输入、调用 LLM，并按返回类型分发。工具调用先进行名称、参数和 `Action` 校验；不合法调用发 `AgentErrorEvent`，不进入普通工具执行路径。[模型请求](https://github.com/OpenHands/software-agent-sdk/blob/6ebd820d10794f1b52bb06ef6c19512888a1401b/openhands-sdk/openhands/sdk/agent/agent.py#L677-L735) · [工具校验与错误](https://github.com/OpenHands/software-agent-sdk/blob/6ebd820d10794f1b52bb06ef6c19512888a1401b/openhands-sdk/openhands/sdk/agent/agent.py#L1163-L1346)
4. `_get_action_event()` 创建并发出 `ActionEvent`；`ResponseDispatchMixin._handle_tool_calls()` 之后才调用 `_requires_user_confirmation()`。确认策略命中时状态变为 `WAITING_FOR_CONFIRMATION`，`run()` 在当前 step 后退出；无须确认才当场执行。[ActionEvent 先发](https://github.com/OpenHands/software-agent-sdk/blob/6ebd820d10794f1b52bb06ef6c19512888a1401b/openhands-sdk/openhands/sdk/agent/agent.py#L1348-L1382) · [确认与执行顺序](https://github.com/OpenHands/software-agent-sdk/blob/6ebd820d10794f1b52bb06ef6c19512888a1401b/openhands-sdk/openhands/sdk/agent/response_dispatch.py#L163-L190) · [run 停在确认](https://github.com/OpenHands/software-agent-sdk/blob/6ebd820d10794f1b52bb06ef6c19512888a1401b/openhands-sdk/openhands/sdk/conversation/impl/local_conversation.py#L2006-L2010)
5. 获准后再次 `run()`，它清掉 waiting 状态；`Agent._step()` 通过 `get_unmatched_actions(active_branch())` 找回动作，执行它们。若用户拒绝，则 `reject_pending_actions()` 发 `UserRejectObservation` 配对，而不调用工具。[再运行](https://github.com/OpenHands/software-agent-sdk/blob/6ebd820d10794f1b52bb06ef6c19512888a1401b/openhands-sdk/openhands/sdk/conversation/impl/local_conversation.py#L1977-L1995) · [匹配算法](https://github.com/OpenHands/software-agent-sdk/blob/6ebd820d10794f1b52bb06ef6c19512888a1401b/openhands-sdk/openhands/sdk/conversation/state.py#L677-L716) · [拒绝动作](https://github.com/OpenHands/software-agent-sdk/blob/6ebd820d10794f1b52bb06ef6c19512888a1401b/openhands-sdk/openhands/sdk/conversation/impl/local_conversation.py#L2610-L2648)
6. `_execute_actions()` 准备批次，委托工具执行，并按原动作顺序发结果事件。单个工具调用传入 `action` 与 `conversation`；通常形成 `ObservationEvent`，`ValueError` 转为 `AgentErrorEvent`。并发批次的实际副作用发生顺序不能仅凭结果事件顺序推断。[批次执行与事件发出](https://github.com/OpenHands/software-agent-sdk/blob/6ebd820d10794f1b52bb06ef6c19512888a1401b/openhands-sdk/openhands/sdk/agent/agent.py#L229-L365) · [调用工具并封装观察](https://github.com/OpenHands/software-agent-sdk/blob/6ebd820d10794f1b52bb06ef6c19512888a1401b/openhands-sdk/openhands/sdk/agent/agent.py#L1384-L1446)

```text
LocalConversation.run() → Agent.step()
  无待处理动作：LLM 工具调用 → ActionEvent 入事件历史 → 确认闸门
    无需确认：Tool(action, conversation) → ObservationEvent / AgentErrorEvent
    需要确认：WAITING_FOR_CONFIRMATION → 本次 run 停止
      再次获准 run：取未匹配动作并执行
      用户拒绝：UserRejectObservation，不执行工具
```

### 停止与未知

`run()` 还会因暂停、卡住、预算或最大迭代数停下，异常会转为 `ERROR` 与 `ConversationErrorEvent`；`FINISHED` 还可能被 stop hook 反馈改回 `RUNNING`。这些是外围循环的停止条件，不应误认为工具调用必然成功。[停止检查](https://github.com/OpenHands/software-agent-sdk/blob/6ebd820d10794f1b52bb06ef6c19512888a1401b/openhands-sdk/openhands/sdk/conversation/impl/local_conversation.py#L1933-L2059)

本篇没有运行确认、崩溃恢复或故障注入测试，因此不宣称 Action/Observation 配对可防止重复副作用；更不宣称具体 workspace 或 Terminal 后端具备沙箱隔离。远程 Agent Server、ACP 后端、异步 `arun()` 与复杂 hook 顺序留待独立章节。
