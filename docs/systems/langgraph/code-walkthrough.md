# 代码走读：LangGraph 的 Checkpoint 如何落盘并派生新分支

[返回 LangGraph 剖面](README.md)

本篇供希望深入源码的读者选读。我们沿着一个最简单的两节点图（`node_a` 已跑完、`node_b` 待执行），顺着 Python `Pregel` 引擎源码看清四件事：**启动时读哪一版快照、每走完一拍存什么、读取时怎样组装状态、改值分叉时怎样串起父子指针**。

先记住源码里的三个高频词：`Pregel` 是底层的图执行循环；`superstep`（超步）是一批就绪节点并发执行并把写入合并回通道的一拍；`saver`（即 checkpointer）是负责读写快照的存储后端（[`InMemorySaver` 键结构](https://github.com/langchain-ai/langgraph/blob/bdb85b5aa87a21de68371d2e534b81aeed398f57/libs/checkpoint/langgraph/checkpoint/memory/__init__.py#L68-L83) · [`StateSnapshot` 字段定义](https://github.com/langchain-ai/langgraph/blob/bdb85b5aa87a21de68371d2e534b81aeed398f57/libs/langgraph/langgraph/types.py#L711-L729)）。

## 1. 启动入口：这一轮从哪份快照起步？

调用 `Pregel.invoke()` 时，底层统一委托给 `stream()`；同步路径会实例化 `SyncPregelLoop`，把配置的 `checkpointer` 与控制落盘时机的 `durability` 参数一并交进去（[`invoke` 委托 `stream`](https://github.com/langchain-ai/langgraph/blob/bdb85b5aa87a21de68371d2e534b81aeed398f57/libs/langgraph/langgraph/pregel/main.py#L3836-L3915) · [构造循环](https://github.com/langchain-ai/langgraph/blob/bdb85b5aa87a21de68371d2e534b81aeed398f57/libs/langgraph/langgraph/pregel/main.py#L2899-L2920)）。

进入 `SyncPregelLoop.__enter__` 时，寻址逻辑非常清晰：

- 若传入的 `config` 明确指定了 `checkpoint_id`，saver 就精确捞取那一个历史版本；
- 若只传了 `thread_id`（日常续跑最常见的情况），saver 就取该线程与命名空间下的最新快照；
- 若是全新线程，则用空快照初始化第 0 拍（[`SyncPregelLoop.__enter__`](https://github.com/langchain-ai/langgraph/blob/bdb85b5aa87a21de68371d2e534b81aeed398f57/libs/langgraph/langgraph/pregel/_loop.py#L1629-L1696) · [`InMemorySaver.get_tuple`](https://github.com/langchain-ai/langgraph/blob/bdb85b5aa87a21de68371d2e534b81aeed398f57/libs/checkpoint/langgraph/checkpoint/memory/__init__.py#L230-L309)）。

## 2. 拍末落盘：一个 Superstep 跑完后写下什么？

每一拍分前后两半：`tick` 先根据当前 checkpoint、尚未合并的 `pending writes` 与图拓扑挑出本拍要跑的节点任务；等节点执行完毕，`after_tick` 把各节点的输出应用到状态通道（channels），清空本拍已消费的 pending writes，随即调用 `_put_checkpoint({"source": "loop"})` 生成新快照（[`tick` 准备任务](https://github.com/langchain-ai/langgraph/blob/bdb85b5aa87a21de68371d2e534b81aeed398f57/libs/langgraph/langgraph/pregel/_loop.py#L599-L629) · [`after_tick` 合并与落盘](https://github.com/langchain-ai/langgraph/blob/bdb85b5aa87a21de68371d2e534b81aeed398f57/libs/langgraph/langgraph/pregel/_loop.py#L683-L724)）。

这里有一个很实用的性能与可靠性权衡开关——`durability`：

- `async`（默认）：后台异步提交快照，不阻塞下一拍节点启动，吞吐更快但极端崩溃时可能少最后一拍；
- `sync`：严格等当前快照写进存储后才迈出下一拍，用延迟换强恢复点；
- `exit`：中间过程不落盘，直到整张图退出或中断时才一次性保存（[`_put_checkpoint` 实现](https://github.com/langchain-ai/langgraph/blob/bdb85b5aa87a21de68371d2e534b81aeed398f57/libs/langgraph/langgraph/pregel/_loop.py#L1133-L1216) · [写入顺序串行化](https://github.com/langchain-ai/langgraph/blob/bdb85b5aa87a21de68371d2e534b81aeed398f57/libs/langgraph/langgraph/pregel/_loop.py#L1530-L1547) · [`durability` 模式说明](https://github.com/langchain-ai/langgraph/blob/bdb85b5aa87a21de68371d2e534b81aeed398f57/libs/langgraph/langgraph/pregel/main.py#L2705-L2711)）。

在 `InMemorySaver.put` 内部，新快照按 `(thread_id, checkpoint_ns, checkpoint_id)` 三级字典归档，同时把入参 `config` 里的旧 `checkpoint_id` 记作 `parent_checkpoint_id`，通道具体值则按版本分存进 `blobs` 表——这就是分支树父子链表的物理落点（[`InMemorySaver.put`](https://github.com/langchain-ai/langgraph/blob/bdb85b5aa87a21de68371d2e534b81aeed398f57/libs/checkpoint/langgraph/checkpoint/memory/__init__.py#L421-L465)）。

## 3. 状态还原：如何把底层存储组装成 `StateSnapshot`？

当你调用 `get_state(config)` 或 `get_state_history(config)` 时，引擎并不是把原始字典原样扔给你，而是经过 `_prepare_state_snapshot` 还原现场：结合通道值与未完成的 `pending writes` 算出当前可见的 `values`，再推演出下一拍应当触发的 `next` 节点与 `tasks` 详情，连同 `config` 和 `parent_config` 一起打包返回（[单版本读取](https://github.com/langchain-ai/langgraph/blob/bdb85b5aa87a21de68371d2e534b81aeed398f57/libs/langgraph/langgraph/pregel/main.py#L1392-L1434) · [历史列表读取](https://github.com/langchain-ai/langgraph/blob/bdb85b5aa87a21de68371d2e534b81aeed398f57/libs/langgraph/langgraph/pregel/main.py#L1480-L1531) · [组装 `StateSnapshot`](https://github.com/langchain-ai/langgraph/blob/bdb85b5aa87a21de68371d2e534b81aeed398f57/libs/langgraph/langgraph/pregel/main.py#L1145-L1265)）。

## 4. 改值分叉：`update_state` 怎样长出新树枝？

把历史某一拍的 `snapshot.config` 传给 `update_state(config, values, as_node=...)`，内部会走完一条干净的“写时复制（Copy-on-Write）”链条：

```text
update_state(old_config, new_values, as_node?)
  → bulk_update_state 读取 old_config 对应的旧 checkpoint 并拷贝副本
  → 找到对应节点的 flat_writers（若存在多节点歧义则要求显式传 as_node）
  → 按通道 reducer 规则把 new_values 合并进副本
  → saver.put 保存为全新 checkpoint_id（parent 指向 old_config）
  → 返回新分支的 fork_config
```

随后执行 `invoke(None, fork_config)`，循环就会加载这条新分支的 checkpoint 往下跑；如果没调 `update_state` 而是直接指定历史 `checkpoint_id` 重放，循环内也预留了创建 `source="fork"` 快照的分支，防止重放撞上中断时污染旧记录（[`update_state` 入口](https://github.com/langchain-ai/langgraph/blob/bdb85b5aa87a21de68371d2e534b81aeed398f57/libs/langgraph/langgraph/pregel/main.py#L2515-L2526) · [读取与拷贝旧版](https://github.com/langchain-ai/langgraph/blob/bdb85b5aa87a21de68371d2e534b81aeed398f57/libs/langgraph/langgraph/pregel/main.py#L1640-L1675) · [节点写入与 `as_node` 校验](https://github.com/langchain-ai/langgraph/blob/bdb85b5aa87a21de68371d2e534b81aeed398f57/libs/langgraph/langgraph/pregel/main.py#L1905-L1999) · [落盘新版本](https://github.com/langchain-ai/langgraph/blob/bdb85b5aa87a21de68371d2e534b81aeed398f57/libs/langgraph/langgraph/pregel/main.py#L2000-L2047) · [加载指定 ID](https://github.com/langchain-ai/langgraph/blob/bdb85b5aa87a21de68371d2e534b81aeed398f57/libs/langgraph/langgraph/pregel/_loop.py#L1629-L1654) · [重放建分支](https://github.com/langchain-ai/langgraph/blob/bdb85b5aa87a21de68371d2e534b81aeed398f57/libs/langgraph/langgraph/pregel/_loop.py#L945-L971) · [官方分叉测试断言](https://github.com/langchain-ai/langgraph/blob/bdb85b5aa87a21de68371d2e534b81aeed398f57/libs/langgraph/tests/test_time_travel.py#L143-L218)）。

## 5. 恢复时的外部边界核查

读完这条链路就能看清：saver 存下的只有图内 `values`、`pending writes` 和版本指针。凡是节点里包含发请求、改数据库、扣费等外部动作，重放或分叉前都必须在业务工具层核对动作 ID 与幂等状态，避免“图状态回到了昨天，外部接口却被重复调了两次”（[快照字段范围](https://github.com/langchain-ai/langgraph/blob/bdb85b5aa87a21de68371d2e534b81aeed398f57/libs/langgraph/langgraph/types.py#L711-L729) · [`InMemorySaver` 存储字段](https://github.com/langchain-ai/langgraph/blob/bdb85b5aa87a21de68371d2e534b81aeed398f57/libs/checkpoint/langgraph/checkpoint/memory/__init__.py#L68-L83) · [`pending writes` 恢复参与调度](https://github.com/langchain-ai/langgraph/blob/bdb85b5aa87a21de68371d2e534b81aeed398f57/libs/langgraph/langgraph/pregel/_loop.py#L611-L629) · [`InMemorySaver` 调试用途说明](https://github.com/langchain-ai/langgraph/blob/bdb85b5aa87a21de68371d2e534b81aeed398f57/libs/checkpoint/langgraph/checkpoint/memory/__init__.py#L33-L44)）。

## 来源与边界

本篇基于 [`langchain-ai/langgraph@bdb85b5aa87a21de68371d2e534b81aeed398f57`](https://github.com/langchain-ai/langgraph/tree/bdb85b5aa87a21de68371d2e534b81aeed398f57) 的 Python `Pregel` 同步循环与 `InMemorySaver` 静态核对；异步 `AsyncPregelLoop`、Postgres 等持久化后端的并发锁与跨进程恢复行为需按对应模块另行验证。
