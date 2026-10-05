# 跟着 Qwen Code 看工具说明怎样找到、工具怎样调用

[返回首页](README.md) · 固定源码 [`b9840886`](https://github.com/QwenLM/qwen-code/tree/b9840886b86c23f196482cc1ee55d59cbc74df87)

模型要使用一个已注册、但暂时隐藏的工具，可以先请求说明，再交出名称和参数。程序负责找工具、检查条件，最后安排真实执行。下面沿普通工具声明模式的这条流程读源码。

已预加载、通过 `visibleTools` 显示或采用 `CodeModeOnly` 的工具，走其他分支。伪代码是流程摘要。

```text
setTools(): ToolRegistry.getFunctionDeclarations() → 给模型的初始工具清单
  仍隐藏的延迟工具暂时省略；已注册且可声明的 tool_search / tool_call 留在清单中

请求一：tool_search(query)
  搜索已注册且隐藏的延迟工具 → 返回 <functions>{工具说明}</functions>
  这一步返回说明，原有工具声明列表保持原样

请求二：tool_call({ name, arguments })
  CoreToolScheduler → resolveDeferredToolCall → 检查目标与使用条件
  包装请求换成真实工具名/参数 → 按真实工具的规则继续处理
```

## 工具清单先从注册表里筛选

`ToolRegistry.getFunctionDeclarations()` 准备模型可见的工具声明，默认省略仍隐藏的延迟工具。`client.setTools()` 用筛选后的声明设置模型可用的原生工具列表。[筛选声明](https://github.com/QwenLM/qwen-code/blob/b9840886b86c23f196482cc1ee55d59cbc74df87/packages/core/src/tools/tool-registry.ts#L835-L869) · [交给模型](https://github.com/QwenLM/qwen-code/blob/b9840886b86c23f196482cc1ee55d59cbc74df87/packages/core/src/core/client.ts#L1181-L1204)

## 搜索把名称、用途和参数交给模型

搜索入口 `ToolSearchTool` 自身保持可见。关键词查询从隐藏的延迟工具里找候选，`select:` 按名称精确查询，也可以重看已显示的工具。

`returnSchemas()` 返回 schema 文本，即工具名称、用途和参数结构。它负责交出说明，既没有执行目标工具，也没有调用 `revealDeferredTool` 把目标显示到原生声明列表中。[建立搜索入口](https://github.com/QwenLM/qwen-code/blob/b9840886b86c23f196482cc1ee55d59cbc74df87/packages/core/src/tools/tool-search.ts#L472-L513) · [找候选工具](https://github.com/QwenLM/qwen-code/blob/b9840886b86c23f196482cc1ee55d59cbc74df87/packages/core/src/tools/tool-search.ts#L258-L293) · [返回说明](https://github.com/QwenLM/qwen-code/blob/b9840886b86c23f196482cc1ee55d59cbc74df87/packages/core/src/tools/tool-search.ts#L295-L411)

## 调用请求先找到目标，再检查使用条件

模型用 `tool_call` 提交名称和参数后，`resolveDeferredToolCall()` 检查请求格式，找到真实工具，并核对它是否仍是隐藏的延迟工具、是否可声明，以及当前上下文是否排除了它。请求把搜索或调用入口套在自己里面时会被拒绝；缺少配套入口也会被拒绝。通过后，它返回目标工具对象和参数。[解析调用请求](https://github.com/QwenLM/qwen-code/blob/b9840886b86c23f196482cc1ee55d59cbc74df87/packages/core/src/tools/tool-call.ts#L60-L211)

`CoreToolScheduler` 是安排工具执行的调度器。它调用解析器，并检查这个 Agent 的允许/禁止工具清单（allowlist/blocklist），再把包装请求换成真实工具名和参数，进入目标工具的后续流程。权限按真实目标检查，通过后才继续执行。[检查并改写请求](https://github.com/QwenLM/qwen-code/blob/b9840886b86c23f196482cc1ee55d59cbc74df87/packages/core/src/core/coreToolScheduler.ts#L2645-L2729) · [安排后续处理](https://github.com/QwenLM/qwen-code/blob/b9840886b86c23f196482cc1ee55d59cbc74df87/packages/core/src/core/coreToolScheduler.ts#L2823-L2863)

读这段代码时，分别看“模型读到了说明”和“工具出现在原生声明列表”这两件事，就容易理解为什么还需要 `tool_call`。

本文尚未运行验证模型是否稳定地先搜索再调用，也未测量节省了多少模型输入单位（token）。它提供的是固定源码里的组织方法，效果需要用真实任务另外比较。
