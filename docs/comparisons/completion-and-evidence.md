# Agent 说“完成”时，哪些证据够用？

[返回横向对照](README.md) · [观察、测试与评测](../concepts/observation-evaluation.md) · [循环为何停止](loop-and-stop.md)

**完成不是一个由模型单独写出的状态位，而是一组与原任务逐项对应的、可复查的声明。**读完本篇，应能把“Agent 停了”“工具返回了”“测试绿了”“产物存在”和“委托人接受了”分别写成有范围的结论，不用其中一项替另一项背书。[《循环为何停止》](loop-and-stop.md)研究控制流出口；这里研究**出口之后，报告能说到哪一步**。

> **范围与证据（2026-09-24 核对）。**系统侧只引用本书已固定的 Pi `898ab804`、mini-SWE-agent `04d809ce`、OpenCode `18ef3cc7`、Kimi Code `75a894e9` 的局部源码切面；评价方法引用[观察与评测篇](../concepts/observation-evaluation.md)及其中的官方资料。下文任务、命令输出和验收结果是**教学构造**，并未在四套系统上同配置运行；不据此排名正确率或宣称用户验收。

## 同一任务：改对数字，还要守住原规则

设想用户要求：“把服务超时时间从 30 秒改成 5 秒；保持现有重试规则；只改相关文件并运行测试；不要提交或推送。最后告诉我改了什么、测了什么、还没验证什么。”假设 Agent 修改了配置，跑过一条测试命令，最后回答“完成”。我们要检验的不只是 `timeout=5`：`retries` 没被破坏、修改范围没有越界、命令确实运行、最终没有提交或推送，都是原任务的一部分。

以下每一层只允许得出**它所覆盖的那句话**。它是从弱到强的报告练习，不是“一旦上了一层，底层自动全部成立”的通用分数；例如人工说“看起来好”不能填补缺失的测试日志。

| 想在交付中说什么 | 至少保留什么可复核证据 | 仍不能推出什么 |
| --- | --- | --- |
| “Agent 这一轮结束了” | 对应运行 ID、结束事件或退出状态及原因。 | 文件已改、测试已跑，更不能推出用户目标满足。 |
| “测试命令执行过” | 同一工作区版本下的命令、参数、环境、退出码、原始输出或测试报告。 | 退出码 0 等于修复正确；工具记录也可能只覆盖局部调用。 |
| “交付物已产生” | 目标文件的实际 diff、基线 commit、工作树状态；若要求生成文件，还要检查内容而非仅看路径存在。 | 文件符合需求，或没有改坏别处。 |
| “指定行为通过测试” | 用例与断言、被测版本、输入、环境、通过/失败记录；本例至少断言 5 秒值与原重试规则。 | 未测配置、真实依赖、性能或生产行为也成立。 |
| “任务边界遵守了” | 完整改动范围与相关操作记录；本例还要核对本地 Git 状态及远端是否发生写入。 | 不完整轨迹可证明从未有越权动作；一个单元测试可替代权限审计。 |
| “可以验收／用户已接受” | 对照原要求的复核结论与明确接受者、范围、日期；重要场景还需集成验证或实际使用反馈。 | 所有未来输入都正确，或一次主观认可就是系统性评测。 |

