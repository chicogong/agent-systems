# 图的文字版：从旧进度试另一条路

[返回章节](../../docs/systems/langgraph/README.md) · [打开原尺寸 SVG](diagram.svg) · [PNG 预览](preview.png)

任务已经做过一遍，你想从中途改一个条件，再试一次。LangGraph 可以找到当时保存的进度，写出新版本，再沿新版本继续。图中的 `thread` 表示同一任务的进度记录，`checkpoint` 是某一步保存的状态快照。

## 先看原来的路线，再看新分支

- **上面是原路线 C₀ → C₁ → C₂。** C₁ 记录了节点 B 还待执行，图中用 `next: B` 表示。B 执行后保存 C₂，留下原结果。
- **下面从 C₁ 改一个条件。** 选中 C₁ 的 `config`（定位这一版进度的配置），调用 `update_state` 更新 `x`，写出新版本 C₁′。
- **从新版本继续执行。** 用返回的配置调用 `invoke(None, fork_config)`，节点 B 在新分支执行，得到 C₂′。原来的 C₂ 仍保留，便于对照两次结果。

图只挑出理解分叉需要的几个快照，实际执行可能保存更多版本。

## 怎样选中要继续的那一版

`thread_id` 选择任务，`checkpoint_ns` 限定读取范围，`checkpoint_id` 再指定具体快照。图中的 `get_state_history(T)` 用于查看该任务的历史；`StateSnapshot.parent_config` 指向当前版本直接接续的上一版。

本文的 `InMemorySaver` 是内存存储示例。给出 `checkpoint_id` 时，`get_state` 读取对应快照；省略它时，则取同一范围中 ID 最大的快照。想沿某条分支继续时，应先选出那条分支的配置，再调用后续操作。

## 保存进度时，还要分清两件事

任务进度保存在图的状态中，发邮件、写远端记录等动作发生在外部服务。恢复旧快照后，外部服务仍保留真实结果，需要另外核对已发生的动作。

实际需要跨进程保留进度时，也要选择合适的存储后端并测试恢复。官方将 `InMemorySaver` 限定为测试和调试用途；这里用它说明版本标识与父版本记录。

图对应 [`langchain-ai/langgraph@bdb85b5a`](https://github.com/langchain-ai/langgraph/tree/bdb85b5aa87a21de68371d2e534b81aeed398f57) 的 Python checkpointer（快照保存与读取组件）源码路径，运行与存储验证范围见正文。

编辑 `build.py` 后运行 `python3 figures/langgraph-checkpoints/build.py`，再由 `excalidraw-agent` renderer 从 `scene.excalidraw` 导出 SVG 和 PNG。
