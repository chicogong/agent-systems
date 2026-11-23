# 代码走读：LangGraph 的 Checkpoint 如何落盘并派生新分支

> Synthesized concept page maintained by Aimake LLM Wiki.

## Key Evidence & Provenance

### Source Snapshot (2026-11-22)
- **Origin**: `/Users/haorangong/Github/chicogong/experiments/agent-systems/docs/systems/langgraph/code-walkthrough.md`
- **SHA-256**: `e65d8b2a426241b9` · Raw: [[../raw/2026-11-22-代码走读-langgraph-的-checkpoint-如何落盘并派生新分支.md|2026-11-22-代码走读-langgraph-的-checkpoint-如何落盘并派生新分支.md]]
- 本篇供希望深入源码的读者选读。我们沿着一个最简单的两节点图（`node_a` 已跑完、`node_b` 待执行），顺着 Python `Pregel` 引擎源码看清四件事：**启动时读哪一版快照、每走完一拍存什么、读取时怎样组装状态、改值分叉时怎样串起父子指针**。
- 先记住源码里的三个高频词：`Pregel` 是底层的图执行循环；`superstep`（超步）是一批就绪节点并发执行并把写入合并回通道的一拍；`saver`（即 checkpointer）是负责读写快照的存储后端（`InMemorySaver` 键结构 · `StateSnapshot` 字段定义）。
- 调用 `Pregel.invoke()` 时，底层统一委托给 `stream()`；同步路径会实例化 `SyncPregelLoop`，把配置的 `checkpointer` 与控制落盘时机的 `durability` 参数一并交进去（`invoke` 委托 `stream` · 构造循环）。
- 进入 `SyncPregelLoop.__enter__` 时，寻址逻辑非常清晰：
- - 若传入的 `config` 明确指定了 `checkpoint_id`，saver 就精确捞取那一个历史版本；
