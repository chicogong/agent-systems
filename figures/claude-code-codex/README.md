# 同一命令提案的关口：文字版

[返回对照正文](../../docs/comparisons/claude-code-codex.md) · [可编辑图源](scene.excalidraw) · [SVG](diagram.svg) · [PNG](preview.png)

图的问题是：**模型为了同一修复任务提出测试命令后，什么事件才让它真正运行？** 顶部注明共同的虚构修复任务；两条泳道从左到右均为“模型提出本地行动 → 产品的行动关口 → 获准后执行、返回并核对结果”。这是教学示意，不是实测事件记录；两行也不表示两个产品使用同名工具或内部模块。

上行依 [Claude Code 工作方式](https://code.claude.com/docs/en/how-claude-code-works)、[权限与沙箱交互](https://code.claude.com/docs/en/permissions#how-permissions-interact-with-sandboxing)的官方公开行为：有效权限规则、模式和沙箱设置共同影响是否询问；启用 `autoAllowBashIfSandboxed` 时，沙箱可替代部分整工具 Bash 询问，但显式 deny 和内容限定 ask 等规则仍适用。命令运行时，Bash 沙箱限制其及子进程的文件和网络访问。图未给出未公开的 harness 函数名，也未声称全部工具都经 Bash 沙箱。

下行依 [`openai/codex@c44deff7b1083e9660ac55d02122481f1cdf139b`](https://github.com/openai/codex/tree/c44deff7b1083e9660ac55d02122481f1cdf139b) 中普通 `exec_command` 的[参数处理](https://github.com/openai/codex/blob/c44deff7b1083e9660ac55d02122481f1cdf139b/codex-rs/core/src/tools/handlers/unified_exec/exec_command.rs#L170-L245)、[策略结果](https://github.com/openai/codex/blob/c44deff7b1083e9660ac55d02122481f1cdf139b/codex-rs/core/src/exec_policy.rs#L394-L460)及[审批与首次沙箱](https://github.com/openai/codex/blob/c44deff7b1083e9660ac55d02122481f1cdf139b/codex-rs/core/src/tools/orchestrator.rs#L151-L309)。`Forbidden` 会终止，`NeedsApproval` 需审批，`Skip` 只免普通审批；允许后仍要看沙箱选择。图把细分条件收在“关口”内，具体分支见[Codex 代码导读](../../docs/systems/codex/code-walkthrough.md)。

每行关口下的**虚线**是条件分支：权限拒绝意味着该次行动未获准；沙箱阻断可能发生在进程尝试访问资源之后，不能据此说进程从未启动。两者都应记录该行动未完成，而非沿实线写成执行成功。底部再提醒：命令运行但测试失败意味着有实际失败输出，仍不能把“提出命令”表述成“已验证修复”。结果可进入下一轮。图未展开 MCP 工单读取、Skill 加载、Codex 的 `apply_patch` 特殊路径、平台沙箱实现或有条件重试；这些在[正文](../../docs/comparisons/claude-code-codex.md)按各自证据说明。

**核验状态（2026-09-23）：** 图源按本目录 `build.py` 生成；本地 SVG/PNG 由同一图源导出，并检查了文字、箭头及边缘裁切。图源占用约 1008 × 730 场景单位，最小字号为 22；按 A4 正文宽 168 mm 等比放置，最小字约 10.4 pt，图高约 122 mm。正文与图为来源映射和教学推演，未经同环境运行验证，也未经独立读者验收。
