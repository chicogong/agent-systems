# 四种常被叫作“记忆”的状态

[返回横向对照](README.md) · [概念图：上下文与记忆](../concepts/context-vs-memory.md)

一个资料助手可以保存上次对话、记下你的回答偏好、检索旧资料，也可以记住任务做到哪一步。这些信息都对持续工作有用，但保存的对象和取用方式不同。下面用四条固定源码路径把它们分开。

| 路径 | 保存的主要对象 | 下一轮怎样用到 | 理解时抓住什么 |
| --- | --- | --- | --- |
| [聊天记录与分支：Pi](../systems/pi/README.md) | 消息与分支事件 | 从完整记录中选出当前分支，再整理成本轮模型输入 | 历史都保留，本轮使用当前分支中的内容。 |
| [常用信息与参考文件：Letta Code](../systems/letta/README.md) | 常用信息的 Markdown、参考文件和过去对话 | 常用信息编入提示；参考文件和过去对话按需查找 | 修改文件后，程序还要同步并更新提示。这里看本地文件记忆（local MemFS v1）。 |
| [可检索事实：Mem0](../systems/mem0/README.md) | 从消息提取、以后可以搜索的事实记录 | 应用查询后，选择要放回模型输入的内容 | 检索给出候选，应用负责选用。这里看开源版的同步路径。 |
| [任务进度快照：LangGraph](../systems/langgraph/README.md) | 任务执行到不同阶段的状态快照 | 选定任务、状态分组和快照版本，继续执行或从旧进度另走一条路 | 保存图执行进度，由快照存储组件（checkpointer）管理。 |

源码定位见各篇固定版本的[Pi 会话投影](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/coding-agent/src/core/session-manager.ts#L543-L582)、[Letta Code 记忆格式](https://github.com/letta-ai/letta-code/blob/1f55d3dc66e238d203757fae288bb53f3adc7cd3/src/agent/memory-format.ts#L6-L29)、[Mem0 检索候选](https://github.com/mem0ai/mem0/blob/f8082a7345dadd9e042ebbc40b57b1498c8f6d63/mem0/memory/main.py#L1628-L1726)、[LangGraph 快照类型](https://github.com/langchain-ai/langgraph/blob/bdb85b5aa87a21de68371d2e534b81aeed398f57/libs/langgraph/langgraph/types.py#L711-L733)。

把这张表用到新项目上，可以做一张小卡片：写明保存对象、保存位置、负责选择的程序、进入模型的时机，以及恢复入口。这样，“它有记忆”就变成了你能解释的一条具体路径。

本表解释源码中的用途，没有测过持久性、召回质量或跨会话效果。实际使用时，可再用同一条信息追踪“保存 → 取回 → 装入 → 回答”的过程。
