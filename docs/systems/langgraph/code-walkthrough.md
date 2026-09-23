# 代码走读：checkpoint 如何变成一条新分支

[返回 LangGraph 剖面](README.md)

> 范围：静态阅读 [`langchain-ai/langgraph@bdb85b5aa87a21de68371d2e534b81aeed398f57`](https://github.com/langchain-ai/langgraph/tree/bdb85b5aa87a21de68371d2e534b81aeed398f57) 的 Python `Pregel`、同步执行循环与 `InMemorySaver`。以下是**固定版本的源码路径**，不是本文的运行观察；异步路径、生产 saver 的事务保证和外部服务均未实测。

设想一个两节点图：第一个节点已经产生状态，第二个节点尚待运行。我们想回到这时的状态，改一个值，再沿新状态继续。关键不是“把整个会话倒带”，而是用 `thread_id`、`checkpoint_ns`、`checkpoint_id` 找到一个图状态版本，并从它生成新的版本。[`InMemorySaver` 的键结构](https://github.com/langchain-ai/langgraph/blob/bdb85b5aa87a21de68371d2e534b81aeed398f57/libs/checkpoint/langgraph/checkpoint/memory/__init__.py#L68-L83) · [`StateSnapshot` 的字段](https://github.com/langchain-ai/langgraph/blob/bdb85b5aa87a21de68371d2e534b81aeed398f57/libs/langgraph/langgraph/types.py#L711-L729)

## 入口：执行先读哪个版本？

`Pregel.invoke` 通过 `stream` 执行；同步 `stream` 构造 `SyncPregelLoop`，把所选 checkpointer 和 `durability` 交给循环。[`invoke` 调用 `stream`](https://github.com/langchain-ai/langgraph/blob/bdb85b5aa87a21de68371d2e534b81aeed398f57/libs/langgraph/langgraph/pregel/main.py#L3836-L3915) · [循环构造](https://github.com/langchain-ai/langgraph/blob/bdb85b5aa87a21de68371d2e534b81aeed398f57/libs/langgraph/langgraph/pregel/main.py#L2899-L2920)

循环进入时，如果 config 指定 `checkpoint_id`，就要求 saver 取这个版本；通常不指定时，则取该 thread/namespace 的最新版本。没有已存版本时，循环以空 checkpoint 起步。在这里，“恢复”首先是**选择要加载的图状态**，还不是把之前执行过的外部动作撤销。[`SyncPregelLoop.__enter__`](https://github.com/langchain-ai/langgraph/blob/bdb85b5aa87a21de68371d2e534b81aeed398f57/libs/langgraph/langgraph/pregel/_loop.py#L1629-L1696) · [`InMemorySaver.get_tuple` 的精确/最新选择](https://github.com/langchain-ai/langgraph/blob/bdb85b5aa87a21de68371d2e534b81aeed398f57/libs/checkpoint/langgraph/checkpoint/memory/__init__.py#L230-L309)

## 写入：一个 superstep 后保存什么？

`tick` 从 checkpoint、pending writes、图节点等准备下一批任务；任务完成后，`after_tick` 把任务写入应用到 channels，清理本轮 pending writes，并调用 `_put_checkpoint({"source": "loop"})`。这解释了 checkpoint 与图执行步骤的关系：它记录的是**状态及其可继续调度所需的信息**，不是一个普通聊天消息列表。[任务准备](https://github.com/langchain-ai/langgraph/blob/bdb85b5aa87a21de68371d2e534b81aeed398f57/libs/langgraph/langgraph/pregel/_loop.py#L599-L629) · [合并写入并创建 checkpoint](https://github.com/langchain-ai/langgraph/blob/bdb85b5aa87a21de68371d2e534b81aeed398f57/libs/langgraph/langgraph/pregel/_loop.py#L683-L724)

`_put_checkpoint` 创建 checkpoint、更新 `checkpoint_config` 中的 ID，并将保存任务交给 checkpointer；保存任务等待前一次保存，以维持交付顺序。注意**“生成新状态”与“已落盘”不能混为一谈**：这个版本的 `durability` 默认为 `async`；`sync` 在下一步前同步持久化，`exit` 则只在图退出时持久化。`exit` 模式下不能假定每个中间 superstep 都有可读的持久 checkpoint。[创建与提交](https://github.com/langchain-ai/langgraph/blob/bdb85b5aa87a21de68371d2e534b81aeed398f57/libs/langgraph/langgraph/pregel/_loop.py#L1133-L1216) · [提交排序](https://github.com/langchain-ai/langgraph/blob/bdb85b5aa87a21de68371d2e534b81aeed398f57/libs/langgraph/langgraph/pregel/_loop.py#L1530-L1547) · [`durability` 说明](https://github.com/langchain-ai/langgraph/blob/bdb85b5aa87a21de68371d2e534b81aeed398f57/libs/langgraph/langgraph/pregel/main.py#L2705-L2711)

以 `InMemorySaver` 为例，`put` 按 thread → namespace → checkpoint ID 保存记录，并把传入 config 的旧 `checkpoint_id` 记为 parent，返回指向新 ID 的 config；channel 值另按版本保存在 blobs 中。这是本篇“新分支”图的存储依据，但不是生产数据库的事务性证明。[`InMemorySaver.put`](https://github.com/langchain-ai/langgraph/blob/bdb85b5aa87a21de68371d2e534b81aeed398f57/libs/checkpoint/langgraph/checkpoint/memory/__init__.py#L421-L465)

## 读取：历史快照不是原样取出的一包 JSON

`get_state(config)` 交给 saver 的 `get_tuple`；`get_state_history(config)` 遍历 saver 的 `list`。两者把保存的 checkpoint 准备成 `StateSnapshot`：根据 channels 和 pending writes 计算 `values`、待执行的 `next` 与 `tasks`，并附上 `config`、`parent_config`。因此读者看到的快照是**从保存结构重建的图状态视图**；特别是读取最新状态与指定旧 ID 时，pending writes 的应用条件不同。[单版本读取](https://github.com/langchain-ai/langgraph/blob/bdb85b5aa87a21de68371d2e534b81aeed398f57/libs/langgraph/langgraph/pregel/main.py#L1392-L1434) · [历史读取](https://github.com/langchain-ai/langgraph/blob/bdb85b5aa87a21de68371d2e534b81aeed398f57/libs/langgraph/langgraph/pregel/main.py#L1480-L1531) · [快照准备](https://github.com/langchain-ai/langgraph/blob/bdb85b5aa87a21de68371d2e534b81aeed398f57/libs/langgraph/langgraph/pregel/main.py#L1145-L1265)

## 分支：旧快照如何接上新运行？

把旧 `snapshot.config` 交给 `update_state(config, values, as_node=...)`。入口转入 `bulk_update_state`，按该 config 读取 checkpoint 并复制它；更新逻辑会调用所选节点的 `flat_writers`、应用写入，再调用 saver 的 `put` 保存**新 checkpoint**，返回它的 config。若不能唯一判定 `as_node`，代码会要求显式指定；这不是把任意字典直接覆盖到旧快照上。[更新入口](https://github.com/langchain-ai/langgraph/blob/bdb85b5aa87a21de68371d2e534b81aeed398f57/libs/langgraph/langgraph/pregel/main.py#L2515-L2526) · [读旧版并复制](https://github.com/langchain-ai/langgraph/blob/bdb85b5aa87a21de68371d2e534b81aeed398f57/libs/langgraph/langgraph/pregel/main.py#L1640-L1675) · [节点写入与歧义检查](https://github.com/langchain-ai/langgraph/blob/bdb85b5aa87a21de68371d2e534b81aeed398f57/libs/langgraph/langgraph/pregel/main.py#L1905-L1999) · [保存新版](https://github.com/langchain-ai/langgraph/blob/bdb85b5aa87a21de68371d2e534b81aeed398f57/libs/langgraph/langgraph/pregel/main.py#L2000-L2047)

随后以返回的新 config 继续 `invoke(None, config)`，循环加载这条分支的 checkpoint，并从其可调度状态继续。官方仓库的 time-travel 测试正是用“取旧快照 → `update_state` → `invoke(None, fork_config)`”检查分叉，并另测同一旧快照产生两条分支；这里引用的是**测试断言**，不是本文运行结果。没有先调用 `update_state` 而直接从旧 ID 重放时，循环还有创建 `source="fork"` checkpoint 的路径，避免重放遇到中断却没有新分支版本。[加载指定 ID](https://github.com/langchain-ai/langgraph/blob/bdb85b5aa87a21de68371d2e534b81aeed398f57/libs/langgraph/langgraph/pregel/_loop.py#L1629-L1654) · [重放时建分支](https://github.com/langchain-ai/langgraph/blob/bdb85b5aa87a21de68371d2e534b81aeed398f57/libs/langgraph/langgraph/pregel/_loop.py#L945-L971) · [分叉测试](https://github.com/langchain-ai/langgraph/blob/bdb85b5aa87a21de68371d2e534b81aeed398f57/libs/langgraph/tests/test_time_travel.py#L143-L218)

## 边界：图恢复不等于外部副作用回滚

**工程推断：**`StateSnapshot` 的字段描述图状态、下一批任务和父版本；`InMemorySaver.put` 保存 checkpoint/channel 版本，并没有为任意 HTTP 请求、邮件发送或支付动作提供逆操作。若重放经过有外部副作用的节点，是否再次执行、是否重复生效，取决于节点逻辑、pending writes、幂等键及外部系统；不能从“成功取回旧快照”推导出“世界也恢复到旧时刻”。[快照字段](https://github.com/langchain-ai/langgraph/blob/bdb85b5aa87a21de68371d2e534b81aeed398f57/libs/langgraph/langgraph/types.py#L711-L729) · [存储字段](https://github.com/langchain-ai/langgraph/blob/bdb85b5aa87a21de68371d2e534b81aeed398f57/libs/checkpoint/langgraph/checkpoint/memory/__init__.py#L68-L83) · [pending writes 参与任务准备](https://github.com/langchain-ai/langgraph/blob/bdb85b5aa87a21de68371d2e534b81aeed398f57/libs/langgraph/langgraph/pregel/_loop.py#L611-L629)

**未知与待测：**`InMemorySaver` 官方注释限定其用于调试/测试；本文没有验证 Postgres 等生产 saver 的事务、故障恢复与跨进程行为，也没有构造含外部副作用的复现实验。下一步测试应同时记录 checkpoint 的 `config`/`parent_config`、节点执行次数和外部系统的动作 ID，分开判定图状态与现实动作。[saver 用途限定](https://github.com/langchain-ai/langgraph/blob/bdb85b5aa87a21de68371d2e534b81aeed398f57/libs/checkpoint/langgraph/checkpoint/memory/__init__.py#L33-L44)
