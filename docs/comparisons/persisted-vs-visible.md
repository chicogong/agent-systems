# 存下来了，下一轮就一定能看见吗？

[返回横向对照](README.md) · [概念图：上下文与记忆](../concepts/context-vs-memory.md)

你告诉资料助手“回答尽量简短”，希望下次也能用上这个偏好。一条完整的路径是：先保存这句话，下次取出适合当前任务的信息，再放进模型输入。“持久保存”让应用以后还能取回；“本轮可见”描述这次请求实际带了什么。下面看 Pi 和 Letta Code 怎样连接这两个位置。

| 同一个问题 | Pi 的已核对路径 | Letta Code 的已核对路径 |
| --- | --- | --- |
| 信息存在哪里？ | 聊天记录按消息和分支保存为 JSONL 文件，也就是每行一条 JSON 记录；当前模型请求另外整理。 | 本地文件记忆（local MemFS v1）的常用信息放在 `system/` 目录的 Markdown 文件中；其他文件、Skills 与历史记录分开。 |
| 下一轮如何进入模型？ | `SessionManager` 从完整记录中选出当前分支的内容；核心在调用模型前整理消息，再转成模型接口需要的格式（`transformContext → convertToLlm`）。 | 常用信息编入系统提示（system prompt）；参考文件正文按需读取；过去对话通过历史查找（recall）工具补查。 |
| 更新后怎样生效？ | 新消息进入下一轮，要经过当前分支选择和上下文转换。 | 文件编辑、提交、同步及提示重编译有先后；当前回合继续使用已经编译的提示。 |
| 本篇的适用范围 | 当前分支的内容选择和调用前转换；旧分支及原始文件需另查。 | 本地文件记忆 v1；其他部署和历史查找的实际效果需另查。 |

Pi 的依据是[会话树投影](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/coding-agent/src/core/session-manager.ts#L543-L582)与[调用前上下文转换](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/agent/src/agent-loop.ts#L380-L406)；Letta Code 的依据是[local MemFS 提示](https://github.com/letta-ai/letta-code/blob/1f55d3dc66e238d203757fae288bb53f3adc7cd3/src/agent/prompts/letta_local_memfs.md#L8-L55)、[格式判定](https://github.com/letta-ai/letta-code/blob/1f55d3dc66e238d203757fae288bb53f3adc7cd3/src/agent/memory-format.ts#L6-L29)及[同步/重编译路径](https://github.com/letta-ai/letta-code/blob/1f55d3dc66e238d203757fae288bb53f3adc7cd3/src/agent/subagents/memory-worker.ts#L95-L139)。完整的适用范围和未验证项分别见 [Pi](../systems/pi/README.md) 与 [Letta Code](../systems/letta/README.md)。

你可以用同一句偏好做一次阅读检查：在文件中找到它，在下一次请求输入中找到它，再看回答有没有按它调整。三处分别说明“保存了”“带进去了”“用起来了”，也能帮你定位遗漏发生在哪一步。

本篇是两条固定源码路径的静态对照，尚未做这种运行检查；完整适用范围见上面的系统章节。
