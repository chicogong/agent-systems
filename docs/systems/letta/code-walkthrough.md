# 跟着 Letta Code 看 local MemFS v1 的记忆可见性

[返回 Letta Code 首页](README.md) · 固定源码 [`1f55d3dc`](https://github.com/letta-ai/letta-code/tree/1f55d3dc66e238d203757fae288bb53f3adc7cd3)

下面是**阅读顺序**，不是一次运行实测，也不是所有编辑路径的同步调用栈。

1. 先看 [`detectMemoryFormat`](https://github.com/letta-ai/letta-code/blob/1f55d3dc66e238d203757fae288bb53f3adc7cd3/src/agent/memory-format.ts#L6-L15)：local MemFS 被判为 v1；只有非 local 且根目录存在 `MEMORY.md` 才判为 v2。本篇后续只跟 v1。
2. 再看 [`isCoreMemoryPath`](https://github.com/letta-ai/letta-code/blob/1f55d3dc66e238d203757fae288bb53f3adc7cd3/src/agent/memory-format.ts#L21-L29)：v1 以 `system/` 下的 Markdown 为核心块；“记忆目录里有文件”和“文件属于核心块”并非同义。
3. [`estimateSystemPromptSize`](https://github.com/letta-ai/letta-code/blob/1f55d3dc66e238d203757fae288bb53f3adc7cd3/src/agent/system-prompt-size.ts#L1-L106) 依格式统计核心范围，并给出粗略输入规模。它不是准确的模型 tokenizer，也不证明实际请求已带上每个字节。
4. [内置 local MemFS 提示](https://github.com/letta-ai/letta-code/blob/1f55d3dc66e238d203757fae288bb53f3adc7cd3/src/agent/prompts/letta_local_memfs.md#L8-L55) 将核心记忆、外部文件/Skills 与历史 recall 分成不同用途。这是系统对 Agent 的指引；实际读取仍须看工具轨迹，不能由提示文字推定。
5. [`memory()` 工具](https://github.com/letta-ai/letta-code/blob/1f55d3dc66e238d203757fae288bb53f3adc7cd3/src/tools/impl/memory.ts#L99-L157) 会解析和约束编辑路径，随后使用 [`commitMemoryWrite`](https://github.com/letta-ai/letta-code/blob/1f55d3dc66e238d203757fae288bb53f3adc7cd3/src/agent/memory-git.ts#L1319-L1358) 提交受影响路径。因此写入磁盘与完成持久化不能画成同一个瞬间。
6. 对于 [memory worker 合并路径](https://github.com/letta-ai/letta-code/blob/1f55d3dc66e238d203757fae288bb53f3adc7cd3/src/agent/subagents/memory-worker.ts#L95-L139)，同步之后才在允许时调用 [`recompileAgentSystemPrompt`](https://github.com/letta-ai/letta-code/blob/1f55d3dc66e238d203757fae288bb53f3adc7cd3/src/agent/modify.ts#L683-L729)。这解释了为何当前已经编译的提示不会因文件编辑而“即时变成新提示”；不能泛化到所有部署与路径。

若要把这条静态路径升级为运行结论，必须同时记录文件 revision、同步/重编译事件、下一次模型请求中实际包含的内容，以及 recall 调用。缺任何一层，最多只能说“已找到对应代码路径”。
