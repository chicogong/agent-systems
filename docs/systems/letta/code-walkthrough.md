# 跟着 Letta Code 看 local MemFS v1 的记忆可见性

[返回 Letta Code 首页](README.md) · 固定源码 [`1f55d3dc`](https://github.com/letta-ai/letta-code/tree/1f55d3dc66e238d203757fae288bb53f3adc7cd3)

这是可选的源码路线。把自己想保存的项目偏好放在脑中，沿“选目录—估容量—编辑—同步—重新准备提示”读下去。下面讲的是代码如何安排这些步骤；运行结果要另外观察。

1. 先看 [`detectMemoryFormat`](https://github.com/letta-ai/letta-code/blob/1f55d3dc66e238d203757fae288bb53f3adc7cd3/src/agent/memory-format.ts#L6-L15)：local MemFS 被判为 v1；只有非 local 且根目录存在 `MEMORY.md` 才判为 v2。本篇后续只跟 v1。
2. 再看 [`isCoreMemoryPath`](https://github.com/letta-ai/letta-code/blob/1f55d3dc66e238d203757fae288bb53f3adc7cd3/src/agent/memory-format.ts#L21-L29)：v1 以 `system/` 下的 Markdown 为核心块；目录决定文件的用途：放在这里的核心块会参加系统提示准备，详细参考资料另走读取路径。
3. [`estimateSystemPromptSize`](https://github.com/letta-ai/letta-code/blob/1f55d3dc66e238d203757fae288bb53f3adc7cd3/src/agent/system-prompt-size.ts#L1-L106) 依格式统计核心范围，并给出粗略输入规模。这里的估算按字节粗略换算，准确 token 数需使用对应模型的分词器；请求内容则到模型调用处查看。
4. [内置 local MemFS 提示](https://github.com/letta-ai/letta-code/blob/1f55d3dc66e238d203757fae288bb53f3adc7cd3/src/agent/prompts/letta_local_memfs.md#L8-L55) 将核心记忆、外部文件/Skills 与历史 recall 分成不同用途。提示告诉 Agent 何时查哪类材料；查看工具记录，可以看到一次任务实际读到了什么。
5. [`memory()` 工具](https://github.com/letta-ai/letta-code/blob/1f55d3dc66e238d203757fae288bb53f3adc7cd3/src/tools/impl/memory.ts#L99-L157) 会解析和约束编辑路径，随后使用 [`commitMemoryWrite`](https://github.com/letta-ai/letta-code/blob/1f55d3dc66e238d203757fae288bb53f3adc7cd3/src/agent/memory-git.ts#L1319-L1358) 为受影响路径形成 Git 版本。记下文件变化、Git 版本、同步和重编译四个位置，就能逐步追踪一条新记忆怎样送到下一次请求。
6. 对于 [memory worker 合并路径](https://github.com/letta-ai/letta-code/blob/1f55d3dc66e238d203757fae288bb53f3adc7cd3/src/agent/subagents/memory-worker.ts#L95-L139)，同步之后才在允许时调用 [`recompileAgentSystemPrompt`](https://github.com/letta-ai/letta-code/blob/1f55d3dc66e238d203757fae288bb53f3adc7cd3/src/agent/modify.ts#L683-L729)。这条路径在同步后重新准备提示，已经开始的回合仍可使用先前准备的内容。其他配置与工具路径，分别从自己的入口追踪。

自己验证时，记录文件 revision（版本）、同步与重编译事件，再查看下一次模型请求包含什么、recall 查到了什么。本文尚未运行这组验证；这些观察点是从代码安排中整理出的检查路线。
