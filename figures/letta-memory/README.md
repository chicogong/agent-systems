# 图的文字版：Letta Code local MemFS v1

本图回答“记忆存放的位置与当前上下文是什么关系”，不是 Letta 所有后端的完整架构图。源码固定于 [`letta-ai/letta-code@1f55d3dc`](https://github.com/letta-ai/letta-code/tree/1f55d3dc66e238d203757fae288bb53f3adc7cd3)。[回到章节](../../docs/systems/letta/README.md)

1. 左栏分列三种存放处：local MemFS v1 将 `system/` 下任意深度的 Markdown 识别为核心记忆块，包括子目录中的文件；这些块可承载身份、偏好、索引等内容。外部文件和 Skills 按需通过工具读取；对话历史与 recall 另列，不等同于这两类 Markdown。
2. 三条箭头指向本轮上下文的不同位置：核心块默认编入 system prompt；外部文件经工具读取后，内容成为本轮 conversation 的一部分，并非默认内联在 system prompt；近期对话和较早消息摘要在当前 conversation 中，更早信息可经 recall 检索。箭头表达设计中的可见路径，不表示每次都发生读取或检索。
3. 底部并列两条已读到的源码路径：`memory()` 工具写入后调用 `commitMemoryWrite`；memory worker 合并时先同步，再在能力允许时重编译提示。它们不是一条所有写入必经的流水线；已编译的当前回合提示也不会被文件编辑即时改写。

图中箭头表示设计路径，**不是实测调用轨迹**。绿色箭头不表示外部文件默认完整加载进 system prompt。API-backed MemFS v2 把核心文件放在根目录，并以 `MEMORY.md` 组织索引；本图不描述该布局。[格式分支源码](https://github.com/letta-ai/letta-code/blob/1f55d3dc66e238d203757fae288bb53f3adc7cd3/src/agent/memory-format.ts#L6-L29)

编辑 `build.py` 后运行 `python3 figures/letta-memory/build.py`，再用仓库说明的 Excalidraw renderer 从 `scene.excalidraw` 导出 `diagram.svg` 与 `preview.png`。交互式 MCP 画布可能更换字体，仓库导出图才是发布视觉基准。
