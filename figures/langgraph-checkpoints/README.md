# 图的文字版：一个 thread 的版本树

范围是 [`langchain-ai/langgraph@bdb85b5a`](https://github.com/langchain-ai/langgraph/tree/bdb85b5aa87a21de68371d2e534b81aeed398f57) 的 Python checkpointer 路径。[返回章节](../../docs/systems/langgraph/README.md)

[打开原尺寸 SVG](diagram.svg) · [PNG 预览](preview.png)。手机上可打开 SVG 放大查看节点和箭头。

1. 上支用 C₀ → C₁ → C₂ 示意一个 thread 的原始执行。C₁ 是 `next` 包含节点 B 的历史快照；C₂ 是原分支执行后的快照。
2. 选取 C₁ 的 `config` 调用 `update_state`，会产生新版本 C₁′。以返回的 config 再 `invoke(None, ...)`，产生新分支后继 C₂′。原 C₂ 仍是历史版本。
3. `thread_id` 和 `checkpoint_ns` 定位作用域；加 `checkpoint_id` 可选具体快照。就图中引用的 `InMemorySaver` 而言，不给 `checkpoint_id` 时，`get_state` 取该作用域下最大 checkpoint ID；这不等于按分支语义选择某个“当前版本”。`StateSnapshot.parent_config` 用于追踪直接父版本。
4. 图只绘制理解分叉所需的关键节点；真正执行可能写出更多 checkpoint。图没有描述 external tool 副作用回滚，也没有证明所有 saver 可跨进程持久化。

`InMemorySaver` 仅用于说明代码可见的键结构和父版本记录；官方注释限定它用于测试/调试。编辑 `build.py` 后运行 `python3 figures/langgraph-checkpoints/build.py`，再由 `excalidraw-agent` renderer 从 `scene.excalidraw` 导出 SVG 和 PNG。
