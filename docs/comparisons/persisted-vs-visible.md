# 存下来了，下一轮就一定能看见吗？

[返回横向对照](README.md) · [概念图：上下文与记忆](../concepts/context-vs-memory.md)

**不一定。**“持久保存”说的是应用未来还有机会取回信息；“本轮可见”说的是此次模型请求里实际带了什么。两者之间有选择、投影、检索或提示重编译步骤。这里仅对照已审阅的两条固定源码路径，不把它们扩展成两个项目全部运行模式的结论。

| 同一个问题 | Pi 的已核对路径 | Letta Code 的已核对路径 |
| --- | --- | --- |
| 信息存在哪里？ | coding-agent 的 JSONL session tree 存消息和分支；当前模型请求另行装配。 | local MemFS v1 的核心记忆位于 `system/` Markdown；其他文件、Skills 与历史记录分开。 |
| 下一轮如何进入模型？ | `SessionManager` 投影当前分支；核心在模型调用前运行 `transformContext → convertToLlm`。 | 核心记忆块编入 system prompt；外部文件正文按需读取；旧对话细节通过 recall 查找。 |
| 更新后立即可见吗？ | 新消息是否进入下一轮，取决于当前分支和上下文转换；单凭 JSONL 存在不能保证。 | 文件编辑、提交、同步及提示重编译是不同事件；已编译的当前回合提示不会因文件变化自动改写。 |
| 这条路径不能证明什么？ | 不证明任意旧分支或原始文件内容都完整进入模型。 | 不证明所有部署采用 local MemFS v1，也不证明 recall 必然命中。 |

Pi 的依据是[会话树投影](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/coding-agent/src/core/session-manager.ts#L543-L582)与[调用前上下文转换](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/agent/src/agent-loop.ts#L380-L406)；Letta Code 的依据是[local MemFS 提示](https://github.com/letta-ai/letta-code/blob/1f55d3dc66e238d203757fae288bb53f3adc7cd3/src/agent/prompts/letta_local_memfs.md#L8-L55)、[格式判定](https://github.com/letta-ai/letta-code/blob/1f55d3dc66e238d203757fae288bb53f3adc7cd3/src/agent/memory-format.ts#L6-L29)及[同步/重编译路径](https://github.com/letta-ai/letta-code/blob/1f55d3dc66e238d203757fae288bb53f3adc7cd3/src/agent/subagents/memory-worker.ts#L95-L139)。完整的适用范围和未验证项分别见 [Pi](../systems/pi/README.md) 与 [Letta Code](../systems/letta/README.md)。

这是一项**静态源码对照**。若要验证用户实际体验，应记录同一条信息在存储、下一次请求输入、模型回答中的位置；没有请求日志或运行轨迹时，不用“记住了”概括其效果。
