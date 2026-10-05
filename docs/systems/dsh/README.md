# DSH：用插件组装运行器，安排工具协作

[返回系统目录](../README.md) · [关键代码导读](code-walkthrough.md)

DSH 是 DeepSeek 开源的 **DeepSeek Harness**。Harness 可以先理解成“让模型持续工作的运行器”：它联系模型、管理会话、安排工具，并把执行结果交回模型。DSH 用插件提供这些能力，让应用可以按需要组装它们。

例如，模型一次提出读取三个文件。运行器要决定哪些读取可以同时开始、最多同时做几个，以及结果按什么顺序交回去。本篇从这件具体的事看 DSH 的设计。

## 工具怎样从请求走到结果

假设这三个调用依次是 A、B、C。程序先检查每次调用的输入和执行条件；需要用户审批时，必须获得允许才能继续。准备好后，允许并行的工具可以同时工作。结果出来后，程序按原调用顺序提交结果，让下一轮模型能把每个结果和自己的请求对应起来。

![工具执行可以重叠，事件结果仍按调用序列提交](../../../figures/dsh-tool-batch/diagram.svg)

[图源](../../../figures/dsh-tool-batch/scene.excalidraw) · [PNG 预览](../../../figures/dsh-tool-batch/preview.png) · [不看图的说明](../../../figures/dsh-tool-batch/README.md)

## 插件分别提供什么

| 部分 | 怎样接入 | 负责的事情 |
| --- | --- | --- |
| 应用组合 | 用插件框架 Cordis 组织插件，通过配置方案（profile）和组合包（bundle）选择服务；精简 SDK（`sdk-minimal`）也可单独接入 | 把模型、会话和工具等服务组装起来 |
| 工具调用 | 准备、审批、执行、后处理各有调用入口 | 检查输入和许可，执行工具，再提交对应结果 |
| 执行环境 | 文件系统、子进程服务和 bash sandbox 执行器 | 让工具使用同一执行环境，并按实际策略限制命令能访问的资源 |

表格依据固定版[架构说明](https://github.com/deepseek-ai/deepseek-harness/blob/477b4f420553e8a52c2fbccc464d7561b239c443/docs/architecture.md#L11-L35)和[文件系统、子进程服务说明](https://github.com/deepseek-ai/deepseek-harness/blob/477b4f420553e8a52c2fbccc464d7561b239c443/docs/architecture.md#L119-L137)。工具如何通过检查、执行和返回结果，可以接着读[代码导读](code-walkthrough.md)。

## B 先做完，结果仍排在 A 后面

批次调度器限制同时执行的工具数，源码把这叫“有界池”。在允许并行的情况下，B 可以比 A 先做完；但负责提交结果的 `commitReady()` 会先等 A，再提交已经准备好的 B。读者可以把它想成：几个人同时做事，报告仍按任务单的顺序摆放。

这样的好处是结果顺序稳定，代价是前面的慢工具会让后面的结果多等一会儿。实际能同时执行多少，还要看并发上限和各工具的执行模式。上图画的是批次内的结果顺序；工具在外部做的事情仍可能按完成先后发生。

## 使用前要留意的两件事

第一，调用要求询问用户、却没有可用审批服务时，这次调用会被拒绝。第二，bash sandbox 执行器采用 `danger-full-access` 策略时，会使用无约束的基础执行方式。沙箱（sandbox）是否生效，要看这次命令实际用了什么策略。

上游 [SAFETY.md](https://github.com/deepseek-ai/deepseek-harness/blob/477b4f420553e8a52c2fbccc464d7561b239c443/SAFETY.md)说明，此开发者预览尚未经过安全审计。尝试运行不可信代码时，需要另外保护真实文件、凭据和网络访问，不能只依赖它的沙箱与审批。本书尚未运行该 Harness。

## 与 Pi 比什么

[Pi](../pi/README.md)把循环核心与终端会话应用分开；DSH 更强调将多种服务作为插件组合。对照阅读时，先找两件事：新能力从哪里加入，工具从开始到结束由谁管理。这里比较的是组织方式，性能和易用性需要另做评测。

读完这页，可以用 A、B、C 的例子向别人解释“做完”和“交回结果”的区别。需要先熟悉基本循环的话，回到 [Agent loop](../../concepts/agent-loop.md)即可。

## 来源与阅读范围

本文依据官方仓库 [`deepseek-ai/deepseek-harness@477b4f420553e8a52c2fbccc464d7561b239c443`](https://github.com/deepseek-ai/deepseek-harness/tree/477b4f420553e8a52c2fbccc464d7561b239c443)，核对日期 2026-09-27。根许可证为 MIT，另有第三方说明。这是开发者预览版，本篇只读了相关源码，尚未安装或运行它。
