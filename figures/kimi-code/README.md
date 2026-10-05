# Kimi Code steer 缓冲图：文字版

[返回系统篇](../../docs/systems/kimi-code/README.md) · [可编辑图源](scene.excalidraw) · [SVG](diagram.svg) · [PNG](preview.png)

Agent 正在跑测试，你补充“先解释失败原因”。图讲的是这条新要求先在哪里等、何时交给模型。turn（回合）是一条输入展开的整段工作，step（步骤）是其中的一轮；steer 表示途中补充或纠正指令。

上半部从左向右，是忙时收下新要求的过程：

1. `steer(input)` 发现回合正在运行，把新要求放进 `steerBuffer`（输入等待区），沿用当前回合。
2. 下一步开始前，`beforeStep` 按收到的顺序取出这些输入，追加为用户消息。
3. `executeLoopStep` 构造该步骤的模型消息，再发起请求。模型到这时才有机会依据新要求继续。

图中“缓冲不取消正在运行的 step”说明，当前模型请求或工具仍按原步骤进行；新要求等下一步处理。工具什么时候返回，会影响这次等待多久。[收下输入](https://github.com/MoonshotAI/kimi-code/blob/75a894e9ad5e8d49509664b3daaa1bbc9bb39432/packages/agent-core/src/agent/turn/index.ts#L130-L143) · [取出等待输入](https://github.com/MoonshotAI/kimi-code/blob/75a894e9ad5e8d49509664b3daaa1bbc9bb39432/packages/agent-core/src/agent/turn/index.ts#L595-L604) · [准备模型请求](https://github.com/MoonshotAI/kimi-code/blob/75a894e9ad5e8d49509664b3daaa1bbc9bb39432/packages/agent-core/src/loop/turn-step.ts#L64-L78)

下半部是原本准备结束时的检查。模型一步结束、没有提出工具调用（非 `tool_use`）时，`runTurn` 先调用 `shouldContinueAfterStop`，再看是否收尾。这个回调先取出 steer 输入：有输入就继续下一步；没有输入，还会检查目标结果（goal outcome）和结束前回调 `Stop` hook，再决定继续或结束。图里“无”的箭头通向的就是这组后续检查。[结束前检查](https://github.com/MoonshotAI/kimi-code/blob/75a894e9ad5e8d49509664b3daaa1bbc9bb39432/packages/agent-core/src/loop/run-turn.ts#L99-L128) · [检查次序](https://github.com/MoonshotAI/kimi-code/blob/75a894e9ad5e8d49509664b3daaa1bbc9bb39432/packages/agent-core/src/agent/turn/index.ts#L611-L657)

底部“仍可终止 turn”提醒：取消、最大步数或异常可能让回合先结束，等待区里的输入就可能没有机会交给下一次模型请求。收下输入和实际继续一步，要分别观察。[步数与中断](https://github.com/MoonshotAI/kimi-code/blob/75a894e9ad5e8d49509664b3daaa1bbc9bb39432/packages/agent-core/src/loop/run-turn.ts#L74-L128)

本图依据[上游固定版本](https://github.com/MoonshotAI/kimi-code/tree/75a894e9ad5e8d49509664b3daaa1bbc9bb39432)的源码整理，未采集真实任务的完整运行记录。命令行输入入口、工具审批、会话保存、目标跨回合驱动和子 Agent 留在图外；想进一步定位函数，可选读[代码导读](../../docs/systems/kimi-code/code-walkthrough.md)。
