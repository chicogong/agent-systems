# 术语表：把名字放回具体任务里

遇到陌生词，可以先看这里的一句话解释，再回到正文例子。各项目的名字和接口会有差别，下表按本书的用法说明。

| 名称 | 用大白话讲 | 继续阅读 |
| --- | --- | --- |
| Agent | 围绕一个目标，边做、边看结果、再选择下一步的运行系统 | [三种任务组织方式](concepts/agent-workflow-multiagent.md) |
| 工作流 | 提前安排好步骤和分支，再按这些安排执行 | [工作流与 Agent](concepts/agent-workflow-multiagent.md) |
| 多 Agent／多执行者 | 把工作分给几个执行者，再检查和合并各自结果 | [委派与交接](concepts/delegation-and-handoff.md) |
| Agent loop | 模型建议动作、工具返回结果，再继续做的循环 | [运行循环](concepts/agent-loop.md) |
| Harness／运行器／宿主 | 组织模型、工具、输入和权限的运行程序 | [一项任务的分工](concepts/model-harness-cli-mcp-skill.md) |
| CLI | 命令行界面，通过输入命令与程序交互 | [职责分工](concepts/model-harness-cli-mcp-skill.md) |
| Tool／工具 | 执行读取、搜索、修改等操作，并返回结果的接口 | [工具怎样接入](concepts/extensibility-layers.md) |
| Proposal／提案 | 尚未执行的动作建议，例如“读取报名说明” | [运行循环](concepts/agent-loop.md) |
| Observation／观察 | 工具带回的内容或执行状态，例如文件原文、错误信息 | [OpenHands](systems/openhands/README.md) |
| 当前上下文 | 模型这次实际收到的指令、消息和材料 | [上下文与记忆](concepts/context-vs-memory.md) |
| Token | 模型处理文本时，将内容分成小片段后使用的计量单位 | [上下文预算](labs/context-budget.md) |
| 输入预算 | 为这次输入预留的容量，需要在其中选择材料 | [上下文与记忆](concepts/context-vs-memory.md) |
| 会话记录 | 应用保存的聊天、操作和结果，供回看或继续使用 | [四类状态](comparisons/four-kinds-of-state.md) |
| 压缩摘要 | 把较早的长内容概括成短内容，再与近期消息一起使用 | [会话变长以后](concepts/session-compaction-and-memory.md) |
| 长期记忆 | 跨任务保留的事实、约定或资料，后续需要时读取或检索 | [Letta Code](systems/letta/README.md)、[Mem0](systems/mem0/README.md) |
| Checkpoint／检查点 | 保存程序执行到某一步的状态，供回看和继续 | [LangGraph](systems/langgraph/README.md) |
| `checkpoint.md` | MiMo Code 中整理给后续模型窗口的任务和线索文件 | [MiMo Code](systems/mimo-code/README.md) |
| 审批 | 用户或既定策略决定一次动作是否可以执行 | [审批与沙箱](concepts/approval-vs-sandbox.md) |
| 沙箱／隔离 | 限定程序运行时能够接触的文件、网络和其他资源 | [沙箱执行环境](concepts/sandbox-execution.md) |
| 副作用 | 操作实际改变了文件或外部系统，例如写入文件、发送邮件 | [中断与恢复](concepts/interruption-recovery.md) |
| 操作 ID／幂等键 | 标记一次业务操作，供查询、关联和按接口规则处理重复请求 | [回执丢失](labs/remote-effect.md) |
| Skill | 按需读取的工作说明及配套资料 | [扩展能力](concepts/extensibility-layers.md) |
| Extension／扩展 | 由宿主加载的代码，可增加工具或参与运行过程 | [Pi 扩展](systems/pi/extensions-and-skills.md) |
| MCP | 连接宿主和外部服务，交换工具、资源等能力的协议 | [工具怎样接力](concepts/mcp-skill-tool-lifecycle.md) |
| 源码事实 | 能在指定代码版本中找到对应实现的说法 | [来源规则](../sources/README.md) |
| 工程推断 | 根据材料得出的设计解释或建议，正文会说明它的身份 | [来源规则](../sources/README.md) |

两个叫 checkpoint 的例子用途不同：LangGraph 保存图执行状态；MiMo Code 的文件提供后续上下文线索。读具体项目时，以章内说明为准。

幂等键也需要配合外部接口规则使用，包括参数是否一致、有效期和重复请求处理。它只是一项请求标识，可靠的重复处理由服务实现。

## 读完之后

选一个熟悉的任务，说清谁提供材料、模型怎样建议下一步、工具做了什么、结果怎样回来。再对照另一套系统，看看安排哪里不同。

本书会持续更新。PDF 是一次书稿的阅读快照，项目的实际行为按对应版本和配置核对。欢迎指出一段难懂的解释，或一个需要修正的图文关系。
