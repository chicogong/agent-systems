# 跟着 Mem0 代码走一次写入和检索

[返回 Mem0 剖面](README.md) · 固定源码版本 [`f8082a73`](https://github.com/mem0ai/mem0/tree/f8082a7345dadd9e042ebbc40b57b1498c8f6d63)

本文只读 Python OSS 的同步 `Memory.add(infer=True)` 与默认不启用 `rerank` 的 `Memory.search`。下面的伪代码是**阅读顺序**，不是上游源码或运行轨迹。两次调用可以由应用连接，但 `search()` 的返回值不会自动进入某个 Agent 的下一轮模型输入。

```text
add(messages, user_id="u1", infer=True)
  → 校验作用域与消息 → 读取近期消息和已有记忆
  → LLM 提取事实 → embedding / hash 排重 → 尝试写向量与历史
  → 保存本轮消息 → 返回 {results: [] 或 [{event: "ADD", ...}]}

search(query, filters={"user_id": "u1"})
  → 校验查询与作用域 → 语义搜索建立候选集
  → 可用时计算关键词分数和实体加分 → 语义阈值 / 综合排序
  → 格式化 → 返回 {results: [...]}（也可能为空）
```

## 写入：消息与可检索事实是两种状态

1. `add()` 拒绝 OSS 不支持的 `timestamp`，经 `_build_filters_and_metadata` 要求 `user_id`、`agent_id`、`run_id` 至少一个，并将字符串或字典消息正规化为列表。`procedural_memory` 与 `infer=False` 不是下列路径。[入口与分支](https://github.com/mem0ai/mem0/blob/f8082a7345dadd9e042ebbc40b57b1498c8f6d63/mem0/memory/main.py#L817-L877) · [作用域校验](https://github.com/mem0ai/mem0/blob/f8082a7345dadd9e042ebbc40b57b1498c8f6d63/mem0/memory/main.py#L360-L404)
2. `_add_to_vector_store()` 读取同一会话作用域的最近消息，以新消息生成查询 embedding，最多取十条已有向量记忆，连同它们一起构造提取提示。这一步的已有记忆是提取时的参考，不是本轮准备覆盖的记录清单。[上下文采集](https://github.com/mem0ai/mem0/blob/f8082a7345dadd9e042ebbc40b57b1498c8f6d63/mem0/memory/main.py#L916-L953)
3. LLM 返回的事实解析为 `memory` 列表。调用失败会抛 `LLMError`；若返回空事实或无法解析出事实，则保存原消息并返回空列表。**消息已保存**不等于**产生了新的向量记忆**。[提取与空结果](https://github.com/mem0ai/mem0/blob/f8082a7345dadd9e042ebbc40b57b1498c8f6d63/mem0/memory/main.py#L955-L989)
4. 对提取出的文本生成 embedding；源码用文本 MD5 与刚检索到的记录及本批次比对，跳过重复或无法取得 embedding 的项。排重只针对这次读到的候选和批次，不能推断整个向量库已全局去重；若没有记录留下，同样保存消息并返回空列表。[embedding 与排重](https://github.com/mem0ai/mem0/blob/f8082a7345dadd9e042ebbc40b57b1498c8f6d63/mem0/memory/main.py#L991-L1043)
5. 有记录时先批量 `vector_store.insert`，失败后逐条尝试；随后写 ADD 历史、尝试关联实体，最后保存本轮消息。这里的 **ADD-only** 指此分支不自动更新或删除既有*记忆记录*；实体关联本身可更新其实体存储，显式 `update/delete` API 也另有路径。[向量写入与回退](https://github.com/mem0ai/mem0/blob/f8082a7345dadd9e042ebbc40b57b1498c8f6d63/mem0/memory/main.py#L1045-L1062) · [历史、实体与消息](https://github.com/mem0ai/mem0/blob/f8082a7345dadd9e042ebbc40b57b1498c8f6d63/mem0/memory/main.py#L1064-L1206)
6. 返回值 `{"results": ...}` 的每个 `ADD` 项按构造的 `records` 生成，而逐条回退中的插入异常仅被记录、没有从 `records` 移除。因此在故障条件下，**返回 ADD 不足以独立证明每个 ID 确已持久化**；这项风险是源码推断，尚需故障注入与向量库读回验证。[回退异常](https://github.com/mem0ai/mem0/blob/f8082a7345dadd9e042ebbc40b57b1498c8f6d63/mem0/memory/main.py#L1050-L1062) · [返回项构造](https://github.com/mem0ai/mem0/blob/f8082a7345dadd9e042ebbc40b57b1498c8f6d63/mem0/memory/main.py#L1192-L1206)

## 检索：谁入候选池，谁只能加分

1. `search()` 拒绝顶层传入的实体 ID，要求在 `filters` 中给出至少一个 `user_id`、`agent_id` 或 `run_id`，并检查 query、阈值和 `top_k`；不通过就不会进入向量检索。[参数校验](https://github.com/mem0ai/mem0/blob/f8082a7345dadd9e042ebbc40b57b1498c8f6d63/mem0/memory/main.py#L1432-L1461)
2. `_search_vector_store()` 对 query 做语义 embedding，并以超过请求 `top_k` 的内部数量取得语义结果；它也尝试关键词搜索和实体关联。这些是不同信号，但 `candidates` **只从语义结果构造**，并在默认情况下跳过已过期记录。[三种信号与候选池](https://github.com/mem0ai/mem0/blob/f8082a7345dadd9e042ebbc40b57b1498c8f6d63/mem0/memory/main.py#L1628-L1677)
3. `score_and_rank()` 先用**语义分数**过滤候选，再叠加可用的 BM25 分数与实体加分、按活跃信号归一化并取 `top_k`。仅被关键词命中、却未进入语义候选池的 ID 不会单独成为结果。[排序算法](https://github.com/mem0ai/mem0/blob/f8082a7345dadd9e042ebbc40b57b1498c8f6d63/mem0/utils/scoring.py#L60-L139)
4. 搜索结果被格式化为记忆对象；仅当调用方启用 `rerank`、配置了 reranker 且已有结果时，才再排序，失败则保留原结果。最终返回 `{"results": ...}`，是否将其注入模型提示由调用方决定，本篇源码并不展示该应用层步骤。[格式化与返回](https://github.com/mem0ai/mem0/blob/f8082a7345dadd9e042ebbc40b57b1498c8f6d63/mem0/memory/main.py#L1689-L1731) · [可选 rerank](https://github.com/mem0ai/mem0/blob/f8082a7345dadd9e042ebbc40b57b1498c8f6d63/mem0/memory/main.py#L1493-L1522)

这份导读没有运行模型、数据库或向量库。LLM 提取质量、适配器是否实现 `keyword_search()`、实体链接准确性、写入失败时返回值与实际存储的一致性，以及检索结果进入 Agent 上下文后的效果，仍需在固定配置下分别采集运行轨迹和读回结果。
