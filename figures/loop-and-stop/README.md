# 工具之后的四个决策点：文字版

[返回对照正文](../../docs/comparisons/loop-and-stop.md) · [图源](scene.excalidraw) · [SVG](diagram.svg) · [PNG](preview.png)

图按行读，不是四个项目串行执行的流程。每行先给出固定源码切面，再从“工具结果写回”走向该系统自己的控制闸口：

1. **Pi**：tool result 进入 `runLoop` 的消息路径。steering 等轮间，follow-up 等本来将结束时；`finishTurn=end` 可优先结束。
2. **mini-SWE-agent**：环境观察进入 `messages`；`DefaultAgent.run()` 在一轮保存后看最后消息，非 `exit` 再循环，`exit` 则返回其 `extra`。
3. **OpenCode**：流事件把结果写成 `ToolPart.completed/error`；`SessionProcessor` 的 `continue/stop/compact` 与外层 `runLoop` 才决定后续。图中的“流内 retry”指模型流处理器内按策略退避，**不是**与 `continue/stop/compact` 并列的返回值；调用级 `error` 本身也不等于重试。
4. **Kimi Code**：工具批次排空 `tool.result` 事件；`tool_use` 后 `runTurn()` 进入下一 step。活动 turn 收到的 steer 在 step 边界刷新；无继续请求、取消或上限可能结束当前 turn。

方框颜色仅帮助辨认四行，不表示性能或证据强弱。图省略了各项目的 provider、CLI、并行工具副作用和恢复路径；具体停止/拒绝分支及固定 SHA 见[正文表格](../../docs/comparisons/loop-and-stop.md)。四行均是 2026-09-23 核对的**固定源码静态切面**，不是一条实际运行轨迹。mini-SWE-agent 行特指基类加本地环境；Kimi Code 行限单个 turn；Pi 行含部分 coding-agent 外壳；OpenCode 行限 session 路径，因此证据粒度不等。
