# Codex：先决定许可，再选择沙箱运行

[返回 Codex 首篇](../../docs/systems/codex/README.md) · [图源](scene.excalidraw) · [原尺寸 SVG（手机可放大）](diagram.svg) · [PNG](preview.png)

让 Codex 运行项目测试时，模型先提出 `exec_command(cmd)`，主程序再检查并安排执行。沿第一行从左向右看：Handler 是接收请求的处理器，核对环境、参数和权限；exec policy 是执行策略，根据规则给出三种决定：

- `Skip`：跳过普通询问，继续检查执行环境。
- `NeedsApproval`：先请求批准，批准后才往下走；用户拒绝就停下。
- `Forbidden`：禁止这次执行，直接返回。

图中的“作出审批决定”就是这一步选择。三条折线表示三种不同决定；`NeedsApproval` 向下的“批准”箭头，只连接获准的请求。[审批结果处理](https://github.com/openai/codex/blob/c44deff7b1083e9660ac55d02122481f1cdf139b/codex-rs/core/src/tools/orchestrator.rs#L164-L221)

允许继续的请求交给 `ToolOrchestrator`（执行编排器），选择沙箱，再由 `UnifiedExecRuntime` 尝试运行。沙箱限制执行时能访问的文件、网络等资源。图中 `Skip` 下方的“仍按配置选执行范围”说明，跳过询问后，程序仍要选择访问范围。首次尝试成功，就返回命令输出或进程会话。

**沙箱拒绝时，再看下方条件分支。** 程序检查原因和重试策略：条件不满足就返回拒绝；符合条件时，可能还要追加审批，之后才进行第二次尝试。虚线画的是这种有条件的重试，普通命令报错另行处理。

本图依据 [`openai/codex@c44deff7b1083e9660ac55d02122481f1cdf139b`](https://github.com/openai/codex/tree/c44deff7b1083e9660ac55d02122481f1cdf139b) 的 Rust core 普通命令路径，尚未采集运行记录。`apply_patch` 专用处理、平台沙箱实现和网络审批细节留在图外；函数与停止条件可选读[关键代码路径](../../docs/systems/codex/code-walkthrough.md)。
