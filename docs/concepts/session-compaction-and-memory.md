# 会话变长以后：压缩、记忆和检查点各保留什么

[返回机制目录](README.md) · [先读：上下文、会话与记忆](context-vs-memory.md) · [状态对照](../comparisons/four-kinds-of-state.md)

“上次明明说过，Agent 怎么又不知道了？”问题通常不在于系统**有没有保存**，而在于下一次请求**选了什么、装进了多少、取回的是否正确**。会话记录、压缩摘要、长期记忆和运行检查点可以同时存在，但彼此不能替代。本篇沿信息的生命周期读四个固定版本的实现；它们是**不同项目的对照案例**，不是一个已集成的产品架构。

## 先看四个动作，而不是四个名字

| 动作 | 保存或产出什么 | 下一次模型请求会自动得到吗？ | 本篇对应案例 |
| --- | --- | --- | --- |
| 记录 | 消息、工具结果或事件，供会话回看、分支与续接 | 不一定；还要选当前分支并组装上下文 | Pi coding-agent 的 JSONL 会话树 |
| 压缩 | 对部分旧消息生成较短的摘要，并保留最近片段 | 只有宿主把摘要及保留片段投影进去才会看到；细节可能丢失 | Pi coding-agent 的 compaction |
| 写入与检索记忆 | 跨轮次维护的核心块、外部文件，或按作用域检索的事实记录 | 核心块可编入提示；外部内容仍需读取或由调用方注入 | Letta Code local MemFS v1、Mem0 Python OSS |
| 检查点 | 某一步的图状态及其可定位版本 | 不等于自动把历史知识放入提示；取决于图的状态与节点逻辑 | LangGraph Python checkpointer |

这里的“自动”只问**所选数据是否进入一次具体模型请求**，不等于模型一定正确理解它。图解版的“存放处 → 本轮可见输入”关系见[上下文与记忆](context-vs-memory.md)；本篇进一步解释内容何时被替换、再次读取或恢复。

## 一条会话怎样变成下一轮输入：以 Pi 为例

