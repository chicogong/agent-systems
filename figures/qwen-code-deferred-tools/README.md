# Qwen Code 延迟工具桥：文字版

[返回讲解](../../docs/systems/qwen-code/README.md) · [图源](scene.excalidraw) · [SVG](diagram.svg) · [PNG](preview.png)

工具很多时，Qwen Code 先给模型一份精简清单，需要某个工具时再取完整说明。图上方的 `ToolRegistry` 是程序保存工具的注册表；“deferred”指已注册、但暂时从模型声明清单里隐藏的工具。

图采用普通工具声明模式，**搜索与调用两个入口均已注册且可声明**。这就是副标题中的“双桥”条件。`getFunctionDeclarations()` 准备模型的工具清单，暂时省略仍隐藏的目标，但保留可用的 `tool_search`、`tool_call`；图中的 eager 指直接列出的工具。

**蓝色轨道：把说明找出来。** 模型用 `tool_search(query)` 提交查询，注册表筛选目标，把 schema（名称、用途和参数结构）放进 `<functions>` 文本交回模型。模型拿到这份说明后，才知道怎样填参数。

**橙色轨道：提出调用，再由程序安排执行。** 模型发出 `tool_call {name, arguments}`，写明工具名和参数。`resolveDeferredToolCall` 找到目标，检查它与当前上下文是否符合条件。调度器 `CoreToolScheduler` 再把这层包装换成真实工具请求，按目标工具的权限与执行规则继续；检查通过后才执行。

图中两个“≠”分别提醒：程序里注册的工具多于模型此次声明清单；搜索返回的说明文本也与原生工具声明分开。搜索只交回说明，目标调用要另发请求。模型若已经知道名称和参数，也可能直接尝试调用，程序仍须检查条件。这两条轨道按用途分开画，实际由同一套工具流程处理。

已预加载或已显示（reveal）的工具，可以直接列进模型声明；它们应直接调用，用 `tool_call` 包装会被拒绝。`CodeModeOnly` 模式采用另一套声明流程，留在图外。

本图依据固定官方源码 [`b9840886b86c23f196482cc1ee55d59cbc74df87`](https://github.com/QwenLM/qwen-code/tree/b9840886b86c23f196482cc1ee55d59cbc74df87)，只讲仍隐藏的延迟工具，尚未运行真实调用。函数位置和研究范围见[章节](../../docs/systems/qwen-code/README.md)。
