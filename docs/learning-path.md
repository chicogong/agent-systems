# 从入门理解到应用实践：选择你的阅读路线

[返回首页](../README.md) · [术语表](glossary.md) · [当前书稿范围](roadmap.md)

先选一个想理解或想完成的小任务，再决定读多深。图文是默认入口，源码和编程实验可以按兴趣选择。

## 先体验，再解释，再带回自己的场景

1. **先做一份成果。** 读[学习与实践](learning-and-practice.md)，用三份虚构资料回答一个问题。纸笔就能完成。
2. **顺着图讲过程。** 读[Agent loop](concepts/agent-loop.md)，指出任务、读取资料、工具返回和回答的位置。
3. **换个用途。** 做学习卡片、课堂讨论材料或工作简报。按[应用入口](learning-and-practice.md#把方法带到你的场景)选择一个。
4. **再选下一篇。** 想理解资料怎样选择，读上下文；想研究实现，选一个项目；想动手，再做小实验。

愿意让 AI 陪读，可以用[阅读指南](../book/frontmatter/reading-guide.md#和-ai-一起读)里的开场：给它当前材料，先说自己的理解，再请它解释卡住的地方。

## 1. 先看模型与工具怎样接力

从 [Agent loop](concepts/agent-loop.md)、[职责分工](concepts/model-harness-cli-mcp-skill.md)和[上下文与记忆](concepts/context-vs-memory.md)开始。先记住模型、工具和宿主的分工：模型建议下一步，工具执行具体操作，宿主组织运行并交回结果。

可以画一个熟悉的例子：收到天气问题 → 读取天气 → 得到结果 → 写出建议。在图上标出谁执行读取，谁组织回答。再把工具换成发送消息，补上发送前的确认步骤。

想看程序执行时，选择[本地循环小实验](labs/first-agent-loop.md)。它用固定脚本模拟模型提案，展示读取、批准、写入和检查，使用 Python 标准库，不需要模型账号。

延伸阅读：[Hugging Face Agents Course 第一单元](https://huggingface.co/learn/agents-course/unit1/introduction) · [Anthropic 的工作流与 Agent 模式](https://www.anthropic.com/engineering/building-effective-agents)。

## 2. 再看能力怎样接入

读 [Skill、MCP 与工具权限](concepts/mcp-skill-tool-lifecycle.md)和 [Codex 的命令执行](systems/codex/README.md)。Skill 提供工作说明和资料，MCP 连接外部能力，运行程序安排工具使用和权限。

可以为一个只读搜索工具写一张说明卡：输入是什么，返回什么，允许搜索哪个目录，出错后怎样处理。再设计一份 `SKILL.md`，说明适用任务和检查方法。想支持写文件时，补上需要谁确认、允许修改哪些文件。

涉及执行环境时，选读[沙箱](concepts/sandbox-execution.md)。涉及页面操作时，选读[Computer／Browser Use](concepts/computer-and-browser-use.md)的“只填表、不提交”例子。先在纸上安排流程，真正执行前再核对产品设置。

延伸阅读：[MCP 架构规范](https://modelcontextprotocol.io/specification/2025-11-25/architecture) · [Agent Skills 格式](https://github.com/agentskills/agentskills/blob/main/docs/specification.mdx)。

## 3. 想读源码时，先选一个项目

建议从 [Pi](systems/pi/README.md)及其[代码导读](systems/pi/code-walkthrough.md)开始。它把模型接口、运行核心和交互应用分开，比较容易看清各自做什么。也可以直接选择更贴近问题的项目：

- [mini-SWE-agent](systems/mini-swe-agent/README.md)：用较短代码读完一轮。
- [OpenCode](systems/opencode/README.md)：查看工具调用与会话的不同进度。
- [Kimi Code](systems/kimi-code/README.md)：查看运行中收到新消息后怎样处理。
- [MiMo Code](systems/mimo-code/README.md)：查看长任务怎样整理续接材料。

从章内给出的固定版本打开三个位置：请求入口、工具结果写回、结束或继续。用自己的话写出一条正常路径，再带着一个问题继续查，例如工具出错后怎样处理。尚未查到的部分留作待查。

需要理解输入选择时，可以先看[上下文预算小实验](labs/context-budget.md)。它用字符预算和固定规则展示两种选法，不测量真实模型的 token。

官方源码：[Pi](https://github.com/earendil-works/pi) · [mini-SWE-agent](https://github.com/SWE-agent/mini-swe-agent) · [OpenCode](https://github.com/anomalyco/opencode) · [Kimi Code](https://github.com/MoonshotAI/kimi-code) · [MiMo Code](https://github.com/XiaomiMiMo/MiMo-Code)。

## 4. 需要做系统时，再看保存、协作与恢复

按手头的问题选择：

- [LangGraph](systems/langgraph/README.md)：保存某一步的状态，再继续执行。
- [Letta Code](systems/letta/README.md)：管理核心记忆和按需资料。
- [GPT Researcher](systems/gpt-researcher/README.md)：将检索材料整理进报告。
- [横向对照](comparisons/README.md)：围绕同一个问题比较不同做法。

可以设计一个“整理三份资料并写摘要”的任务，写出来源、各步产物、运行时限和检查方法。假设在读取后、保存摘要前中断，列出已完成和待完成的步骤。涉及外部写入时，再安排状态查询和重试规则。

愿意动手时，按需选这些独立小实验：

- [不可信资料与结果检查](labs/evidence-contract.md)：看引用和工具权限怎样核对。
- [回执丢失](labs/remote-effect.md)：看请求超时后怎样查询原结果。
- [本地 HTTP](labs/http-receipt.md)：在本机测试读超时、同 ID 重放和冲突。它会启动本机 loopback 服务，业务仍是虚构登记任务。

前两项使用无网络的确定性模拟，HTTP 项目只连接本机服务。运行环境、临时目录和命令在各篇说明。

官方源码：[LangGraph](https://github.com/langchain-ai/langgraph) · [Letta Code](https://github.com/letta-ai/letta-code) · [GPT Researcher](https://github.com/assafelovic/gpt-researcher) · [Microsoft Agent Framework](https://github.com/microsoft/agent-framework)。

## 怎样继续选材料

先选能解答当前问题的材料。想比较编排方式，可以查看 [CrewAI](https://github.com/crewAIInc/crewAI)；想了解项目演进，可以查看 [AutoGen README](https://github.com/microsoft/autogen/blob/main/README.md) 的当前维护说明。两者是延伸阅读，不要求逐个安装。

[Claude Code 的官方说明](https://code.claude.com/docs/en/how-claude-code-works)适合对照公开行为；[Jev 文档](https://docs.typesafe.ai/introduction)介绍有限问题的判断。闭源产品的说明与开源项目的代码导读，按各自材料理解。

想深入某个项目时，核对它的版本和维护情况；复用代码、图片或教程时，检查对应许可。本书各项目篇保留固定版本与已读范围，方便回到当时的实现。
