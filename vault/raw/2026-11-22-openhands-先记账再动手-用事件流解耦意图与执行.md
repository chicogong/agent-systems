---
title: "OpenHands：先记账再动手，用事件流解耦意图与执行"
origin: "/Users/haorangong/Github/chicogong/experiments/agent-systems/docs/systems/openhands/README.md"
sha256: "149d749b87d1a79d6c2120a5b40657ea349a0d715f33144591fe74dd66aa9772"
ingested_at: "2026-11-22T13:54:22.964Z"
tags: []
---

# OpenHands：先记账再动手，用事件流解耦意图与执行

# OpenHands：先记账再动手，用事件流解耦意图与执行

[返回系统目录](../README.md) · [跟读代码](code-walkthrough.md) · [图的文字版](../../../figures/openhands-action-events/README.md)

写一个 50 行的玩具 Agent 很容易：拿到模型的 `tool_call`，直接调函数改文件或跑命令，再把返回值塞回 `messages`。一旦进入真实工程，这种「函数直连循环」立刻会撞上三堵墙：

1. **人工审批会卡死调用栈**：模型准备执行 `rm -rf dist/` 或修改线上配置，必须等用户点「批准」。你不能让后台线程干等二十分钟；可如果直接退出函数，下次恢复时怎么知道模型刚才打算执行哪条命令、参数是什么？
2. **中断与拒绝会留下半截账本**：要是用户点了「拒绝」，或者工具参数校验失败，没有配对结果的 `tool_call` 留在上下文里，下一轮请求模型接口就会直接报错。
3. **多端观测与执行耦合**：界面渲染、审计日志、持久化存储都需要同时知道「Agent 打算做什么」和「实际做出了什么」，硬塞进同一个循环只会变成胶水代码泥潭。

OpenHands（核心引擎位于独立拆出的 `software-agent-sdk`）借用了数据库预写日志（WAL）的思路，把整个循环改造成一条**只追加的事件流**（Action / Observation Event Stream）：模型意图、环境执行与会话记录不再互相直接调用，而是全部通过标准事件总线对账。

## 核心机制：把「打算做」和「做完结果」拆成配对事件

在 OpenHands SDK 里，模型的每一次工具调用不会立刻触发外部副作用，而是严格走完「**预写意图 → 审批门禁 → 执行工具 → 回填观察**」四步：

1. **先记录动作意图**：模型输出工具调用后，Agent 先校验工具名与参数结构，把「准备执行的动作」封装成 `ActionEvent` 追加进会话事件流。
2. **审批挂起零线程阻塞**：如果确认策略判定该动作需要人工确认，管理会话的 `LocalConversation` 直接把状态切到 `WAITING_FOR_CONFIRMATION`，当前 `run()` 干净退出。因为待执行的 `ActionEvent` 已经躺在事件流里，系统不需要挂起任何协程或线程。
3. **重入时优先清偿未配对动作**：宿主拿到用户批准后再次调用 `run()`，`Agent.step()` 第一件事不是请求模型，而是扫描当前分支上「还没有结果配对」的 `ActionEvent`，先把它们执行完，再去问模型下一步。
4. **用 ID 闭合每一笔动作**：工具正常返回生成 `ObservationEvent`，参数或运行报错生成 `AgentErrorEvent`，用户拒绝则生成 `UserRejectObservation`——三者都通过动作编号与原 `ActionEvent` 精确配对。

