# 会话变长以后：保存记录、压缩内容、取回记忆

[返回机制目录](README.md) · [先读：上下文与记忆](context-vs-memory.md) · [四类状态对照](../comparisons/four-kinds-of-state.md)

你和助手连续准备了几次读书会：先确定场地，再整理材料，最后讨论分享顺序。聊天越来越长，程序需要安排下一轮带上哪些内容。重要约定可以单独保存；较早的讨论可以概括；执行到一半的任务也可以保存进度。

这几种办法解决的事情不同。下面用 Pi、Letta Code、Mem0 和 LangGraph 的例子说明，它们是不同项目，不是一套已经接好的系统。

## 四种保存方法怎样使用

| 方法 | 留下的内容 | 后续怎样使用 |
| --- | --- | --- |
| 会话记录 | 原始消息、工具结果和相关事件 | 选择当前对话分支，整理成下一轮消息 |
| 压缩摘要 | 较早讨论的概括，以及保留的近期内容 | 用摘要和近期片段组成较短输入 |
| 长期记忆 | 跨任务有用的事实、约定或资料 | 放入固定提示，或按需要搜索和读取 |
| 检查点 | 程序执行到某一步的状态 | 找到保存位置，继续或调整任务 |

比如“地点在图书馆二楼”可以出现在原聊天里，也可以写入单独的活动资料。下一轮需要它时，程序必须把相关内容交给模型。可以用[上下文与记忆](context-vs-memory.md)中的“打开几份文件”来理解这一步。

## Pi：从当前聊天分支选出消息

Pi 的 coding-agent 用一棵会话树保存记录。每条记录有自己的 `id` 和指向上一条的 `parentId`；当前叶子，也就是 leaf，表示这次正在继续的分支。

准备模型输入时，`buildContextEntries()` 沿当前分支取记录。如果其中有压缩记录，就把摘要放到前面，再从 `firstKeptEntryId` 指定的记录开始，保留后续片段。`buildSessionProjection()` 将这些记录整理成消息，`buildSessionContext()` 返回消息列表。

[会话树](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/coding-agent/src/core/session-manager.ts#L976-L985) · [当前分支与消息整理](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/coding-agent/src/core/session-manager.ts#L468-L582)

这里的 projection，可以理解为“从已保存的记录中，整理出这次要用的一份内容”。

## Pi：把早期讨论缩成摘要

会话接近模型输入上限时，`shouldCompact()` 检查长度和预留量。`prepareCompaction()` 选择较早的内容用于概括，保留近期片段，并带上已有摘要。生成后，`appendCompaction()` 将新的压缩记录追加到会话里。

下一次输入可以用摘要代替早期长消息，原记录仍可用于回看。摘要占的空间较少，但它可能遗漏细节。例如摘要只写“已确定场地”，之后又要回答具体楼层时，就需要找回原材料。

[触发条件](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/coding-agent/src/core/compaction/compaction.ts#L286-L292) · [选取内容](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/coding-agent/src/core/compaction/compaction.ts#L894-L955) · [追加压缩记录](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/coding-agent/src/core/session-manager.ts#L1258-L1285)

Pi 也支持手动 `/compact`。另外，`/tree` 切换分支时可以生成分支摘要；这是另一个触发场景。[固定版本说明](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/coding-agent/docs/compaction.md#L14-L23)

以上会话树和压缩功能来自 pi-coding-agent。进入模型调用前，agent-core 还可以通过 `transformContext` 调整消息，再用 `convertToLlm` 转成模型接口接受的格式。使用其他 Pi 宿主时，需要查看它自己的消息安排。[模型调用前的处理](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/agent/src/agent-loop.ts#L376-L406)

## Letta Code：固定记忆与按需资料分开

Letta Code 的 local MemFS v1 把 `system/` 下的 Markdown 文件识别为核心记忆块，供程序编入提示。其他资料和 Skills 可以按需要读取；较早的对话可以通过 recall 查找，recall 就是找回历史记录。

适合经常使用的约定，可以放在核心块里。内容较长、只在某类任务里需要的资料，可以留在外部文件。

文件修改后，当前已编译的提示要等后续重新编译才会更新。这个过程可以理解为：先改资料，再重新整理模型将读取的那份输入。

[记忆文件类型](https://github.com/letta-ai/letta-code/blob/1f55d3dc66e238d203757fae288bb53f3adc7cd3/src/agent/memory-format.ts#L6-L29) · [内置提示对读取时机的说明](https://github.com/letta-ai/letta-code/blob/1f55d3dc66e238d203757fae288bb53f3adc7cd3/src/agent/prompts/letta_local_memfs.md#L8-L46)

## Mem0：存入事实，再搜索需要的内容

本书核对的 Mem0 Python OSS 同步路径，提供给应用调用的存取接口。`Memory.add(infer=True)` 从消息里提取候选事实并处理写入；`Memory.search(query, filters=...)` 按查询和范围寻找相关记录。

得到搜索结果后，应用选择合适内容，核对来源，再放进模型输入。比如下一次安排活动时，检索“场地约定”，把命中的内容交给助手参考。

[写入入口](https://github.com/mem0ai/mem0/blob/f8082a7345dadd9e042ebbc40b57b1498c8f6d63/mem0/memory/main.py#L760-L932) · [提取事实与写入](https://github.com/mem0ai/mem0/blob/f8082a7345dadd9e042ebbc40b57b1498c8f6d63/mem0/memory/main.py#L940-L1067) · [检索与范围](https://github.com/mem0ai/mem0/blob/f8082a7345dadd9e042ebbc40b57b1498c8f6d63/mem0/memory/main.py#L1379-L1456)

`infer=False`、procedural memory、异步接口和托管服务有其他处理路径。想了解它们，可以继续查看项目对应实现。

## LangGraph：保存执行进度

LangGraph 的 `StateSnapshot` 保存当前 `values`、下一步 `next`、版本配置 `config` 和上一个版本的 `parent_config` 等内容。应用可以找到某一步的图状态，回看或继续执行。

这很像保存一个处理流程的进度：已经整理了哪些材料，下一步准备做什么。消息是否放在状态里，由应用决定。需要按含义搜索长期知识时，应用仍要安排相应的存取逻辑。

[快照字段](https://github.com/langchain-ai/langgraph/blob/bdb85b5aa87a21de68371d2e534b81aeed398f57/libs/langgraph/langgraph/types.py#L711-L729) · [LangGraph 导读](../systems/langgraph/README.md)

如果任务已经发过邮件或修改过外部数据，恢复进度后先核对这些动作的实际结果，再继续。[中断与恢复](interruption-recovery.md)用创建工单的例子说明这一步。

## 回到自己的任务

面对一段较长的讨论，可以这样安排：

- 原聊天保留，方便回到出处。
- 近期任务带上相关材料和简短摘要。
- 经常使用的约定单独整理，更新时保留来源。
- 执行到一半的流程保存进度，恢复时检查已做的动作。

本章基于固定版本源码和项目内置提示，没有测量摘要准确度、记忆召回率或跨进程恢复效果。重要细节需要回到原材料确认，保存和检索的方法则按所用应用配置。

继续读：[Pi](../systems/pi/README.md) · [Letta Code](../systems/letta/README.md) · [Mem0](../systems/mem0/README.md) · [LangGraph](../systems/langgraph/README.md)。