Pi 的 `SessionManager` 把 entry 组织为有 `id`、`parentId` 的会话树，当前 leaf 指向活动分支。组装时，`buildContextEntries()` 沿当前 leaf 路径取 entry；若路径上有压缩 entry，则从其 `firstKeptEntryId` 保留后续片段，并把压缩摘要放在前面。`buildSessionProjection()` 再把这些 entry 变成消息，`buildSessionContext()` 返回本次要用的消息列表。[会话树及用途](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/coding-agent/src/core/session-manager.ts#L976-L985) · [当前分支与压缩投影](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/coding-agent/src/core/session-manager.ts#L468-L582)

压缩不是简单地“删除旧消息”。这条固定源码的**自动压缩判断**中，`shouldCompact()` 按上下文 token 与窗口预留量判断是否触发；`prepareCompaction()` 根据会话投影选取待概括部分和近期保留部分，带上先前摘要；生成结果有 `summary`、`firstKeptEntryId` 等字段，并由 `appendCompaction()` 追加为新的会话 entry。下次投影用摘要替代较早的模型可见内容。**旧 entry 仍在这条会话树中的什么位置**，和**旧细节是否还在本轮模型输入**，是两个问题。[自动触发条件](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/coding-agent/src/core/compaction/compaction.ts#L286-L292) · [选取与摘要输入](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/coding-agent/src/core/compaction/compaction.ts#L894-L955) · [压缩 entry](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/coding-agent/src/core/session-manager.ts#L1258-L1285)

同样叫“摘要”，也要分清触发原因：Pi 的 compaction 可在超出上下文阈值或手动 `/compact` 时发生；另有 `/tree` 导航时的 branch summarization，用于切换分支时保留上下文。两者不是一个触发器。[固定版本的官方说明](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/coding-agent/docs/compaction.md#L14-L23)

还要再跨一层：agent-core 在模型调用前可运行 `transformContext`，再执行 `convertToLlm`，所以 coding-agent 的会话投影也不是对所有 Pi 宿主都成立的“最终提示”。上述会话树和压缩属于 **pi-coding-agent 的所选实现**，不是 `pi-agent-core` 自带的通用持久化保证。[模型请求边界](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/agent/src/agent-loop.ts#L376-L406)

## 要跨任务找回事实，得有另一个读写合同

Letta Code 的 **local MemFS v1** 把 `system/` 下的 Markdown 识别为核心记忆块；内置提示将核心块、外部文件/Skills、历史 recall 分开：核心块进入提示，外部内容按需读，较早对话可经 recall 查找。这里“进入提示”来自内置提示的设计声明及对应路径，**不代表本文已抓取每轮实际请求**。同一内置提示还明确说，编辑记忆不会立即改变当前已编译的提示，而要等待后续重编译。[v1 路径判定](https://github.com/letta-ai/letta-code/blob/1f55d3dc66e238d203757fae288bb53f3adc7cd3/src/agent/memory-format.ts#L6-L29) · [三类存放处与可见时机](https://github.com/letta-ai/letta-code/blob/1f55d3dc66e238d203757fae288bb53f3adc7cd3/src/agent/prompts/letta_local_memfs.md#L8-L46)

Mem0 在本篇限定的 Python OSS 同步路径中是**供应用调用的存取层**：`Memory.add(infer=True)` 处理输入消息、提取候选事实并写入；`Memory.search(query, filters=...)` 按作用域检索结果。搜索返回什么，不等于使用 Mem0 的 Agent 已把它装进下一次提示；**调用方还需选择、核验并注入**。此外 `infer=False`、procedural memory、异步和托管服务是其他路径，不能用这段解释概括。[写入入口与分支](https://github.com/mem0ai/mem0/blob/f8082a7345dadd9e042ebbc40b57b1498c8f6d63/mem0/memory/main.py#L760-L932) · [事实提取与写入](https://github.com/mem0ai/mem0/blob/f8082a7345dadd9e042ebbc40b57b1498c8f6d63/mem0/memory/main.py#L940-L1067) · [检索入口与作用域](https://github.com/mem0ai/mem0/blob/f8082a7345dadd9e042ebbc40b57b1498c8f6d63/mem0/memory/main.py#L1379-L1456)

LangGraph 又是另一件事：`StateSnapshot` 有 `values`、下一步 `next`、可取回版本的 `config`、`parent_config` 等字段。它描述**图执行到某一步的状态版本**，可用于回看和从旧状态继续；如果图状态内有消息，那是应用的状态设计，不等于内置了语义记忆检索。尤其不要把“恢复 checkpoint”理解成“已经回滚外部写入或工具副作用”。[快照字段](https://github.com/langchain-ai/langgraph/blob/bdb85b5aa87a21de68371d2e534b81aeed398f57/libs/langgraph/langgraph/types.py#L711-L729) · [固定版本的分支路径](../systems/langgraph/README.md)

## 用一次修复任务检验理解

以下是**教学假设，不是四个项目共同运行的一条实测轨迹**。假设用户让 Agent 修复“订单导出超时”，工具输出了较长的错误日志：

1. 当轮日志成为消息或工具结果；宿主若记录了它，记录与模型当轮看见它仍是两个可分别核对的事件。
2. 会话变长时，Pi 式压缩可能把早期日志概括为“导出查询缺少索引”，而保留最近消息。下一轮看见的是**摘要中的说法**，未必看见原日志；若摘要误写，不能把它当成已验证诊断。
3. 若“团队约定：改索引前先测慢查询”值得跨任务保留，Letta 式核心块或外部文件需要明确写入，并在适当时机重编译或读取；Mem0 式事实记录需要 `add`，以后还要 `search` 并由应用决定是否引用。**只是出现在旧聊天里，不会自动完成这些步骤。**
4. 若任务由 LangGraph 图执行，checkpoint 可以定位到某一步的图状态；恢复后仍要核对已发出的数据库写入、邮件或部署动作，不能靠状态快照推定它们撤销了。

## 证据边界与自查问题

- **源码事实**：上文 Pi 的当前分支投影与压缩 entry、Letta 的 v1 路径判定、Mem0 的同步 API 路径、LangGraph 的快照字段，均锚定所列 commit。
- **文档声明**：Letta 内置提示对核心块、recall 与重编译时机的描述是该项目给 Agent 的指引；模型是否遵循、部署是否完全按此运行，要看实际轨迹。
- **工程推断**：为了避免重复错误，重要结论应保留来源和验证状态；摘要、检索命中和状态恢复都不应代替重新核验。这是本书的操作建议，不是四个项目共有的硬编码策略。
- **未证**：本文没有运行模型或存储后端；未测摘要忠实度、记忆召回率、跨设备同步、checkpoint 对外部副作用的恢复结果，也未证明任何项目的所有运行模式。

读下一套系统时只问四句：原始内容**存在哪里**？本次请求**实际选进了什么**？压缩或检索**可能丢了什么**？发生中断后，恢复的究竟是**消息、知识还是执行状态**？把这四句答清楚，比笼统说“它有记忆”更有用。

继续沿源码读：[Pi 会话与运行分层](../systems/pi/README.md) · [Letta Code local MemFS v1](../systems/letta/README.md) · [Mem0 写入与检索](../systems/mem0/README.md) · [LangGraph checkpoint](../systems/langgraph/README.md)。