这张表的逻辑是**结论不能超过证据覆盖面**。命令退出码只描述那个进程的结束；测试通过只描述其断言在特定版本和环境下成立；文件存在只描述一种磁盘状态；接受则是任务所有者或明确授权的验收关口作出的决定。[观察与评测篇](../concepts/observation-evaluation.md)还区分单次日志/trace、针对性测试、跨任务离线 eval 和人工反馈：它们的观察对象与时间尺度不同，不能互换。[OpenTelemetry 的信号概念](https://opentelemetry.io/docs/concepts/signals/) · [LangSmith 的评测类型](https://docs.langchain.com/langsmith/evaluation-types)

## 四套固定路径留下的是线索，不是验收章

| 固定源码切面 | 它能提示复核者什么 | 报告“修复完成”还缺什么 |
| --- | --- | --- |
| [Pi 核心与 coding-agent](../systems/pi/code-walkthrough.md) | `runLoop` 可发结束事件；工具错误会形成 `isError` 结果；coding-agent 的常规消息另记入会话树。 | 结束事件不是测试断言；会话记录仍要对照实际 diff 和测试输出。 |
| [mini-SWE-agent 基类／本地环境](../systems/mini-swe-agent/code-walkthrough.md) | 消息尾部 `exit` 让基类循环结束；`Submitted`、限额、连续格式错误可形成不同出口；`save()` 仅在配置路径时落文件。 | `exit` 或提交哨兵不能证明 5 秒与重试条件都满足；默认交互 CLI 也不等于此基类。 |
| [OpenCode 会话处理器](../systems/opencode/code-walkthrough.md) | 单个 `ToolPart` 可有 `completed/error` 及结果内容；Session 另有 `busy/retry/idle`。 | `completed` 是调用结果状态，不是任务验收；`idle` 也不能代替文件与断言复核。 |
| [Kimi Code 单 turn](../systems/kimi-code/code-walkthrough.md) | `turn.ended` 区分 `completed/cancelled/failed`；`maxSteps`、取消与 steer 影响能否继续。 | `completed` 表示这个 turn 正常结束，不证明改动正确、未越界，亦不代表外层 goal 或用户已验收。 |

固定源码依据分别是 [Pi 的回合结束与工具结果](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/agent/src/agent-loop.ts#L279-L320)、[Pi 工具错误包装](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/agent/src/agent-loop.ts#L773-L861)、[mini-SWE-agent 的循环与退出分支](https://github.com/SWE-agent/mini-swe-agent/blob/04d809ceab9df28f9adaed044884180159172930/src/minisweagent/agents/default.py#L88-L124)、[mini-SWE-agent 的本地提交哨兵](https://github.com/SWE-agent/mini-swe-agent/blob/04d809ceab9df28f9adaed044884180159172930/src/minisweagent/environments/local.py#L24-L56)、[OpenCode 的调用结果](https://github.com/anomalyco/opencode/blob/18ef3cc7c5a25b82114c953a80ccc09f4988f74e/packages/opencode/src/session/processor.ts#L383-L420)、[OpenCode 的会话状态](https://github.com/anomalyco/opencode/blob/18ef3cc7c5a25b82114c953a80ccc09f4988f74e/packages/opencode/src/session/status.ts#L30-L48)、[Kimi Code 的 turn 结束映射](https://github.com/MoonshotAI/kimi-code/blob/75a894e9ad5e8d49509664b3daaa1bbc9bb39432/packages/agent-core/src/agent/turn/index.ts#L441-L510)。这些只证明相应提交中**可能的控制与记录分支**；本篇没有本例的真实执行日志，也没有把某个系统内部状态当作测试结果。

## 两个“看上去完成”的失败样本

**样本一：绿灯覆盖错了条件。**Agent 把 `timeout` 改为 5 秒，跑 `test_timeout_value` 得到退出码 0，并生成最终回复；但它同时把 `retries=3` 改成 `retries=0`。这与“模型停了”“测试绿了”“文件存在”完全相容，却违反“保持重试规则”。实际 diff 和覆盖两项约束的断言才会暴露缺口。这是**构造反例**，不是任何上游系统的已观察故障。[观察与评测篇的同题反例](../concepts/observation-evaluation.md#失败反例五种证据仍可能指向不同结论)

**样本二：摘要把未做的事写成做过。**Agent 回复“已运行全部测试”，但只有一次模型文字和最终事件，没有相应工具调用结果；又写“未推送”，却没有核对远端状态。即使最终补丁恰好正确，交付报告里这两句话也没有匹配证据。反过来，若工具结果显示测试失败，不能因为 turn 后来正常结束就省略失败。证据链要把**同一任务、同一工作区版本、同一次命令与结论**连起来；缺任何一环，都应缩小措辞或标“未核对”。

因此一次诚实的交付可以写成：“`config.yaml` 的 diff 将超时设为 5 秒；重试配置未在 diff 中改变。针对这两项的测试在版本 X、环境 Y 以命令 Z 运行并通过；集成环境及真实用户等待体验未验收。没有执行提交或推送；远端状态的独立核查若未做，则不能进一步宣称远端绝无变化。”这里的 X/Y/Z 是待填的**证据位置**，不是本书已经得到的测试结果。

## 读完自测

1. `turn.ended(completed)`、`Agent` 结束事件或 `exit` 出现后，最强能先说什么？说对应范围内的循环／turn 结束及原因；继续核对改动、工具结果和验收条件。
2. 测试命令退出码为 0，能否直接说“重试规则没变”？不能；要知道该测试断言了什么，并看实际 diff 与被测版本。
3. `ToolPart.completed` 且输出文件存在，可以宣称用户已接受吗？不能；工具、产物和接受者的判断分属不同证据层。
4. 轨迹缺失一段时，“未观察到推送”是否等于“证明没有推送”？不等于；说明采集边界，必要时核对远端。

**下一步如何验证本章。**在授权的练习仓库固定 commit、配置、Agent 版本及同一任务，保存去敏的模型／工具事件、前后 diff、完整测试命令与断言、Git 本地和远端状态，再请不参与执行的人按原验收条件判读。这样的实验才会得到一次任务的运行观察；当前文章只给出静态源码支持的状态边界和工程上的证据门槛。
