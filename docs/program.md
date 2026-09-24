# 选题地图：系统与架构问题

[返回首页](../README.md) · [当前状态](roadmap.md) · [写作方法](editorial-plan.md)

这里记录**为什么研究某个系统**，不记录它是否已完成。当前完成度、缺口和发布门槛只在[路线页](roadmap.md)维护；一篇文章的固定源码版本和结论范围，以文章本身及[来源台账](../sources/systems.json)为准。Star 数、讨论热度与项目名都不能替代选题理由。

## 四条研究线

| 问题线 | 先问什么 | 可提供差异的系统 |
| --- | --- | --- |
| 运行循环与工具 | 谁控制下一轮？工具何时开始、停止或失败？ | [Pi](systems/pi/README.md)、[OpenCode](systems/opencode/README.md)、[mini-swe-agent](systems/mini-swe-agent/README.md)、[Qwen Code](systems/qwen-code/README.md) |
| 执行环境与权限 | 动作由谁授权、在哪里运行、如何记录副作用？ | [Codex](systems/codex/README.md)、[OpenHands](systems/openhands/README.md)、[Browser Use](systems/browser-use/README.md) |
| 上下文、会话与记忆 | 什么真正进入本轮模型输入，什么只是被保存？ | [Pi](systems/pi/README.md)、[Letta Code](systems/letta/README.md)、[Mem0](systems/mem0/README.md)、[LangGraph](systems/langgraph/README.md) |
| 编排与常驻系统 | 谁拥有会话，怎样聚合来源或协调执行者？ | [OpenClaw](systems/openclaw/README.md)、[GPT Researcher](systems/gpt-researcher/README.md)、[LangGraph](systems/langgraph/README.md) |

一个系统可出现在多条问题线中，但每篇文章仍只证明它固定版本中的一条**窄路径**。概念篇解释设计空间，系统篇给来源，对照篇只比较双方已经核对的同一问题；不做“最佳 Agent”总榜。

## 跨层选题先分层

[五层职责导读](concepts/model-harness-cli-mcp-skill.md)已用一项任务区分模型、Harness、CLI、Skill 与 MCP。它们不是五种竞品：模型给出判断，Harness 管运行与边界，CLI 提供交互入口，Skill 装载流程知识，MCP 连接外部能力。下一波研究沿以下问题推进，而不把热门名称直接并列打分。

| 对象 | 研究层次 | 要回答的新问题 | 晋级方式 |
| --- | --- | --- | --- |
| [Codex](systems/codex/README.md)、[Claude Code](https://code.claude.com/docs/en/how-claude-code-works) | 两个编码 Agent 的公开行为与用户工作流 | 同一修复任务中的项目指导、MCP、Skill、审批/沙箱如何分工？ | [使用层对照](comparisons/claude-code-codex.md)把 Codex 固定源码与 Claude Code 官方文档分开标注；不推断未公开调用栈。 |
| [MiMo Code](systems/mimo-code/README.md)、[Kimi Code](systems/kimi-code/README.md) | 开源 CLI + Harness | 长任务 checkpoint/重建与忙时 steer 缓冲/step 边界分别怎样做？ | 已形成各自固定 commit 的局部静态源码稿；后续核运行层时序、失败注入与二次来源。 |
| [Jev](https://typesafe.ai/blog/introducing-system-one-models-and-jev) | 结构化决策模型，不是编码 Agent | 有界判断怎样嵌入 Skill 选择或路由，而执行权仍留给代码？ | 已有[模型/决策层旁栏](concepts/jev-and-system-one.md)；性能与正确性仍属厂商主张，未独立复现。 |
| MCP、Agent Skills、CLI 与 Harness | 协议、工作流包、界面与运行器 | 哪个层次能增加能力，哪个层次能授权执行，哪个只改变入口？ | 官方规范/文档加至少一条具体产品接入路径；安全边界与失败路径都要有。 |

[Jev、MiMo Code、Kimi Code 研究笔记](field-notes/2026-09-23-jev-mimo-kimi.md)保留初始问题和第一方入口；是否已成书、核验到哪一步，以各章节与[路线页](roadmap.md)为准，不能用早期笔记代替现稿。

## 仍可补位的候选

| 候选 | 值得调查的问题 | 升格条件 |
| --- | --- | --- |
| [Aider](https://github.com/Aider-AI/aider)、[Cline](https://github.com/cline/cline)、[Goose](https://github.com/aaif-goose/goose)、[Gemini CLI](https://github.com/google-gemini/gemini-cli) | 在循环、上下文装配、授权或工具生命周期上，是否提供与已有案例不同的取舍？ | 至少指出一个现有章节解释不了的问题，并固定可定位的源码版本。 |
| [AutoGen](https://github.com/microsoft/autogen)、[CrewAI](https://github.com/crewAIInc/crewAI)、[Pydantic AI](https://github.com/pydantic/pydantic-ai) | 框架提供哪些状态、委派与运行保证，哪些仍须应用自己完成？ | 先明确框架与成品 Agent 的比较边界，避免直接拿不同层次排功能榜。 |
| [Letta 历史服务](https://github.com/letta-ai/letta) | 旧版 memory blocks 与当前 Letta Code local MemFS 有何连续或断裂？ | 核对仓库维护状态与版本；只作历史对照，不把旧实现标作现行架构。 |
| WorkBuddy 等闭源工具的使用路径 | 对同一任务，项目指令、工具接入、审批与交付证据在用户界面上如何呈现？ | 先确认具体产品与官方资料，再用获授权的环境记录可复现实操；只写公开行为，不猜内部架构。 |

新增剖面按[系统模板](systems/TEMPLATE.md)写一个可证伪的问题，固定仓库、commit、关键文件、核对日期与许可，再决定是否需要主图和第二篇。找不到可靠来源或只重复已有解释时，保留为候选，不为凑热门名单扩书。闭源产品只能据官方公开资料作边界清晰的参考，不能写成开源源码剖面。
