# DSH 代码导读：几个工具同时做事，结果按顺序交回

[返回 DSH 首页](README.md)

接着首页的 A、B、C 例子往下读：这三个工具可以怎样同时开始，B 先完成时结果放在哪里，需要批准的调用又在哪里停下。先跟着正常流程，再看取消与执行环境。

固定版本为 `477b4f420553e8a52c2fbccc464d7561b239c443`，核对日期 2026-09-27。本篇依据静态源码介绍工具批次、批准检查和执行器，尚未启动 DSH。

## 1. 先决定哪些工具可以一起做

[`executeToolCalls()`](https://github.com/deepseek-ai/deepseek-harness/blob/477b4f420553e8a52c2fbccc464d7561b239c443/packages/core/agent-loop/src/tool-calls.ts#L60-L101)先找到发起调用的 Agent 和会话，再查看工具当前的执行模式。允许并行的调用可以组成一组；要求独占的调用单独处理。程序处理后续调用时还会重新看执行模式。

## 2. 先检查每次调用，再安排执行

[`runGroup()`](https://github.com/deepseek-ai/deepseek-harness/blob/477b4f420553e8a52c2fbccc464d7561b239c443/packages/core/agent-loop/src/tool-calls.ts#L122-L213)限制同时执行的数量。`startCall()` 先记录调用，再完成准备。准备时可能得到拒绝等最终结果，也可能得到一个可以开始执行的对象。

准备按次序进行，实际执行可以重叠。源码把“开始执行”叫 dispatch，把“结果已可交回”叫 ready。按这两个词往下读，就能分别找到工具何时开始、何时做完。

## 3. B 先做完，提交器先等 A

同文件的 [`commitReady()`](https://github.com/deepseek-ai/deepseek-harness/blob/477b4f420553e8a52c2fbccc464d7561b239c443/packages/core/agent-loop/src/tool-calls.ts#L147-L159)从当前序号开始，依次提交已经就绪的结果。用假设的完成顺序说明：

```text
调用次序       A → B → C
完成次序       B → A → C   （假设）
结果提交       A → B → C
B 完成时       A 还没做完，先保留 B 的结果，等 A 就绪
```

这里排好的是交回的结果。如果 B 实际修改了远端数据，修改可能已经比 A 更早发生。要知道外部操作的先后，还要看工具本身的执行记录。

## 4. 等待批准的调用，在哪里停下

[`prepareExecution()`](https://github.com/deepseek-ai/deepseek-harness/blob/477b4f420553e8a52c2fbccc464d7561b239c443/packages/core/tools/src/index.ts#L1489-L1539)处理执行前的决定。预执行处理（pre-execute）默认给出 `allow`；给出 `ask` 时，就先询问审批。保护检查（guard）还可以拒绝调用，后续的 allow 处理无法覆盖这项拒绝。最后还会检查是否已经取消。

需要询问时，[`serviceAsk()`](https://github.com/deepseek-ai/deepseek-harness/blob/477b4f420553e8a52c2fbccc464d7561b239c443/packages/core/tools/src/index.ts#L1727-L1767)负责取得决定。批准一次会映射为允许；拒绝、取消、服务不可用或缺少 Agent 信息时，会映射为拒绝。因此，需要用户批准的调用，必须先拿到允许才能执行。

## 5. 用哪种环境执行命令

[`SandboxBashExecutor.execute()`](https://github.com/deepseek-ai/deepseek-harness/blob/477b4f420553e8a52c2fbccc464d7561b239c443/packages/shell/bash-sandbox/src/index.ts#L85-L133)读取本次执行策略。`danger-full-access` 使用基础执行器，其他策略通过 [`ctx.sandbox.confine()`](https://github.com/deepseek-ai/deepseek-harness/blob/477b4f420553e8a52c2fbccc464d7561b239c443/packages/shell/bash-sandbox/src/index.ts#L187-L189)构造带限制的命令。沙箱执行器不可用时会返回相应错误，程序不会在这个分支自动改为普通执行。

各操作系统怎样实现这些限制，需要继续检查对应后端；本篇尚未做隔离测试。

## 6. 取消、报错和结束提示怎样处理

[`runGroup()` 的异常与取消处理](https://github.com/deepseek-ai/deepseek-harness/blob/477b4f420553e8a52c2fbccc464d7561b239c443/packages/core/agent-loop/src/tool-calls.ts#L219-L242)区分已经开始和还没开始的工作：调度出错时，先等已开始的工具返回，再向上报告错误；取消时，未开始的调用可以记为跳过。已经发出的网络操作是否完成，仍要向目标系统核对。想进一步理解这种情况，可以读[回执与副作用练习](../../labs/remote-effect.md)。

某个结果还可以带 `concludesTurn: true`，表示希望结束当前回合。批次把这个提示汇总为 `concluded`，交给上层程序；余下工具仍按批次流程处理。上层怎样收尾，要继续看调用方。[汇总结束提示](https://github.com/deepseek-ai/deepseek-harness/blob/477b4f420553e8a52c2fbccc464d7561b239c443/packages/core/agent-loop/src/tool-calls.ts#L147-L159) · [继续批次并返回](https://github.com/deepseek-ai/deepseek-harness/blob/477b4f420553e8a52c2fbccc464d7561b239c443/packages/core/agent-loop/src/tool-calls.ts#L83-L101)

## 读完可以怎样讲给别人

工具先通过执行前检查，允许并行的一起做，结果按请求顺序交回。需要批准却没有批准服务的调用会停下；要知道命令实际能访问哪里，还要看执行策略。

若以后补运行实验，可以先在专用、没有真实凭据的环境里放两个假工具，分别记录准备、开始、完成和交回结果。这个实验尚未实现，本篇只提供读代码的方法。
