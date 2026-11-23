# Claude Code 与 Codex：同一修复任务如何执行与受控？

> Synthesized concept page maintained by Aimake LLM Wiki.

## Key Evidence & Provenance

### Source Snapshot (2026-11-22)
- **Origin**: `/Users/haorangong/Github/chicogong/experiments/agent-systems/docs/comparisons/claude-code-codex.md`
- **SHA-256**: `1faba243771f99bc` · Raw: [[../raw/2026-11-22-claude-code-与-codex-同一修复任务如何执行与受控.md|2026-11-22-claude-code-与-codex-同一修复任务如何执行与受控.md]]
- 很多开发者的终端里同时装着 `claude` 和 `codex`。日常修 Bug 时，你很容易遇到两桩让人困惑的事：
- 1. 明明在仓库根目录的 `CLAUDE.md` 或 `AGENTS.md` 里白纸黑字写着“可以随便跑单测，严禁运行 `git push`”，为什么跑 `npm test` 时有时还会弹窗求批准，而一旦放开自动批准，单靠那行 Markdown 又拦不住高危命令？
- 2. 明明开启了本地命令沙箱（Sandbox），以为一切写入都被关进了笼子，结果 Agent 调起工单系统的 MCP 工具时，一个请求就直接改掉了远端线上工单的状态。
- 问题出在我们把**提示词约定**、**工具审批**、**OS 进程沙箱**和**外部服务权限**混成了一道墙。实际上，无论是 Claude Code 还是 Codex，一次代码修复动作从“模型动念头”到“真正落到机器上”，都要穿过四道职责截然不同的控制关口。
- 可编辑图源 · PNG 预览 · 图的文字版
