# Qwen Code 延迟工具桥：文字版

[返回剖面](../../docs/systems/qwen-code/README.md) · [图源](scene.excalidraw) · [SVG](diagram.svg) · [PNG](preview.png)

图分成三个连续片段。起点处，`ToolRegistry` 已注册目标工具，但 `getFunctionDeclarations()` 不把仍隐藏的 deferred schema 放进普通模型声明；模型保留可见的 `tool_search` 与 `tool_call` 桥。上方蓝色“发现”轨道是 `tool_search` 检索并把 `<functions>` schema 文本返回给模型；这只让模型读到参数形状，不执行目标，也不把目标加入函数声明。下方橙色“执行”轨道是模型发出 `tool_call {name, arguments}`，调度器解析成真实目标，检查上下文与目标策略后按真实工具继续执行。图中的两条轨道是教学整理，不表示源码里有两个独立线程。

图只针对**仍隐藏**的 deferred 工具。已预加载或被 reveal 的工具可直接出现在模型声明中；`CodeModeOnly` 则使用另一条声明机制。可见工具用 `tool_call` 包装会被拒绝，须直接调用。固定官方源码 [`b9840886b86c23f196482cc1ee55d59cbc74df87`](https://github.com/QwenLM/qwen-code/tree/b9840886b86c23f196482cc1ee55d59cbc74df87)，证据定位与未验证边界见[章节](../../docs/systems/qwen-code/README.md)。
