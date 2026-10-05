# Agent 说“完成”时，哪些证据够用？

[返回横向对照](README.md) · [观察、测试与评测](../concepts/observation-evaluation.md) · [循环为何停止](loop-and-stop.md)

一次清楚的交付会告诉你：做出了什么，检查了什么，还有哪一步等你确认。比如资料助手给出时间、地点和报名要求，每项附上出处，你就能逐项核对。编码助手则要拿出修改文件和测试结果。本篇把这些成果连到原任务，帮你读懂一份“完成报告”。[《循环为何停止》](loop-and-stop.md)解释程序在哪停下；这里接着看停下后怎样交付。

> **范围（2026-09-24 核对）。** 引用 Pi `898ab804`、mini-SWE-agent `04d809ce`、OpenCode `18ef3cc7`、Kimi Code `75a894e9` 的固定源码路径，以及[观察与评测篇](../concepts/observation-evaluation.md)中的官方资料。下文任务与结果为教学构造，尚无四套系统同配置实测。

## 先用一个只读回答看“完成”

回到[读书会资料助手](../concepts/agent-loop.md#先看一次正常完成)：用户要活动时间、地点、是否报名，还要每项的出处。助手读到 `D1`、`D2`、`D3` 后，可以整理三项答案；你按编号回到原文，核对它有没有读对、有没有漏项。资料取回、答案形成和用户确认，就这样连成一条交付路径。

若暂时只拿到 `D1`、`D2`，可以先交付“周六 14:00 [D1]、图书馆二楼 [D2]，报名要求待核对”。明确标出缺项，用户就知道下一步要补哪份材料，而不会把未读到的 `D3` 猜成“无需报名”。

这个例子不需要写代码，也能看出四层差别：循环是否结束、资料是否返回、回答是否有相应出处、用户是否接受。下一个仓库修改案例把同一原则延伸到文件、测试和禁止推送的边界。

## 同一任务：改对数字，还要守住原规则

设想用户要求：“把服务超时时间从 30 秒改成 5 秒；保持现有重试规则；只改相关文件并运行测试；不要提交或推送。最后告诉我改了什么、测了什么、还没验证什么。”助手修改文件、运行测试之后，就按这份要求组织报告。

把这条要求拆成清单后，检查就很直接：超时值是 5、重试规则仍在、文件范围合适、相关测试跑过、未提交推送。下表给每类结论配一个检查位置，按需使用即可。

| 想在交付中说什么 | 检查位置 | 接下来还要看什么 |
| --- | --- | --- |
| “Agent 这一轮结束了” | 对应运行 ID、结束事件或退出状态及原因。 | 文件、测试与任务清单。 |
| “测试命令执行过” | 同一工作区版本下的命令、参数、环境、退出码、原始输出或测试报告。 | 命令实际检查的条件和失败详情。 |
| “交付物已产生” | 文件实际内容、diff、基线 commit 与工作树状态。 | 内容是否符合要求，以及其他改动。 |
| “指定行为通过测试” | 用例、断言、被测版本、输入与环境；本例检查 5 秒值及原重试规则。 | 任务所需的集成环境、真实依赖和未覆盖场景。 |
| “任务边界遵守了” | 完整改动范围与相关操作记录；本例核对本地 Git 和远端写入情况。 | 记录采集的范围与缺口。 |
| “候选成果可以提交验收” | 对照原要求的清单、已做检查、未覆盖项和产物位置。 | 指定接受者的判断。 |
| “用户已接受” | 接受者确认的范围、版本和日期；重要场景加入集成或使用反馈。 | 后续输入与长期使用的表现。 |

读表时记住一条写报告的方法：**每个结论后面，写出对应的文件或记录。** 退出码描述一次进程结束，测试报告描述特定版本和环境下的断言，用户确认描述被接受的成果范围。[观察与评测篇](../concepts/observation-evaluation.md)还介绍单次日志／轨迹（trace）、针对性测试、跨任务评测（eval）和人工反馈，适合继续了解不同尺度的检查。[OpenTelemetry 的信号概念](https://opentelemetry.io/docs/concepts/signals/) · [LangSmith 的评测类型](https://docs.langchain.com/langsmith/evaluation-types)

## 四套系统怎样记录过程

| 固定源码路径 | 程序留下什么记录 | 交付时怎样使用 |
| --- | --- | --- |
| [Pi 核心与 coding-agent](../systems/pi/code-walkthrough.md) | `runLoop` 发结束事件；工具错误形成 `isError` 结果；coding-agent 将常规消息记入会话树。 | 用记录定位本次操作，再对照文件差异（diff）与测试输出。 |
| [mini-SWE-agent 基类／本地环境](../systems/mini-swe-agent/code-walkthrough.md) | 消息尾部 `exit` 结束基类循环；`Submitted`、限额、连续格式错误对应不同出口；配置了保存路径时 `save()` 落文件。 | 先辨认出口原因，再检查 5 秒值和重试条件。默认交互 CLI 的子类要另读。 |
| [OpenCode 会话处理器](../systems/opencode/code-walkthrough.md) | `ToolPart` 记录单次调用的 `completed/error` 与内容；Session 记录会话 `busy/retry/idle`。 | 调用状态帮助找到对应输出；任务清单用文件和断言检查。 |
| [Kimi Code 单 turn](../systems/kimi-code/code-walkthrough.md) | `turn.ended` 区分 `completed/cancelled/failed`；`maxSteps`、取消与 steer 影响续跑。 | `completed` 说明本 turn 正常结束；改动、外层目标和用户确认另有检查位置。 |

想追源码，可从 [Pi 的回合结束与工具结果](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/agent/src/agent-loop.ts#L279-L320)、[Pi 工具错误包装](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/agent/src/agent-loop.ts#L773-L861)、[mini-SWE-agent 的循环与退出分支](https://github.com/SWE-agent/mini-swe-agent/blob/04d809ceab9df28f9adaed044884180159172930/src/minisweagent/agents/default.py#L88-L124)、[mini-SWE-agent 的本地提交哨兵](https://github.com/SWE-agent/mini-swe-agent/blob/04d809ceab9df28f9adaed044884180159172930/src/minisweagent/environments/local.py#L24-L56)、[OpenCode 的调用结果](https://github.com/anomalyco/opencode/blob/18ef3cc7c5a25b82114c953a80ccc09f4988f74e/packages/opencode/src/session/processor.ts#L383-L420)、[OpenCode 的会话状态](https://github.com/anomalyco/opencode/blob/18ef3cc7c5a25b82114c953a80ccc09f4988f74e/packages/opencode/src/session/status.ts#L30-L48)、[Kimi Code 的 turn 结束映射](https://github.com/MoonshotAI/kimi-code/blob/75a894e9ad5e8d49509664b3daaa1bbc9bb39432/packages/agent-core/src/agent/turn/index.ts#L441-L510)读起。它们解释对应版本中的控制与记录分支。

## 一份简短的交付报告

可以按三项组织这个配置任务的候选报告：

- **改动**：`config.yaml` 中超时设为 5 秒；diff 中重试配置保持原样，附文件位置。
- **检查**：两项测试在版本 X、环境 Y 以命令 Z 运行通过，附完整报告。
- **待确认**：集成环境与实际等待体验还需检查；执行记录中没有提交或推送，远端状态是否独立核查应另写清。

X／Y／Z 是需要填写的实际记录位置。这是报告模板，书中尚无这条任务的真实测试结果。

## 两个“看上去完成”的失败样本

**样本一：测试漏了一项要求。** Agent 把 `timeout` 改为 5 秒，`test_timeout_value` 返回 0，但同时将 `retries=3` 改成了 `retries=0`。查看 diff，并把重试条件加入断言，就能发现缺项。这是教学构造的反例。[观察与评测篇的同题反例](../concepts/observation-evaluation.md#把检查条件写完整)

**样本二：报告缺少对应记录。** 最终回复写了“已运行全部测试”，却找不到测试工具结果；写了“未推送”，却没有独立核对远端。把同一任务、工作区版本和实际命令连起来，已有结果如实记录，缺项标为“待核对”。失败的测试也留在报告中，方便下一步继续处理。

## 带回自己的任务

拿一份你熟悉的 AI 交付报告，画出三栏：**原要求、交付内容、检查位置**。把“已完成”拆成具体条目；测试通过就附用例与被测版本，文件生成就检查实际内容，用户确认就写确认范围。缺少记录的位置标为“待核对”，再决定需要补哪一步。你的成果是一份读者能沿链接复查的简短清单。

## 本篇范围

本文的源码记录与教学样本用于解释检查位置，尚未对四套系统做这条任务的实测，或评价正确率与用户接受情况。若要继续验证，可在获准的练习仓库固定版本、配置和任务，保存去敏的模型／工具事件、前后 diff、测试报告以及 Git 本地和远端状态，再请另一位读者按原要求检查。
