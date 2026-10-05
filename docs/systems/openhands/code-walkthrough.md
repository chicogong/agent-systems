# 跟着 OpenHands SDK 走一条事件路径

[返回 OpenHands 首篇](README.md) · [固定 SDK 源码](https://github.com/OpenHands/software-agent-sdk/tree/6ebd820d10794f1b52bb06ef6c19512888a1401b)

上一页的流程是“记录动作→需要时等待批准→执行工具→记录结果”。这页从用户输入开始，沿同步 `LocalConversation.run()` 和默认 `Agent.step()` 找到这些步骤。伪代码只概括流程，具体实现见固定源码。

## 输入和动作，都先进入事件清单

`send_message()` 把用户输入变成消息事件 `MessageEvent`，交给 `_on_event`。默认会话处理先用 `ConversationState.append_event()` 加入清单，再通知外部订阅者。存储出错时，后面的通知也会停下。可选的本地显示器（visualizer）则在保存前显示内容，读显示行为时要看对应位置。[用户输入](https://github.com/OpenHands/software-agent-sdk/blob/6ebd820d10794f1b52bb06ef6c19512888a1401b/openhands-sdk/openhands/sdk/conversation/impl/local_conversation.py#L1808-L1870) · [保存和通知](https://github.com/OpenHands/software-agent-sdk/blob/6ebd820d10794f1b52bb06ef6c19512888a1401b/openhands-sdk/openhands/sdk/conversation/impl/local_conversation.py#L415-L468)

`run()` 启动循环，一轮轮调用 `agent.step()`。每步先查看当前分支有没有已经记录、但还没有对应结果的动作。找到时，先执行这些待办动作，再进入后续轮次。[运行循环](https://github.com/OpenHands/software-agent-sdk/blob/6ebd820d10794f1b52bb06ef6c19512888a1401b/openhands-sdk/openhands/sdk/conversation/impl/local_conversation.py#L1903-L2010) · [先处理待办动作](https://github.com/OpenHands/software-agent-sdk/blob/6ebd820d10794f1b52bb06ef6c19512888a1401b/openhands-sdk/openhands/sdk/agent/agent.py#L645-L661)

没有待办动作时，`Agent._step()` 从当前 `state.view` 整理消息，询问模型。模型要求调用工具后，程序先核对名称、参数和动作格式；格式无效时，发出错误事件 `AgentErrorEvent`。[准备并请求模型](https://github.com/OpenHands/software-agent-sdk/blob/6ebd820d10794f1b52bb06ef6c19512888a1401b/openhands-sdk/openhands/sdk/agent/agent.py#L677-L735) · [核对工具调用](https://github.com/OpenHands/software-agent-sdk/blob/6ebd820d10794f1b52bb06ef6c19512888a1401b/openhands-sdk/openhands/sdk/agent/agent.py#L1163-L1346)

## 需要批准时，先停下，暂不执行

有效调用先由 `_get_action_event()` 创建并发出 `ActionEvent`。随后 `_handle_tool_calls()` 检查是否需要用户确认：需要时，把会话设为 `WAITING_FOR_CONFIRMATION`，本次 `run()` 退出；无须确认时，继续执行工具。[记录动作](https://github.com/OpenHands/software-agent-sdk/blob/6ebd820d10794f1b52bb06ef6c19512888a1401b/openhands-sdk/openhands/sdk/agent/agent.py#L1348-L1382) · [检查用户确认](https://github.com/OpenHands/software-agent-sdk/blob/6ebd820d10794f1b52bb06ef6c19512888a1401b/openhands-sdk/openhands/sdk/agent/response_dispatch.py#L163-L190) · [停在等待确认](https://github.com/OpenHands/software-agent-sdk/blob/6ebd820d10794f1b52bb06ef6c19512888a1401b/openhands-sdk/openhands/sdk/conversation/impl/local_conversation.py#L2006-L2010)

这里接入 SDK 的宿主程序必须先取得批准，再调用 `run()`。这个版本的同步路径把等待后再次调用 `run()` 视为批准，会直接清掉等待状态，继续取待办动作；此处没有另查一份新的批准记录。自动把等待中的会话重新运行，会跳过宿主本应做的询问。[这一约定的注释](https://github.com/OpenHands/software-agent-sdk/blob/6ebd820d10794f1b52bb06ef6c19512888a1401b/openhands-sdk/openhands/sdk/agent/agent.py#L652-L661) · [再次运行时清除等待状态](https://github.com/OpenHands/software-agent-sdk/blob/6ebd820d10794f1b52bb06ef6c19512888a1401b/openhands-sdk/openhands/sdk/conversation/impl/local_conversation.py#L1977-L1995)

批准后再次运行，`get_unmatched_actions(active_branch())` 找出当前分支的待办动作。用户拒绝时，宿主则用 `reject_pending_actions()` 为动作生成拒绝结果 `UserRejectObservation`，工具不会执行。[继续运行](https://github.com/OpenHands/software-agent-sdk/blob/6ebd820d10794f1b52bb06ef6c19512888a1401b/openhands-sdk/openhands/sdk/conversation/impl/local_conversation.py#L1977-L1995) · [找出待办动作](https://github.com/OpenHands/software-agent-sdk/blob/6ebd820d10794f1b52bb06ef6c19512888a1401b/openhands-sdk/openhands/sdk/conversation/state.py#L677-L716) · [记录用户拒绝](https://github.com/OpenHands/software-agent-sdk/blob/6ebd820d10794f1b52bb06ef6c19512888a1401b/openhands-sdk/openhands/sdk/conversation/impl/local_conversation.py#L2610-L2648)

## 工具做完，把结果与原动作配起来

`_execute_actions()` 把动作交给工具。单次执行传入动作 `action` 和会话 `conversation`，工具返回后，Agent 通常生成 `ObservationEvent`；`ValueError` 会变成 `AgentErrorEvent`。

批次可以并行执行，结果事件按原动作次序发出。若工具修改外部文件或数据，实际修改的先后还要看工具执行过程。[执行一批动作](https://github.com/OpenHands/software-agent-sdk/blob/6ebd820d10794f1b52bb06ef6c19512888a1401b/openhands-sdk/openhands/sdk/agent/agent.py#L229-L365) · [执行并整理单个结果](https://github.com/OpenHands/software-agent-sdk/blob/6ebd820d10794f1b52bb06ef6c19512888a1401b/openhands-sdk/openhands/sdk/agent/agent.py#L1384-L1446)

```text
LocalConversation.run() → Agent.step()
  没有待办动作：模型请求工具 → ActionEvent 记入清单 → 检查确认条件
    无需确认：Tool(action, conversation) → ObservationEvent / AgentErrorEvent
    需要确认：WAITING_FOR_CONFIRMATION → 本次 run 停止
      宿主取得批准后再次 run：取出待办动作并执行
      用户拒绝：UserRejectObservation，不执行工具
```

## 还有哪些情况会停下

暂停、卡住、达到预算或最大轮数时，`run()` 也会停下。异常使状态变为 `ERROR`，并生成会话错误事件 `ConversationErrorEvent`。标为 `FINISHED`（已结束）后，结束钩子还可以给出反馈，让状态回到 `RUNNING` 继续工作。[查看停止条件](https://github.com/OpenHands/software-agent-sdk/blob/6ebd820d10794f1b52bb06ef6c19512888a1401b/openhands-sdk/openhands/sdk/conversation/impl/local_conversation.py#L1933-L2059)

阅读一次工作记录时，先看结束原因，再看工具结果，最后核对实际产物。本篇尚未运行确认和崩溃恢复测试；外部动作是否会重复，以及实际执行环境如何隔离，需要另外检查。远程 Agent Server、ACP 接入和异步 `arun()` 采用的流程也要分别阅读。
