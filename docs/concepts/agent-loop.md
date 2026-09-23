# Agent loop：一次行动怎样闭环

Agent 不只是“模型回答了一次”。对需要行动的任务，宿主通常要反复处理四类东西：本轮模型输入、模型提出的下一步、工具执行后的观察、继续或结束的判定。**模型建议调用工具**和**工具已经执行**之间还可能有参数校验、审批、沙箱及扩展钩子；**模型说完成了**和**结果真的可交付**之间也可能需要测试或人的验收。

![从任务目标到行动、观察与验证的概念循环](../../figures/agent-loop/diagram.svg)

[图的文字版](../../figures/agent-loop/README.md)说明了这只是教学模型，不是 Pi、Codex 或任何项目的真实内部拓扑。

## 用一条最小轨迹来读

```text
用户目标与边界 → 装配本轮输入 → 模型提出动作
             → 宿主校验/授权 → 工具执行 → 观察写回
             → 宿主判断继续、停止或失败 → 候选结果验证
```

沿这条线读源码，至少要找到三个控制点：谁组装模型能看到的输入，谁有权执行带副作用的动作，谁决定何时停止。不要把“模型返回一个 tool call”误当成执行日志，也不要把“退出循环”误当成任务成功。图中的最终验证是读者理解完整任务生命周期的**建议检查点**；它不声称下面三个项目都内置同一个验收器。

## 三种具体实现揭示不同边界

在固定版本的 [Pi](../systems/pi/README.md) 中，`Agent.prompt()` 进入运行循环；`runLoop` 组织模型请求、工具结果、steering 与 follow-up。coding-agent 的会话持久化在外壳层，不应画成 agent-core 本身的文件存储。[`runLoop` 源码](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/agent/src/agent-loop.ts#L162-L320)

[mini-SWE-agent](../systems/mini-swe-agent/README.md) 给出更短的对照：`DefaultAgent.step()` 组合 `query()` 与 `execute_actions()`，观察被追加进消息账本；基类 `run()` 看最后一条消息是否为 `role=exit`。资源上限、格式错误或提交哨兵也可能使循环结束，因此“停了”要继续问**因何而停**。[循环源码](https://github.com/SWE-agent/mini-swe-agent/blob/04d809ceab9df28f9adaed044884180159172930/src/minisweagent/agents/default.py#L88-L157)

[OpenCode](../systems/opencode/README.md) 把一次工具调用的 `pending/running/completed/error` 与整个 Session 的 `busy/retry/idle` 分开。跟踪失败时，先确定自己观察的是调用状态，还是会话状态；两者不是同一台状态机。[工具调用状态](https://github.com/anomalyco/opencode/blob/18ef3cc7c5a25b82114c953a80ccc09f4988f74e/packages/opencode/src/session/processor.ts#L216-L253) · [SessionStatus](https://github.com/anomalyco/opencode/blob/18ef3cc7c5a25b82114c953a80ccc09f4988f74e/packages/opencode/src/session/status.ts#L30-L48)

## 失败和停止路径不能省略

工具可能被拒绝、执行失败、超时或返回不可信结果；调用中断后可能留下尚未对账的状态。mini-SWE-agent 的格式错误反馈会进入下一轮，但连续错误达到阈值会退出；一般未捕获异常虽然也写 `exit` 消息，却会重新抛出。[格式错误与异常分支](https://github.com/SWE-agent/mini-swe-agent/blob/04d809ceab9df28f9adaed044884180159172930/src/minisweagent/agents/default.py#L100-L124) 这说明“结束”至少要分成正常交付、预算/限制停止、用户或宿主中断、异常失败几类，不能只画一条通往“完成”的箭头。

读真实项目时，先画**一条固定版本的正常路径**，再追一个失败分支；最后问有没有运行轨迹证明时序。以上三个案例仍是静态源码阅读，没有在本书中复现模型调用、命令执行或最终用户验收。
