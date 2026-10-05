# 图的文字版：Letta Code 怎样取用记忆

[回到章节](../../docs/systems/letta/README.md)

维护项目时，助手经常需要知道你的偏好，偶尔需要翻一份长手册，有时还要找回以前的对话。图左边把这三类材料分开存放，右边说明它们怎样进入这次模型输入。

## 从左到右看三条路

- **常用信息随系统提示带上。** 本图采用 local MemFS v1，即本地的一种记忆目录配置。`system/` 下的 Markdown 文件，包括子目录里的文件，都属于核心记忆块，可以保存身份、偏好或索引。准备请求时，这些块默认编入 `system prompt`（系统提示），与基础指令一起交给模型。
- **长文件需要时再读。** 外部文件和 Skills（工作方法）由工具按需读取。工具返回的正文放进 `conversation`（本次对话消息）里；系统提示中默认只放核心块，不会把所有参考文件都塞进去。图中的绿色箭头表示这条读取路径。
- **过去的对话按远近取用。** 近期消息和较早消息的摘要可以放进当前对话消息；更早的细节通过 `recall`（历史检索）找回。这里保存的是对话记录，另有自己的查找办法。

图右边的“本轮交给模型的材料”，就是最终交给模型的系统提示和对话消息。箭头列出可能使用的路径，具体一次任务会读取哪些材料，要看实际调用。

## 改了笔记之后，何时能用上

图底部并排画了两种更新方式：

1. 用 `memory()` 工具编辑记忆后，`commitMemoryWrite` 为修改形成 Git 提交。
2. `memory worker`（专门整理记忆的执行者）合并改动时，先同步文件，再在支持这项能力时重新编译系统提示。

阅读更新结果时，分别查看文件、Git 版本、同步和提示重建。两条路径各有自己的入口；已经准备好的当前回合提示，仍保留准备时的内容，等对应的更新步骤完成后再使用新内容。

## 本图对应的配置

源码固定于 [`letta-ai/letta-code@1f55d3dc`](https://github.com/letta-ai/letta-code/tree/1f55d3dc66e238d203757fae288bb53f3adc7cd3)，图依据源码和内置提示说明流程，尚未追踪实际运行。另一种 API-backed MemFS v2 配置把核心文件放在根目录，并以 `MEMORY.md` 组织索引；读那种配置时，要换用它的目录规则。[格式分支源码](https://github.com/letta-ai/letta-code/blob/1f55d3dc66e238d203757fae288bb53f3adc7cd3/src/agent/memory-format.ts#L6-L29)

编辑 `build.py` 后运行 `python3 figures/letta-memory/build.py`，再用仓库说明的 Excalidraw renderer 从 `scene.excalidraw` 导出 `diagram.svg` 与 `preview.png`。交互式 MCP 画布可能更换字体，仓库导出图是发布视觉基准。
