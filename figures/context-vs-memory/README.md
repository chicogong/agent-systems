# “存着”与“本轮看见”的文字版

[返回概念专题](../../docs/concepts/context-vs-memory.md) · [图源](scene.excalidraw) · [SVG](diagram.svg) · [PNG](preview.png)

可在此目录运行 `python3 build.py` 重建可编辑图源，再用 excalidraw-agent 渲染 SVG 与 PNG。

左侧四层是系统可能拥有的来源：会话记录、压缩摘要、长期记忆和外部知识。它们通过选择、引用或检索，才可能进入中间的上下文装配。右侧是一次模型请求实际可见的输入；它不自动等于左侧所有内容。虚线不表示每个系统都有该路径。具体 Pi 实例及源码边界见专题正文。
