# 跟着 Pi 代码走一轮：从 `prompt()` 到会话树投影

[返回 Pi 首页](README.md) · 固定源码版本 [`898ab804`](https://github.com/earendil-works/pi/tree/898ab804050730e9dcefb4443875d5a932aa6a32)

自己动手写过第一个 Agent 循环的人，几乎都会在三天内撞上同一批暗礁：模型输出撞上 `max_tokens` 被拦腰截断，半截残缺的 JSON 参数直接把工具层炸崩；用户趁工具跑着的时候追发了一句话，结果两条并发循环同时往 `messages` 数组里乱塞消息；上游 API 偶发 529 过载报错，重试一次却把上一次失败的残骸留在上下文里，惹得模型一脸茫然。

这一篇我们就以「读取文件并修改代码」为主线，像拆解机械机芯一样，顺着 `pi-agent-core` 与 `pi-coding-agent` 的真实函数签名跟读一整轮，看 Pi 是怎样在几百行核心代码里把这些工程暗礁逐一排干的。

## 1. 单入口互斥与消息双层转换

一切从 [`Agent.prompt()`](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/agent/src/agent.ts#L367-L442) 开始。它做的第一件防呆动作，就是**严禁重入**：只要当前已经有任务在跑，第二个直接打进来的 `prompt()` 调用会被当场拒绝，逼着调用方明确表态——你到底是想中途改方向（走 `steer`），还是等干完活再加菜（走 `followUp`），从根源上杜绝两个循环并发篡改同一份内存状态。

通过入口检查后，用户任务进入 [`runLoop`](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/agent/src/agent-loop.ts#L162-L320)。每次真正向大模型发起流式请求前，Pi 不会把内存里的原始消息直接裸发出去，而是依次走过三步准备管线（见[准备这一轮](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/agent/src/agent-loop.ts#L181-L241)与[组成模型输入](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/agent/src/agent-loop.ts#L380-L406)）：

1. **请求前准备**（`prepareRequest`）：运行宿主配置的请求前异步准备逻辑（例如刷新动态状态）。
2. **业务上下文裁剪**（`transformContext`）：在 Agent 内部消息层面做裁剪、注入或过滤（此时操作的仍是应用认识的业务消息对象）。
3. **协议格式映射**（`convertToLlm`）：最后一步才把业务消息翻译成 `pi-ai` 统一模型接口所需的标准协议格式，交给 `streamFn` 流式拉取回复。

为什么要把 `transformContext` 和 `convertToLlm` 拆成两步？因为应用常常会在内存消息上挂载 UI 展示字段或内部标记——先在业务层剪裁完，最后再做纯净的协议映射，两边才不会互相污染。

## 2. 工具调用的四道防线：截断拦截、钩子门禁与并行保序

当模型流式吐完一条带工具调用的回复时，新手最容易犯的错是拿到 `toolCalls` 就立刻遍历执行。Pi 在真正调工具前立下了四道关键防线：

### 第一道：输出截断整批熔断

如果模型正在生成一段三百行的 `write` 文件内容，突然撞上输出长度上限（`length` 截断），工具参数虽然外层结构看似存在，内容却只写了一半。一旦贸然执行，就会用半截残废代码直接覆盖掉用户磁盘上的好文件！因此 Pi 先检查停止原因：只要因长度超限截断且含有工具调用，**当场给整批调用生成失败结果返回**，绝不让残缺参数触碰真实工具（见[输出截断处理](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/agent/src/agent-loop.ts#L475-L499)）。

### 第二道：参数校验与前后置钩子短路

对于完整生成的调用，程序依次查找工具定义、校验参数结构，再调用宿主配置的 `beforeToolCall` 钩子。只要找不到工具、参数不合法或被前置钩子拦截，程序立刻合成错误结果，**直接跳过真实执行与后置钩子**（`execute` 与 `afterToolCall`）；只有放行后才执行工具并走后置处理（见[执行前的检查](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/agent/src/agent-loop.ts#L703-L771)与[执行与结果处理](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/agent/src/agent-loop.ts#L773-L861)）。需要注意，这些钩子与工具列表都通过[可配置的 AgentOptions](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/agent/src/agent.ts#L113-L140) 注入，`pi-agent-core` 本身并不自带操作系统级沙箱。

### 第三道：一票降级的并行与严格按序落账

模型一轮同时发起三个 `read` 调用时，串行等待太慢；可如果其中夹了一个有副作用的工具呢？Pi 的[默认模式](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/agent/src/agent.ts#L244-L250)允许并行，但在[选择执行模式](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/agent/src/agent-loop.ts#L505-L520)时采用「一票否决」：只要全局配置要求串行，或者当前批次里**哪怕只有一个工具**不允许并发，整批就退回顺序执行。而在并行分支里，[收集并行结果](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/agent/src/agent-loop.ts#L583-L657)等所有任务返回后，仍严格按模型原本请求的次序写入消息列表（当然，若两个并行工具同时写同一个外部文件，磁盘层面的竞态仍需工具自身规避）。

## 3. 双队列检查点与核外事件落盘

工具跑完一轮后，用户在途中发来的补充指令怎么进场？对照源码里的三个位置，双队列的咬合时机非常清晰：

- **写入队列**：`steer()` 与 `followUp()` 把新消息分别压入各自的内存队列（见[放入队列](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/agent/src/agent.ts#L142-L173)）。
- **轮间急转弯**（`steering`）：在首次请求模型前、每个回合之间，甚至在异步 `prepareRequest` 跑完之后都会再次补查 steering 队列——哪怕用户正好卡在准备请求的几十毫秒空隙里按下回车，这句纠偏指令也能赶在本轮发往模型前塞进去（见[取出 steering](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/agent/src/agent-loop.ts#L174-L215) 与[准备之后再看新输入](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/agent/src/agent-loop.ts#L181-L207)）。
- **收尾续单**（`follow-up`）：只有当模型不再请求工具、steering 也已清空、整个循环眼看就要收工退出时，才去检查 follow-up 队列，把追加任务拉进来开启下一轮（见[取出 follow-up](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/agent/src/agent-loop.ts#L279-L320)）。

与此同时，`runLoop` 内部一行写磁盘的代码都没有。每当一条用户、助手或工具消息尘埃落定，它只管广播 `message_end`；外层 `pi-coding-agent` 里的 `AgentSession` 监听到这个事件后，才把常规消息交给 `SessionManager`，以带父子指针的节点追加进 JSONL 会话树（见[交给会话管理器](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/coding-agent/src/core/agent-session.ts#L921-L943)、[会话树](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/coding-agent/src/core/session-manager.ts#L976-L1005)、[整理当前分支](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/coding-agent/src/core/session-manager.ts#L543-L582)，特定维护操作下也会[重写会话文件](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/coding-agent/src/core/session-manager.ts#L1124-L1134)）。

把核内循环与核外持久化的配合画在一张图上，主干一目了然：

```text
Agent.prompt(input) ──► runLoop
  │
  ├─► [请求前] drain(steering) → prepareRequest → 补查 steering → transformContext → convertToLlm → streamFn
  ├─► [有工具调用] 检查长度截断 → 校验参数 / beforeToolCall → execute → afterToolCall → 生成 toolResult
  ├─► [回合推进] 若有工具结果或新 steering，继续下一轮
  └─► [准备收尾] finishTurn 决策 → 若未强制结束则 drain(followUp)，有内容就继续跑，否则发 agent_end

（核外订阅）AgentSession 监听 message_end ──► SessionManager 追加 JSONL 节点并维护当前分支
```

## 4. 循环停机与续跑契约：错误转消息、`terminate` 与 `continue()`

在循环内部，**工具执行抛错不等于循环崩溃**。无论是工具内部抛异常，还是 `afterToolCall` 后置钩子抛错，都会被捕获并包装成带 `isError: true` 的工具结果送回下一轮，让大模型亲眼看到报错栈并自己想办法补救。只有当一个非空工具批次里**所有已完成调用的结果都显式要求终止**（`terminate: true`）时，工具批次才会主动要求提前结束本轮运行（见[处理工具错误](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/agent/src/agent-loop.ts#L773-L814)、[处理后置钩子](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/agent/src/agent-loop.ts#L816-L861)与[整批结束条件](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/agent/src/agent-loop.ts#L685-L687)）。

宿主还可以通过 `finishTurn` 精细接管收尾动作：返回 `end` 会立刻发出 `agent_end` 并跳过后面的 follow-up 队列；返回 `continue` 则在既无工具调用也无排队输入时，强行拿着现有历史再催模型往下走一步（见[回合收尾](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/agent/src/agent-loop.ts#L279-L320)）。

而当一次运行停下后，外部想调用 `continue()` 接着跑时，必须遵守大模型 API 的底层铁律——不能把一条孤零零的 `assistant` 回复作为末尾直接发给模型。因此 [`Agent.continue()`](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/agent/src/agent.ts#L380-L408) 发现末尾是助手回复时，会依次尝试从 steering 和 follow-up 队列捞出新输入垫在后面，两边都空就直接报错；[底层继续入口](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/agent/src/agent-loop.ts#L62-L99)同样要求转换后的末尾消息必须是用户输入或工具结果。

## 5. 故障恢复分层：核心快速止损，外壳接管重试与溢出压缩

为什么 `pi-agent-core` 不直接在 `runLoop` 里写死指数退避重试和自动摘要压缩？因为不同宿主（CLI 交互终端 vs 批处理评测脚本）对等待时间和摘要损耗的容忍度完全不同。Pi 的做法是**底层立停，外层施救**：

- **核心层快速止损**：一旦模型流以 `error` 或 `aborted` 结束，`runLoop` 立刻跳过回复中未跑的工具调用并发出结束事件；未捕获异常冒泡到 `Agent` 外层时，也会补一条记录错误或取消原因的助手消息再干净退出（见[底层处理](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/agent/src/agent-loop.ts#L240-L255)与[外层异常处理](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/agent/src/agent.ts#L503-L550)）。
- **外壳层瞬态报错重试**（无痕抹除坏回合）：`AgentSession` 接住结束后，判断错误类型与重试预算；决定重试时，那条失败的半截回复**依然保留在原始 JSONL 账本里备查**，但会被打上 `context_edit` 标记，使得下一次发给模型时自动隐去这次失败尝试，退避等待后再干净重发（见[选择是否重试](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/coding-agent/src/core/agent-session.ts#L1468-L1529)、[整理重试消息](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/coding-agent/src/core/agent-session.ts#L1015-L1031)与[等待后再试](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/coding-agent/src/core/agent-session.ts#L3375-L3419)）。
- **外壳层上下文溢出压缩**：如果报错是因为消息塞爆了模型窗口（Context Overflow），无脑重试只会再炸一次。`AgentSession` 会把这类错误分流到自动压缩管线：先对旧历史生成压缩摘要腾出窗口，再最多重试一次；若某轮回复已正常收尾但逼近阈值，则只做压缩为下一轮腾地方（见[区分错误类型](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/coding-agent/src/core/agent-session.ts#L3322-L3329)与[压缩与继续](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/coding-agent/src/core/agent-session.ts#L2599-L2696)）。
- **用户主动取消**：触发取消时，`Agent.abort()` 拉响底层中止信号，终端层的 `abort()` 则一并掐断正在倒计时的重试定时器与后台压缩任务，等待状态归于空闲——当然，取消信号只能停住未完成的计算，此前已经落盘的文件修改或已发出的外部网络写操作不会自动回滚（见[核心取消](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/agent/src/agent.ts#L332-L349)与[终端应用取消](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/coding-agent/src/core/agent-session.ts#L2072-L2092)）。

## 6. 调试长会话失忆：看懂消息的「三层投影」

很多开发者在排查长会话问题时会纳闷：「我明明在 `.jsonl` 会话文件里看到了第 5 轮那条消息，为什么第 30 轮模型表现得完全没见过它？」

读完 Pi 的链路就会明白，磁盘里存的跟模型眼睛里看到的根本不是同一份数组，中间隔着**三层投影**（见[保存消息](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/coding-agent/src/core/agent-session.ts#L921-L943)、[会话父子关系](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/coding-agent/src/core/session-manager.ts#L976-L985)、[整理当前分支](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/coding-agent/src/core/session-manager.ts#L543-L582)与[最终模型消息](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/agent/src/agent-loop.ts#L380-L406)）：

```text
第 1 层：JSONL 完整会话树（全量审计账本）
  [msg_1] ──► [msg_2: 529 失败尝试] ──► [context_edit: 隐藏 msg_2] ──► [compaction: 1~15 轮摘要] ──► [msg_16]
                 └──► [另一条历史分叉分支...]

第 2 层：SessionManager 当前分支投影（Agent 内存视图）
  只沿当前叶子节点的父指针回溯，用 compaction 摘要替换旧节点，剔除被 context_edit 屏蔽的失败记录
  ──► [summary(1~15), msg_16]

第 3 层：单次请求最终载荷（Provider 线协议视图）
  再经 transformContext 动态裁剪 + convertToLlm 协议转换
  ──► 发往大模型的最终 messages 字节流
```

顺着「原始账本 → 分支投影 → 请求载荷」这三级台阶逐层核对，任何「上下文丢了或多了」的疑难杂症都能在几分钟内定位到具体哪一层动了刀。

## 来源与边界

本文基于官方仓库固定提交 [`earendil-works/pi@898ab804050730e9dcefb4443875d5a932aa6a32`](https://github.com/earendil-works/pi/tree/898ab804050730e9dcefb4443875d5a932aa6a32) 的静态源码分析整理，核对日期 2026-09-23。其中第 5、6 节的自动重试、溢出压缩与 JSONL 会话树属于 `pi-coding-agent` 应用层策略；若仅将 `pi-agent-core` 嵌入自定义宿主，持久化与恢复逻辑需由宿主自行实现。
