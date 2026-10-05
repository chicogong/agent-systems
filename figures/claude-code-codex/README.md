# 同一条测试命令怎样运行：文字版

[返回对照正文](../../docs/comparisons/claude-code-codex.md) · [可编辑图源](scene.excalidraw) · [SVG](diagram.svg) · [PNG](preview.png)

给两个助手同一个虚构修复任务，模型都建议运行测试。两行从左到右看：提出命令、检查是否允许、运行命令、拿到输出并核对结果。中间方框分别说明许可与执行环境的安排，两个产品的具体实现各有条件。

**上行看 Claude Code。** 权限规则、使用模式和沙箱设置共同决定怎样询问用户。启用 `autoAllowBashIfSandboxed` 时，一部分 Bash 工具调用可在沙箱中自动放行；明确禁止的 deny 规则和针对命令内容的 ask 规则仍适用。命令在 Bash 沙箱里运行时，进程与子进程的文件和网络访问受到限制。具体说明见 [Claude Code 工作方式](https://code.claude.com/docs/en/how-claude-code-works)和[权限与沙箱交互](https://code.claude.com/docs/en/permissions#how-permissions-interact-with-sandboxing)。

**下行看 Codex 的普通命令路径。** `Forbidden` 是禁止执行，`NeedsApproval` 是需要确认，`Skip` 是免去普通确认。获准后，再选择执行沙箱。图把细分条件放在中间方框，想深入可读[Codex 代码导读](../../docs/systems/codex/code-walkthrough.md)。

每行下面的虚线画出没有顺利完成的情况。许可拒绝时，动作还没获准；沙箱阻断也可能发生在进程已经尝试访问资源之后，需要保留实际错误。测试命令运行但测试失败时，把失败输出送回下一轮，继续修复。说明结果时，分别写清建议了什么、实际运行了什么、测试通过了哪些项目。

## 阅读范围

Claude Code 这一行依据官方公开行为，未公开的运行器函数保持未知；Bash 沙箱的说明只覆盖对应工具。Codex 这一行只看普通 `exec_command`。MCP 工单读取、Skill 加载、`apply_patch` 特殊处理、平台沙箱和条件重试，见[正文](../../docs/comparisons/claude-code-codex.md)的分别说明。两行用于对照文档与固定源码，尚未做同环境运行比较。

Codex 来源是 [`openai/codex@c44deff7b1083e9660ac55d02122481f1cdf139b`](https://github.com/openai/codex/tree/c44deff7b1083e9660ac55d02122481f1cdf139b) 的[参数处理](https://github.com/openai/codex/blob/c44deff7b1083e9660ac55d02122481f1cdf139b/codex-rs/core/src/tools/handlers/unified_exec/exec_command.rs#L170-L245)、[策略结果](https://github.com/openai/codex/blob/c44deff7b1083e9660ac55d02122481f1cdf139b/codex-rs/core/src/exec_policy.rs#L394-L460)和[审批与首次沙箱](https://github.com/openai/codex/blob/c44deff7b1083e9660ac55d02122481f1cdf139b/codex-rs/core/src/tools/orchestrator.rs#L151-L309)。

图源由本目录 `build.py` 生成，SVG/PNG 从同一图源导出。按 A4 正文宽 168 mm 放置时，最小字约 10.4 pt；最终阅读效果仍需检查实际 PDF 和读者试读。
