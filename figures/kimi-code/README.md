# Kimi Code steer 缓冲图：文字版

[返回系统篇](../../docs/systems/kimi-code/README.md) · [可编辑图源](scene.excalidraw) · [SVG](diagram.svg) · [PNG](preview.png)

本图只回答：**进行中的 turn 接到 steer 后，模型何时可能看到它？** 上半部从左到右：`steer(input)` 在有活动 turn 时，把新输入写入 `steerBuffer`，不在该调用里创建新 turn；下一个 `beforeStep` 把缓冲按序追加为 user message，之后 `executeLoopStep` 构建模型消息并发起该 step。蓝色与绿色实线表示这条源码可见的控制顺序，并不表示等待时间固定。[`steer` 与缓冲](https://github.com/MoonshotAI/kimi-code/blob/75a894e9ad5e8d49509664b3daaa1bbc9bb39432/packages/agent-core/src/agent/turn/index.ts#L130-L143) · [`beforeStep`](https://github.com/MoonshotAI/kimi-code/blob/75a894e9ad5e8d49509664b3daaa1bbc9bb39432/packages/agent-core/src/agent/turn/index.ts#L595-L604) · [`executeLoopStep` 的次序](https://github.com/MoonshotAI/kimi-code/blob/75a894e9ad5e8d49509664b3daaa1bbc9bb39432/packages/agent-core/src/loop/turn-step.ts#L64-L78)

下半部从左到右：若模型完成一步且没有 `tool_use`，`runTurn` 在结束前调用 `shouldContinueAfterStop`；该回调先刷新 steer 缓冲。有新输入则继续下一 step；没有则还要检查 goal outcome、`Stop` hook，之后才可能结束。紫、绿、红箭头均为控制分支；“无”不是必然直接结束。[`runTurn` 停止钩子](https://github.com/MoonshotAI/kimi-code/blob/75a894e9ad5e8d49509664b3daaa1bbc9bb39432/packages/agent-core/src/loop/run-turn.ts#L99-L128) · [Kimi Code 的优先序](https://github.com/MoonshotAI/kimi-code/blob/75a894e9ad5e8d49509664b3daaa1bbc9bb39432/packages/agent-core/src/agent/turn/index.ts#L611-L657)

图边界：取消、最大步数或异常都可能终止当前 turn；它没有描绘 CLI 输入路径、工具审批细节、会话持久化、goal 跨 turn 驱动或子 Agent。依据为固定提交的**静态源码阅读**，无运行轨迹。[上游固定版本](https://github.com/MoonshotAI/kimi-code/tree/75a894e9ad5e8d49509664b3daaa1bbc9bb39432) · [步数与中断](https://github.com/MoonshotAI/kimi-code/blob/75a894e9ad5e8d49509664b3daaa1bbc9bb39432/packages/agent-core/src/loop/run-turn.ts#L74-L128)

图内为印刷可读性压短了两处提示：“缓冲不取消正在运行的 step”涵盖当前模型请求或工具；底部“仍可终止 turn”表示缓冲输入**不保证**一定进入一次后续模型请求。具体条件以上述正文和[代码导读](../../docs/systems/kimi-code/code-walkthrough.md)为准。
