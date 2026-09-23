# 图解 Agent 系统：并行实施总图

[返回首页](../README.md) · [发布路线](roadmap.md)

本书不是热门项目名录，而是一组能互相对照的架构问题。每个系统先做一条**可定位的窄路径**，再决定是否值得第二篇；机制篇解释共性，系统篇给出固定版本的反例或实现，对照篇只比较已经核验过的同一问题。

## 四条并行研究线

| 研究线 | 要回答的问题 | 首批系统 | 适合的图，不是硬性模板 |
| --- | --- | --- | --- |
| 运行循环与编码 Agent | 输入、模型回合、工具结果、停止条件怎样连接？ | Pi、Codex、OpenCode、mini-SWE-agent | 时序图、状态图、事件时间线 |
| 执行环境与权限 | 工具在哪运行，谁批准、隔离、观察和恢复副作用？ | Codex、OpenHands、Browser Use、Cline | 泳道、信任边界、失败路径 |
| 上下文、会话与记忆 | 什么进入本轮模型输入，什么写入持久状态，什么需要检索？ | Pi、Letta Code、OpenCode、Mem0 | 数据生命周期、存储/可见性映射 |
| 编排与生态扩展 | 何时多 Agent，插件、Skill、MCP 或框架各改了什么？ | OpenClaw、GPT Researcher、LangGraph、AutoGen、CrewAI | 委派树、依赖图、对照矩阵 |

安全、可观测与评测贯穿四条线，不为它们虚构一个通用“最佳实践”。每个机制篇至少要讲一个正常路径和一个失败/边界路径。图的形式按[设计原则](../figures/STYLE.md)决定。

## 系统选题池与首问

“首问”是研究范围，不是已核实的架构结论。仓库地址用于发现；只有开始正文时才记录固定 commit 和证据。

| 批次 | 系统 | 第一篇先问什么 | 预期贡献 |
| --- | --- | --- | --- |
| 已起步 | [Pi](systems/pi/README.md) | 核心循环、coding-agent 外壳、Extension 与 Skill 如何分层？ | 可读的小核心与资源边界 |
| 首轮已起稿 | [Codex](systems/codex/README.md) | 一次工具动作如何跨审批、沙箱与执行边界？ | 控制与执行路径 |
| 首轮已起稿 | [OpenCode](systems/opencode/README.md) | 一次工具调用的状态与整段 Session 状态如何区别？ | 细粒度状态组织 |
| 首轮已起稿 | [Letta Code](systems/letta/README.md) | local MemFS v1 的持久记忆与本轮模型可见上下文如何分开？ | 记忆模型 |
| 另列历史线索 | [Letta 旧服务](https://github.com/letta-ai/letta) | 旧版 memory blocks 怎样工作？ | 主仓库当前源码状态须先核对，不把归档实现当现行架构 |
| 第二轮已起稿 | [OpenHands](systems/openhands/README.md) | 默认 SDK 路径里动作如何记录、确认、执行和回写？ | 事件与确认边界 |
| 第二轮已起稿 | [mini-SWE-agent](systems/mini-swe-agent/README.md) | 极简循环怎样依消息账本停止？ | 最小基线 |
| 第二轮已起稿 | [Browser Use](systems/browser-use/README.md) | 浏览器观察、动作与页面状态如何闭环？ | UI 动作空间 |
| 第三轮已起稿 | [OpenClaw](systems/openclaw/README.md) | Gateway 显式 sessionKey 怎样定 owner 与授权目标？ | 常驻系统的路由边界 |
| 第三轮已起稿 | [GPT Researcher](systems/gpt-researcher/README.md) | Hybrid 的多源上下文怎样汇合到写作器？ | 研究型工作流 |
| 第三轮已起稿 | [Qwen Code](systems/qwen-code/README.md) | 延迟工具的 schema 怎样发现，执行为何另过调度器？ | 工具声明预算与执行控制 |
| 专题已起稿 | [LangGraph](systems/langgraph/README.md) | 同一 thread 的 checkpoint 如何定位历史版本并分叉？ | 运行状态版本，不是语义记忆 |
| 专题候选 | [AutoGen](https://github.com/microsoft/autogen)、[CrewAI](https://github.com/crewAIInc/crewAI)、[Pydantic AI](https://github.com/pydantic/pydantic-ai) | 框架提供状态、委派与运行保证的哪一部分？ | 框架与成品 Agent 的边界 |
| 第二轮已起稿 | [Mem0](systems/mem0/README.md) | 记忆抽取、存储、检索与写回各在何处？ | 外挂记忆对照 |
| 对照卡 | [Aider](https://github.com/Aider-AI/aider)、[Cline](https://github.com/cline/cline)、[Goose](https://github.com/aaif-goose/goose)、[Gemini CLI](https://github.com/google-gemini/gemini-cli)、[Kimi Code](https://github.com/MoonshotAI/kimi-cli) | 对现有机制是否提供不同的取舍？ | 有差异才升格为深读 |

这不是承诺把每个仓库都画成完整拓扑。表中“已起稿”仅指一条源码切面完成，不表示完整审计或运行验证；其余候选继续按差异价值滚动研究，没有可靠源码定位的主题不给“已研究”标签。闭源产品只能作为公开资料的边界清晰参照。

## 章节与交付合同

每篇系统剖面使用[统一模板](systems/TEMPLATE.md)，但图不统一模板。最小完整单元包含：一个窄问题、固定源码版本、主图及等价文字、5–10 步关键代码导读、证据等级、失败/停止路径、刻意省略之处、可复核的链接。每篇概念专题还要给术语、反例与至少一个系统映射。对照页必须引用已完成的系统剖面，不能用项目宣传语直接填表。

本地 `.excalidraw` 是可编辑图源；SVG 嵌入 Markdown；PNG 用于视觉检查。检查图本身、缩小后的图、文字版、源码版本以及生成/导出是否同源。图库允许时序、状态、泳道、生命周期、层级和矩阵并存，读者看不懂的“漂亮图”不算完成。

## 并行合稿规则

各研究任务只写自己的 `docs/systems/<system>/` 和 `figures/<figure>/`，不抢改首页、目录、路线或公共脚本。主编负责合并索引、审查跨篇术语、运行 `scripts/check_repo.py`、目视复核图、记录未完成项。一个 Agent 的源码审计是初稿，不是独立审查；关键结论在合稿时重新打开固定来源。外部 ChatGPT 网页研究若使用，只作为候选和反证线索，需单独记录模型输出与官方来源核验，不把未验证摘要直接贴进正文。

## 发布边界

仓库当前保持私有。公开前至少完成：内容/代码许可，第三方图与短引文检查，链接与图源检查，图文可访问性，一轮非作者读者测试，以及对静态源码结论与运行观察的清楚区分。公开可发布“预览版”，但未写完的候选系统必须继续标为候选。
