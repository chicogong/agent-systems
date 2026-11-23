# 跟着 Qwen Code 看延迟工具怎样检索与脱壳执行

> Synthesized concept page maintained by Aimake LLM Wiki.

## Key Evidence & Provenance

### Source Snapshot (2026-11-22)
- **Origin**: `/Users/haorangong/Github/chicogong/experiments/agent-systems/docs/systems/qwen-code/code-walkthrough.md`
- **SHA-256**: `7ebff3327b211279` · Raw: [[../raw/2026-11-22-跟着-qwen-code-看延迟工具怎样检索与脱壳执行.md|2026-11-22-跟着-qwen-code-看延迟工具怎样检索与脱壳执行.md]]
- 读 Qwen Code 的延迟工具源码时，最容易混淆两个完全独立的状态：**模型在对话消息里读到了某工具的说明书**，以及**该工具出现在模型 API 的顶层原生声明列表里**。
- 看懂普通工具声明模式下这两件事是怎样分开处理的，就能彻底明白为什么搜索之后没有调 `revealDeferredTool`，以及为什么 `CoreToolScheduler` 必须在执行前拦截并改写 `tool_call`（至于预算内预加载、`visibleTools` 显式放行或 `CodeModeOnly` 分支，则走各自的直接路径）。
- 初始化：ToolRegistry.getFunctionDeclarations() → client.setTools()
- ├─ 隐藏的延迟工具（shouldDefer 且未显露）→ 从顶层原生声明中筛除
- └─ 常驻工具 + tool_search + tool_call     → 保留在模型原生声明列表中
