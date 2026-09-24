# Codex 命令执行决策图：文字版

[返回 Codex 首篇](../../docs/systems/codex/README.md) · [图源](scene.excalidraw) · [原尺寸 SVG（手机可放大）](diagram.svg) · [PNG](preview.png)

从左到右看第一行：模型提交 `exec_command(cmd)`；Handler 验证环境、参数与权限；exec policy 产出三种决策。`Forbidden` 在执行前终止，`NeedsApproval` 要求审核并可能被拒绝，`Skip` 不要求普通审批，但不等于无沙箱。允许继续的请求汇合到沙箱选择与第一次执行；这里的路径是 `ToolOrchestrator → UnifiedExecRuntime`。第一次执行成功直接返回输出或进程会话；若出现沙箱拒绝，还须检查具体重试条件。不满足条件时返回拒绝；满足条件时可能追加审批，再进行第二次尝试。图中虚线表示**有条件**而非必经路径。网络审批、平台后端和 `apply_patch` 拦截不在图内展开。

本图只映射 [`openai/codex@c44deff7b1083e9660ac55d02122481f1cdf139b`](https://github.com/openai/codex/tree/c44deff7b1083e9660ac55d02122481f1cdf139b) 的 Rust core 局部源码。代码路径及停止条件详见[关键代码路径](../../docs/systems/codex/code-walkthrough.md)。它不是运行轨迹；不包含 `apply_patch` 拦截分支、平台沙箱实现和网络审批细节。
