# 选题地图：系统与架构问题

[返回首页](../README.md) · [当前状态](roadmap.md) · [写作方法](editorial-plan.md)

这里记录**为什么研究某个系统**，不记录它是否已完成。当前完成度、缺口和发布门槛只在[路线页](roadmap.md)维护；一篇文章的固定源码版本和结论范围，以文章本身及[来源台账](../sources/systems.json)为准。Star 数、讨论热度与项目名都不能替代选题理由。

## 四条研究线

| 问题线 | 先问什么 | 可提供差异的系统 |
| --- | --- | --- |
| 运行循环与工具 | 谁控制下一轮？工具何时开始、停止或失败？ | [Pi](systems/pi/README.md)、[OpenCode](systems/opencode/README.md)、[mini-SWE-agent](systems/mini-swe-agent/README.md)、[Qwen Code](systems/qwen-code/README.md) |
| 执行环境与权限 | 动作由谁授权、在哪里运行、如何记录副作用？ | [Codex](systems/codex/README.md)、[OpenHands](systems/openhands/README.md)、[Browser Use](systems/browser-use/README.md) |
| 上下文、会话与记忆 | 什么真正进入本轮模型输入，什么只是被保存？ | [Pi](systems/pi/README.md)、[Letta Code](systems/letta/README.md)、[Mem0](systems/mem0/README.md)、[LangGraph](systems/langgraph/README.md) |
| 编排与常驻系统 | 谁拥有会话，怎样聚合来源或协调执行者？ | [OpenClaw](systems/openclaw/README.md)、[GPT Researcher](systems/gpt-researcher/README.md)、[LangGraph](systems/langgraph/README.md) |

一个系统可出现在多条问题线中，但每篇文章仍只证明它固定版本中的一条**窄路径**。概念篇解释设计空间，系统篇给来源，对照篇只比较双方已经核对的同一问题；不做“最佳 Agent”总榜。

## 仍可补位的候选

| 候选 | 值得调查的问题 | 升格条件 |
| --- | --- | --- |
| [Aider](https://github.com/Aider-AI/aider)、[Cline](https://github.com/cline/cline)、[Goose](https://github.com/aaif-goose/goose)、[Gemini CLI](https://github.com/google-gemini/gemini-cli)、[Kimi Code](https://github.com/MoonshotAI/kimi-cli) | 在循环、上下文装配、授权或工具生命周期上，是否提供与已有案例不同的取舍？ | 至少指出一个现有章节解释不了的问题，并固定可定位的源码版本。 |
| [AutoGen](https://github.com/microsoft/autogen)、[CrewAI](https://github.com/crewAIInc/crewAI)、[Pydantic AI](https://github.com/pydantic/pydantic-ai) | 框架提供哪些状态、委派与运行保证，哪些仍须应用自己完成？ | 先明确框架与成品 Agent 的比较边界，避免直接拿不同层次排功能榜。 |
| [Letta 历史服务](https://github.com/letta-ai/letta) | 旧版 memory blocks 与当前 Letta Code local MemFS 有何连续或断裂？ | 核对仓库维护状态与版本；只作历史对照，不把旧实现标作现行架构。 |

新增剖面按[系统模板](systems/TEMPLATE.md)写一个可证伪的问题，固定仓库、commit、关键文件、核对日期与许可，再决定是否需要主图和第二篇。找不到可靠来源或只重复已有解释时，保留为候选，不为凑热门名单扩书。闭源产品只能据官方公开资料作边界清晰的参考，不能写成开源源码剖面。
