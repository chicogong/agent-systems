# 代码导读：追踪 Letta Code local MemFS v1 的记忆生效链路

> Synthesized concept page maintained by Aimake LLM Wiki.

## Key Evidence & Provenance

### Source Snapshot (2026-11-22)
- **Origin**: `/Users/haorangong/Github/chicogong/experiments/agent-systems/docs/systems/letta/code-walkthrough.md`
- **SHA-256**: `dede1587db8e0e67` · Raw: [[../raw/2026-11-22-代码导读-追踪-letta-code-local-memfs-v1-的记忆生效链路.md|2026-11-22-代码导读-追踪-letta-code-local-memfs-v1-的记忆生效链路.md]]
- 你在对话里嘱咐编码助手：“以后汇报排查结果时，先给三行结论，再贴文件路径。”助手调用记忆工具把这条规则写进了 `system/style.md`，但在当前回合接下来的几步工具调用里，它的系统提示并没有立刻刷新——直到同步与提示重编译完成，后续请求才真正带上这条新规矩。
- 为什么一条新记忆从“写进磁盘”到“出现在系统提示”要跨越多步？下面沿着 `letta-code` 的源码调用链，按**目录契约判定 → 容量预算 → 落盘与 Git 留痕 → 同步与重编译**的顺序走一遍。
- 打开 `detectMemoryFormat` 可以看到第一道分流：只要 `localMemfs` 为真，代码直接返回 `"v1"`；只有非本地模式且根目录下存在 `MEMORY.md` 时，才会返回 `"v2"`。
- 紧接着，`isCoreMemoryPath` 把目录结构翻译成“是否常驻系统提示”的布尔判断：在 `v1` 模式下，只有位于 `system/` 目录下的 `.md` 文件才返回 `true`。这意味着在 local MemFS v1 中，路径本身就是架构指令——放进 `system/style.md` 就会参与系统提示组装，而放进 `docs/runboo
- 既然 `system/` 下的所有 Markdown 都会常驻系统提示，一旦失控堆积就会挤压任务正文的上下文空间。`estimateSystemPromptSize` 复用同一套 `v1 / v2` 路径规则，递归扫描 `system/` 目录下的核心文件字节数，并按 `bytes / 4` 粗略折算 token 消耗：
