# DSH 代码导读：并发完成、顺序提交与拒绝执行

[返回 DSH 剖面](README.md)

固定版本为 `477b4f420553e8a52c2fbccc464d7561b239c443`，核对日期 2026-09-27。本篇只读工具批次与授权/执行器接缝，没有启动模型、CLI 或操作系统隔离环境。以下顺序是导读顺序，表里的原文件链接才是实现依据。

## 1. 先找工具批次，不从包目录背起

[`executeToolCalls()`](https://github.com/deepseek-ai/deepseek-harness/blob/477b4f420553e8a52c2fbccc464d7561b239c443/packages/core/agent-loop/src/tool-calls.ts#L60-L101)先定位发起 Agent 和会话，并按当前工具执行模式组织批次。模式会被重新检查，因此不要把模型给出的多个 tool call 直接画成几个已经运行的进程。

## 2. 准备与执行分开观察

[`runGroup()`](https://github.com/deepseek-ai/deepseek-harness/blob/477b4f420553e8a52c2fbccc464d7561b239c443/packages/core/agent-loop/src/tool-calls.ts#L122-L213)维护有界池。`startCall()`先记录调用、再准备；准备可能直接得到最终结果，或得到可 dispatch 的执行对象。准备阶段串行推进，实际 dispatch 可以重叠。读轨迹时，应分别找“调用记录”“批准/拒绝”“dispatch”“结果记录”，不能用其中一个替代其余三个。

## 3. 哪个变量维护结果次序

同文件的 [`commitReady()`](https://github.com/deepseek-ai/deepseek-harness/blob/477b4f420553e8a52c2fbccc464d7561b239c443/packages/core/agent-loop/src/tool-calls.ts#L147-L159)从当前提交位置连续取 ready 结果。下面是教学推演，不是实测：

```text
调用次序       A → B → C
完成次序       B → A → C   （假设）
事件提交       A → B → C
观察边界       B 完成时，A 尚未 ready，提交位置仍等 A
```

这是批次内的结果提交顺序，不是远端副作用的发生顺序。若 B 发出真实网络写入，它完全可能先改变远端；有序日志不会把外部世界自动串行化。

## 4. 取消与调度异常不是“没有发生”

[`runGroup()` 的异常/取消分支](https://github.com/deepseek-ai/deepseek-harness/blob/477b4f420553e8a52c2fbccc464d7561b239c443/packages/core/agent-loop/src/tool-calls.ts#L219-L242)处理已启动工作与尚未 dispatch 的调用。异常时等待在途工作结算并传播失败；取消时，未启动的调用可记录跳过结果。代码不能证明已经 dispatch 的外部操作被撤销，也不允许把缺结果自动补成成功。需要判断外部动作是否完成时，读[回执与副作用练习](../../labs/remote-effect.md)。

## 5. 从 pre-execute 跟到审批

[`prepareExecution()`](https://github.com/deepseek-ai/deepseek-harness/blob/477b4f420553e8a52c2fbccc464d7561b239c443/packages/core/tools/src/index.ts#L1489-L1539)处理预执行决定、询问审批和 guard，再检查取消状态。pre-execute 的默认终端值为 `allow`；只有决定为 `ask` 时才进入询问。不同入口有不同责任：pre-execute 可以要求询问，guard 则提供不能被后续 allow 逆转的拒绝接缝。不要把一个 allow hook 写成能覆盖所有拒绝的万能插件，也不要把“缺询问通道时拒绝”误读成所有调用默认都要求询问。

[`serviceAsk()`](https://github.com/deepseek-ai/deepseek-harness/blob/477b4f420553e8a52c2fbccc464d7561b239c443/packages/core/tools/src/index.ts#L1727-L1767)在无审批服务或无 Agent 上下文等情况下返回拒绝；批准一次与拒绝/取消/不可用分别映射为允许与拒绝。**默认预执行决定**和**要求询问但无法询问**是两种分支，不能混称“默认放行”。

## 6. 有审批还要核对执行器

[`SandboxBashExecutor.execute()`](https://github.com/deepseek-ai/deepseek-harness/blob/477b4f420553e8a52c2fbccc464d7561b239c443/packages/shell/bash-sandbox/src/index.ts#L85-L133)解析本次策略。`danger-full-access` 路径调用基础执行器；其他策略经 [`ctx.sandbox.confine()`](https://github.com/deepseek-ai/deepseek-harness/blob/477b4f420553e8a52c2fbccc464d7561b239c443/packages/shell/bash-sandbox/src/index.ts#L187-L189)构造受约束命令。runner failure 会成为 sandbox 不可用错误；不要把这种错误消除为“那就普通执行”。本篇未检查各操作系统 confine backend，也没有隔离逃逸测试。

## 三个自测问题

1. B 比 A 先完成，模型是否因此先得到 B 的事件结果？**本批次提交器仍按调用顺序等待连续 ready 结果；这不限制外部副作用次序。**
2. 插件要求审批，但当前没有审批服务，应画允许还是拒绝？**拒绝；缺询问通道不是用户批准。**
3. 图中出现 sandbox 执行器，能否宣布整个程序安全？**不能；须检查实际策略、backend、凭据、出网和上游安全声明。**

下一步运行实验应在专用无真实凭据的环境中，只放 A/B 两个确定性假工具，记录准备、启动、完成和提交四类事件，再分别注入拒绝与取消。本文只提出验收方案，未将它标作可复跑的成品实验。
