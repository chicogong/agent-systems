# 图的文字版：Mem0 同步检索漏斗

图回答“多信号检索是不是三路召回并集”，范围为 [`mem0ai/mem0@f8082a73`](https://github.com/mem0ai/mem0/tree/f8082a7345dadd9e042ebbc40b57b1498c8f6d63) 的 Python OSS `Memory.search()` 路径。[返回章节](../../docs/systems/mem0/README.md)

1. `query` 带作用域 filters 进入检索。语义向量搜索产生候选列表，这是后续排序的输入集合。
2. 同一个 query 还尝试关键词搜索和实体匹配。图内的“可用时”与“命中时”表示这两支可能没有分数；它们产生的是候选 ID 对应的分数或加分，而不是独立追加到候选集合的记录。关键词命中不能单独进入候选池。
3. `score_and_rank` 先按语义分数阈值淘汰候选，再叠加可用的 BM25 与实体加分，排序取 `top_k`。
4. 写入侧不在图内展开：`add(infer=True)` 的消息经 LLM 提取事实、hash 去重，最终 `insert` 到向量库。写入详细路径在正文。

这是源码路径示意而非实测轨迹。`keyword_search` 基类默认返回 `None`，所以图中的橙色分数支路是**可用时**参与；实体分支也可能没有命中。托管平台实现、异步 API 和其他向量库适配器不在本图范围内。

编辑 `build.py` 后运行 `python3 figures/mem0-retrieval/build.py`，再由 `excalidraw-agent` renderer 从 `scene.excalidraw` 导出 SVG 和 PNG。