源码入口：[创建动作记录](https://github.com/OpenHands/software-agent-sdk/blob/6ebd820d10794f1b52bb06ef6c19512888a1401b/openhands-sdk/openhands/sdk/agent/agent.py#L1227-L1382) · [检查确认条件](https://github.com/OpenHands/software-agent-sdk/blob/6ebd820d10794f1b52bb06ef6c19512888a1401b/openhands-sdk/openhands/sdk/agent/response_dispatch.py#L163-L190) · [先处理待办动作](https://github.com/OpenHands/software-agent-sdk/blob/6ebd820d10794f1b52bb06ef6c19512888a1401b/openhands-sdk/openhands/sdk/agent/agent.py#L645-L661)

![OpenHands ActionEvent 与 ObservationEvent 的泳道时序图](../../../figures/openhands-action-events/diagram.svg)

[可编辑图源](../../../figures/openhands-action-events/scene.excalidraw) · [PNG 预览](../../../figures/openhands-action-events/preview.png) · [不看图的说明](../../../figures/openhands-action-events/README.md)

从数据视角看，一次历经「挂起等待确认 → 用户批准执行」的会话，事件流里落下的记录就像复式记账本：

```json
[
  { "idx": 1, "type": "MessageEvent",     "source": "user",  "content": "清理构建产物并跑单测" },
  { "idx": 2, "type": "ActionEvent",      "id": "act_01",    "tool": "terminal", "cmd": "rm -rf build && pytest" },
  // ↑ 命中确认策略：会话状态置为 WAITING_FOR_CONFIRMATION，本次 run() 在执行前直接返回
  // ↓ 宿主获得用户批准后再次调用 run()，扫描出未配对的 act_01 并执行（若拒绝则写入 UserRejectObservation）
  { "idx": 3, "type": "ObservationEvent", "action_id": "act_01", "exit_code": 0, "output": "12 passed in 1.4s" }
]
```

## 架构取舍：事件总线的红利与代价

把状态收敛到单一事件清单，给宿主程序带来了极高的可解释性与解耦度，但也引入了明确的工程边界：

- **先落账、后广播的一致性顺序**：`LocalConversation` 收到新事件时，默认先调用 `append_event()` 写入状态存储，成功后再通知外部订阅者，避免订阅者看到「未入账的幽灵事件」。至于事件是否真正落盘，取决于初始化配置——未指定持久化目录时，会退化为内存态的 `InMemoryFileStore`。[保存与通知顺序](https://github.com/OpenHands/software-agent-sdk/blob/6ebd820d10794f1b52bb06ef6c19512888a1401b/openhands-sdk/openhands/sdk/conversation/impl/local_conversation.py#L415-L468) · [按编号找待办动作](https://github.com/OpenHands/software-agent-sdk/blob/6ebd820d10794f1b52bb06ef6c19512888a1401b/openhands-sdk/openhands/sdk/conversation/state.py#L677-L716) · [存储选择](https://github.com/OpenHands/software-agent-sdk/blob/6ebd820d10794f1b52bb06ef6c19512888a1401b/openhands-sdk/openhands/sdk/conversation/state.py#L506-L541)
- **同步重入的隐式批准契约**：在这条同步 `LocalConversation.run()` 路径上，会话处于 `WAITING_FOR_CONFIRMATION` 时**再次调用 `run()` 本身就被视作已获批准**，程序会直接清除等待标记并执行待办动作。这意味着接入 SDK 的外层宿主绝不能给 `run()` 套无脑自动重试循环，否则等于直接绕过人工确认。
- **事件解耦不等于执行沙箱**：事件流只管「记账与调度」，不管「隔离爆炸半径」。例如 `TerminalTool` 从 `conv_state.workspace.working_dir` 读取初始工作目录，但这仅仅是命令行的起始路径，挡不住 `cd ..` 或访问宿主机网络；真正的文件与网络边界完全取决于 `workspace` 挂接的是容器沙箱还是无隔离的本地模式。[TerminalTool 初始化](https://github.com/OpenHands/software-agent-sdk/blob/6ebd820d10794f1b52bb06ef6c19512888a1401b/openhands-tools/openhands/tools/terminal/definition.py#L294-L330) · [本地模式提醒](https://github.com/OpenHands/OpenHands/blob/928873b4c2efb5a17ffa93eb541c78bb43a109f3/README.md#L63-L66)

## 双仓分工：读源码别进错门

翻阅新版 OpenHands 时，首先要分清两个官方仓库的职责切分：主仓 `OpenHands/OpenHands` 现在聚焦于 Agent Canvas 交互界面与本地应用服务编排；而真正的 Agent 循环、工具定义、会话状态机（`ConversationState`）、工作空间（`workspace`）与事件模型全部沉淀在独立的 `OpenHands/software-agent-sdk` 中。[官方仓库分工](https://github.com/OpenHands/OpenHands/blob/928873b4c2efb5a17ffa93eb541c78bb43a109f3/README.md#L140-L150)

想顺着调用栈看清 `ActionEvent` 怎么入账、挂起后怎么恢复、并行批次怎么保序回填，请继续阅读下一篇[代码导读](code-walkthrough.md)。

## 来源与边界

本篇的 Agent 核心实现依据官方固定提交 [`OpenHands/software-agent-sdk@6ebd820d10794f1b52bb06ef6c19512888a1401b`](https://github.com/OpenHands/software-agent-sdk/tree/6ebd820d10794f1b52bb06ef6c19512888a1401b)，仓库职责分工与本地模式说明依据 [`OpenHands/OpenHands@928873b4c2efb5a17ffa93eb541c78bb43a109f3`](https://github.com/OpenHands/OpenHands/tree/928873b4c2efb5a17ffa93eb541c78bb43a109f3)，核对日期 2026-09-23。全文基于静态源码阅读，聚焦同步 `LocalConversation.run()` 与默认 `Agent.step()` 主路径；远程 Agent Server、异步接口、Canvas 前端及进程崩溃后的外部副作用幂等性需结合对应模块另行核查。
