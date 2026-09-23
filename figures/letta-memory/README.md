# 图的文字版：Letta Code local MemFS v1

本图回答“记忆存放的位置与当前上下文是什么关系”，不是 Letta 所有后端的完整架构图。源码固定于 [`letta-ai/letta-code@1f55d3dc`](https://github.com/letta-ai/letta-code/tree/1f55d3dc66e238d203757fae288bb53f3adc7cd3)。[回到章节](../../docs/systems/letta/README.md)

1. 左栏是较持久的状态：`system/*.md` 是本地 v1 的核心记忆；外部文件和 Skills 按需读取；对话历史与 recall 另列，不等同于这两类 Markdown。
2. 右栏是模型本轮可见的上下文：核心块编入 system prompt；外部文件经工具读取后，内容成为本轮消息的一部分；近期对话和旧消息摘要在当前 conversation 中，更早信息可经 recall 检索。
3. 底部时序条说明一次记忆修改不是即时提示变更：编辑文件、Git 提交、同步或重新编译是有先后和模式条件的步骤。

图中箭头表示设计路径，**不是实测调用轨迹**。绿色箭头不表示外部文件默认完整加载进 system prompt。API-backed MemFS v2 把核心文件放在根目录，并以 `MEMORY.md` 组织索引；本图不描述该布局。[格式分支源码](https://github.com/letta-ai/letta-code/blob/1f55d3dc66e238d203757fae288bb53f3adc7cd3/src/agent/memory-format.ts#L6-L29)

编辑 `build.py` 后运行 `python3 figures/letta-memory/build.py`，再用仓库说明的 Excalidraw renderer 从 `scene.excalidraw` 导出 `diagram.svg` 与 `preview.png`。交互式 MCP 画布可能更换字体，仓库导出图才是发布视觉基准。
