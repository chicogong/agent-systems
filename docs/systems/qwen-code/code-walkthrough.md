# 跟着 Qwen Code 的延迟工具桥走两次调用

[返回剖面](README.md) · 固定源码 [`b9840886`](https://github.com/QwenLM/qwen-code/tree/b9840886b86c23f196482cc1ee55d59cbc74df87)

以下是逻辑摘要，不是复制源码。它限定在普通 function-declaration 模式中一个仍隐藏的 deferred 目标；已预加载、`visibleTools`、`CodeModeOnly` 等情况另走分支。

```text
setTools(): ToolRegistry.getFunctionDeclarations() → 初始模型声明
  hidden deferred 目标不在声明列表；tool_search 与 tool_call 留在列表

请求一：tool_search(query)
  检索已注册且隐藏的 deferred 工具 → 返回 <functions>{schema}</functions>
  不调用目标；不因此 reveal 目标

请求二：tool_call({ name, arguments })
  CoreToolScheduler → resolveDeferredToolCall → 检查目标与上下文
  wrapper 改写为真实工具名/参数 → 后续按真实目标调度
```

1. `ToolRegistry.getFunctionDeclarations()` 默认排除仍隐藏的 deferred 工具；`client.setTools()` 用过滤后的声明集更新模型可见工具。[声明过滤](https://github.com/QwenLM/qwen-code/blob/b9840886b86c23f196482cc1ee55d59cbc74df87/packages/core/src/tools/tool-registry.ts#L835-L869) · [setTools](https://github.com/QwenLM/qwen-code/blob/b9840886b86c23f196482cc1ee55d59cbc74df87/packages/core/src/core/client.ts#L1181-L1204)
2. `ToolSearchTool` 自身保持可见；关键词查询只遍历隐藏 deferred 候选，`select:` 则可精确重看可见工具。处理返回的是 schema 文本。源码的 `returnSchemas()` 没有调用 `revealDeferredTool` 或执行目标；`tool_search` 的返回文本也不等于模型函数声明刷新。[工具构造](https://github.com/QwenLM/qwen-code/blob/b9840886b86c23f196482cc1ee55d59cbc74df87/packages/core/src/tools/tool-search.ts#L472-L513) · [候选](https://github.com/QwenLM/qwen-code/blob/b9840886b86c23f196482cc1ee55d59cbc74df87/packages/core/src/tools/tool-search.ts#L258-L293) · [返回](https://github.com/QwenLM/qwen-code/blob/b9840886b86c23f196482cc1ee55d59cbc74df87/packages/core/src/tools/tool-search.ts#L295-L411)
3. `resolveDeferredToolCall()` 校验 `tool_call` wrapper、规范目标名、拒绝桥自身嵌套、要求目标仍是隐藏 deferred，并检查子 Agent 排除规则和声明能力。桥缺半边时也拒绝。它返回的是**目标工具对象与参数**，不是自己执行目标。[解析](https://github.com/QwenLM/qwen-code/blob/b9840886b86c23f196482cc1ee55d59cbc74df87/packages/core/src/tools/tool-call.ts#L60-L211)
4. `CoreToolScheduler` 在调度前调用解析器，再用目标工具名替换 wrapper；它也检查该 Agent 的目标工具 allowlist/blocklist。因此 `tool_call` 包装并不是绕开目标权限的捷径。[调度改写](https://github.com/QwenLM/qwen-code/blob/b9840886b86c23f196482cc1ee55d59cbc74df87/packages/core/src/core/coreToolScheduler.ts#L2645-L2729) · [调度入口](https://github.com/QwenLM/qwen-code/blob/b9840886b86c23f196482cc1ee55d59cbc74df87/packages/core/src/core/coreToolScheduler.ts#L2823-L2863)

注意：schema 在 `tool_search` 的回复里可读，与目标出现在模型原生工具声明中是两种不同的可见性。本文没有量化节约多少 token，也没有实测模型是否稳定遵循“先搜索再调用”；不把源码注释里的设计意图当成效果指标。
