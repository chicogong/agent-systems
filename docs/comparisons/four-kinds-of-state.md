# 四种常被叫作“记忆”的状态

[返回横向对照](README.md) · [概念图：上下文与记忆](../concepts/context-vs-memory.md)

“Agent 有记忆”可能指完全不同的能力。下表只对照本书已完成的四条固定源码路径；它们的用途不同，不能排成一个“谁记得更好”的榜单。

| 路径 | 保存的主要对象 | 下一轮怎样用到 | 最容易误称为 |
| --- | --- | --- | --- |
| [Pi session tree](../systems/pi/README.md) | 消息与分支事件 | 当前分支经投影与上下文转换进入模型请求 | “整个历史都在上下文里” |
| [Letta Code local MemFS v1](../systems/letta/README.md) | 核心块 Markdown、外部文件及可 recall 历史 | 核心块编入提示；外部材料/旧历史按需读取 | “文件一写完本轮模型立即知道” |
| [Mem0 OSS 同步路径](../systems/mem0/README.md) | 从消息提取的可检索事实记录 | 应用查询后还须决定是否、如何放回模型输入 | “向量库会自动成为模型上下文” |
| [LangGraph checkpointer](../systems/langgraph/README.md) | 图执行的版本化 checkpoint | 按 thread / namespace / checkpoint 选状态或从旧版本分叉 | “用户偏好语义记忆” |

这些区别来自各篇固定版本的[Pi 会话投影](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/coding-agent/src/core/session-manager.ts#L543-L582)、[Letta Code 记忆格式](https://github.com/letta-ai/letta-code/blob/1f55d3dc66e238d203757fae288bb53f3adc7cd3/src/agent/memory-format.ts#L6-L29)、[Mem0 检索候选](https://github.com/mem0ai/mem0/blob/f8082a7345dadd9e042ebbc40b57b1498c8f6d63/mem0/memory/main.py#L1628-L1726)、[LangGraph 快照类型](https://github.com/langchain-ai/langgraph/blob/bdb85b5aa87a21de68371d2e534b81aeed398f57/libs/langgraph/langgraph/types.py#L711-L733)。这是**静态源码语义对照**，不是持久性、召回质量或跨会话效果的实测。

读一个新 Agent 时，先写出“保存了什么、在哪里、由谁选择、哪一轮可见、失败时怎样恢复”。若这五个问题尚无答案，就先说“有某种状态存储”，不要笼统称为长期记忆。
