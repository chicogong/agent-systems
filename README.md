# 图解 Agent 系统

**在 AI 时代，学懂 Agent，把方法用起来。一本用图解、讲解和具体案例连接入门学习、日常应用与开源实现的中文书。**

<img src="book/assets/cover-preview.png" alt="《图解 Agent 系统》封面预览" width="220">

[在线阅读](https://books.aimake.cc/) · [学习与应用](docs/learning-and-practice.md) · [选择阅读路线](docs/learning-path.md) · [按书序阅读](book/CONTENTS.md) · [PDF 电子校样](https://books.aimake.cc/pdf)

如果你是学生、老师、对 AI 感兴趣的人，或已经在学习和工作中使用 AI 工具，可以从这里选一个起点：先看具体任务，再学习怎样组织资料、安排步骤和检查结果，愿意深入时再读真实系统的实现。图、例子和讲解会带着你往下走，纸笔就能先试。

书中从一个资料助手的正常任务展开，解释模型、工具、上下文与记忆如何配合；再连接 Pi、Codex 等项目的设计取舍。想探索 AI 相关职业方向的读者，可以借这些问题寻找值得继续学习的能力，积累一份自己的学习或项目成果；本书不承诺就业、收入或特定工具的使用效果。

这是**持续更新的公开预览稿**。系统篇介绍指定版本中的一条实现路径，章末列出来源和研究范围。

## 翻几张图，看看书里怎么讲

每张图讲清一件事，正文用具体例子说明步骤，代码导读供愿意深入的读者选看。点缩略图可打开原尺寸 SVG；每组图都有可编辑 `.excalidraw` 和文字说明。

| 从目标到一份有出处的回答 | 模型、Harness、CLI、Skill、MCP 怎样分工 |
| --- | --- |
| [![Agent 运行循环：任务、决策、执行、观察与验证](figures/agent-loop/preview.png)](figures/agent-loop/diagram.svg) | [![一项任务穿过 Agent 系统的五层职责](figures/agent-stack/preview.png)](figures/agent-stack/diagram.svg) |
| [读 Agent loop](docs/concepts/agent-loop.md) | [读一项任务里的分工](docs/concepts/model-harness-cli-mcp-skill.md) |
| **资料怎样进入这次回答** | **超时后，先查询原操作** |
| [![会话、摘要、记忆与检索进入本轮上下文的区别](figures/context-vs-memory/preview.png)](figures/context-vs-memory/diagram.svg) | [![外部动作超时后的状态查询与重试边界](figures/permission-and-recovery/preview.png)](figures/permission-and-recovery/diagram.svg) |
| [读上下文与记忆](docs/concepts/context-vs-memory.md) | [读审批、恢复与回执丢失实验](docs/comparisons/permission-and-recovery.md) |
| **给代码安排合适的执行环境** | **Hermes 怎样保存和使用记忆** |
| [![沙箱的运行设置、执行记录与结果检查](figures/sandbox-execution/preview.png)](figures/sandbox-execution/diagram.svg) | [![Hermes 的知识文件、提示快照与待批准写入](figures/hermes-session-memory/preview.png)](figures/hermes-session-memory/diagram.svg) |
| [读沙箱与生命周期](docs/concepts/sandbox-execution.md) | [读 Hermes 的知识维护路径](docs/systems/hermes/README.md) |

想看小字时，点图打开原尺寸 SVG。更多图和文字说明见[图稿索引](figures/README.md)。

## 你可以怎样读

- **学生、老师与第一次接触 AI 的读者：** 从[学习与应用导读](docs/learning-and-practice.md)的三份虚构资料开始，看一份带出处的回答怎样形成，再读 [Agent 循环](docs/concepts/agent-loop.md)。学生可以整理知识与问题，老师可以把同一例子改成讨论活动；不用先学习代码。
- **已经在用 AI，希望用得更好：** 用[学习与应用](docs/learning-and-practice.md#把方法带到你的场景)中的任务卡，练习说清目标、选择资料、区分事实与建议、核对结果。卡住时可选用[AI 陪读](book/frontmatter/reading-guide.md#和-ai-一起读)，再读[上下文与记忆](docs/concepts/context-vs-memory.md)。
- **想探索新方向、积累能力：** 先留下一份自己的解释、简报或图，再沿[阅读路线](docs/learning-path.md)选择使用、源码或工程方向，逐步积累作品和经验。
- **想读懂一个项目：** 从 [Pi 的运行核心与外壳](docs/systems/pi/README.md)或[Codex 的命令审批与执行](docs/systems/codex/README.md)开始。系统篇给出上游仓库、固定 commit、关键源码位置、正常/失败路径与未验证范围，不要求把整个仓库从头读完。
- **正在设计自己的系统：** 按问题查[机制](docs/concepts/README.md)、[跨系统对照](docs/comparisons/README.md)和[术语表](docs/glossary.md)。例如工具权限、上下文预算、记忆可见性、委派交接、checkpoint、评测和外部副作用，不必先选“最佳框架”。

也可以选用[AI 陪读](book/frontmatter/reading-guide.md#和-ai-一起读)：让常用助手解释图中一个关系、听你的复述，再换个例子一起检查。书提供图文与来源，AI 帮你展开问题，最后用自己的话说明理解。

## 内容地图

| 章节类型 | 你会得到什么 | 从这里试看 |
| --- | --- | --- |
| **学习与应用** | 用一组随书资料尝试回答、教学活动或工作简报，形成自己的任务卡与修改记录 | [把所学用起来](docs/learning-and-practice.md) · [阅读路线](docs/learning-path.md) · [AI 陪读](book/frontmatter/reading-guide.md#和-ai-一起读) |
| **机制图解** | 一条任务怎样经过模型、工具、上下文、记忆、权限和恢复；图旁写明例子与反例 | [Agent loop](docs/concepts/agent-loop.md) · [MCP、Skill 与工具](docs/concepts/mcp-skill-tool-lifecycle.md) · [观察与评测](docs/concepts/observation-evaluation.md) |
| **开源项目讲解** | 一个版本里的具体步骤，以及连接这些步骤的关键代码 | [Pi](docs/systems/pi/README.md) · [OpenCode](docs/systems/opencode/README.md) · [LangGraph](docs/systems/langgraph/README.md) |
| **横向对照** | 围绕同一个问题，比较不同做法和取舍 | [循环与停止](docs/comparisons/loop-and-stop.md) · [四种状态](docs/comparisons/four-kinds-of-state.md) · [权限与恢复](docs/comparisons/permission-and-recovery.md) |
| **可选小实验** | 用随书脚本观察读取、输入选择、结果查询和错误处理 | [第一轮 Agent](docs/labs/first-agent-loop.md) · [上下文预算](docs/labs/context-budget.md) · [远端结果查询](docs/labs/remote-effect.md) · [本地 HTTP 回执](docs/labs/http-receipt.md) |

系统案例覆盖 Pi、DSH（DeepSeek Harness）、Codex、OpenCode、mini-SWE-agent、OpenHands、Browser Use、Qwen Code、Kimi Code、MiMo Code、Letta Code、Hermes Agent、Mem0、LangGraph、OpenClaw 与 GPT Researcher。它们分属编码助手、运行框架、记忆组件等不同层次；**入书理由是能解释一种架构取舍，不是热度或 Star 数。** 逐篇范围见[系统索引](docs/systems/README.md)，候选及后续教学安排见[选题地图](docs/program.md)与[扩写计划](docs/curriculum-expansion.md)。

也介绍[沙箱](docs/concepts/sandbox-execution.md)，说明怎样安排代码运行的文件、网络和资源；[Computer／Browser Use](docs/concepts/computer-and-browser-use.md)用填表任务讲清观察页面、执行操作和读取结果。想进一步观察检查过程，可以选择[资料与工具权限小实验](docs/labs/evidence-contract.md)。

## 选择顺手的阅读方式

| 入口 | 适合什么场景 |
| --- | --- |
| [在线阅读站](https://books.aimake.cc/) | 手机阅读、章节导航、搜索和反馈；公开站按人工发布批次更新。 |
| [GitHub 书序目录](book/CONTENTS.md) | 直接看唯一的 Markdown 源稿、代码链接、图源和修订历史。 |
| [可携带 Markdown 阅读包](https://books.aimake.cc/downloads) | 固定版本 ZIP，导入 Obsidian 或普通 Markdown 阅读器；相对链接、图与可选练习的代码随包保留。[自行构建](book/README.md#markdown-阅读包)。 |
| [PDF 电子校样](https://books.aimake.cc/pdf) | 固定页序浏览、批注和下载；它不是印刷母版，更新不由每周 Action 自动覆盖。 |

正文只维护一份。`book/manifest.txt` 决定 GitHub 目录、网站、PDF 和阅读包的书序；导出物不是第二份稿件。线上站与本地仓库可能处于不同发布批次，**精确篇数、页数和验收缺口以[当前状态](docs/roadmap.md)为准**。

## 证据、图源与参与

每篇系统文章区分**源码事实、官方文档、运行观察、工程推断与未知**；上游版本记录在[来源台账](sources/README.md)。图的 `.excalidraw`、SVG、PNG 与文字说明成组维护；图稿排版遵循[风格与可读性规则](figures/STYLE.md)。通过脚本测试不等于真实产品通过端到端验证，更不等于读者已经读懂。[写作与校稿方法](docs/editorial-plan.md)和[出版验收单](docs/publication-checklist.md)公开了进入预览稿、正式版和印刷版各自的门槛。

欢迎带着**具体章节、固定版本链接、复现步骤或图中哪条箭头有问题**提交反馈：[网站勘误入口](https://books.aimake.cc/feedback) · [贡献指南](CONTRIBUTING.md)。作者联系邮箱：[ghr7719@gmail.com](mailto:ghr7719@gmail.com)。

如果愿意帮我们检验“图和例子是否真的讲明白”，可以[任选一篇做简短试读](docs/reader-trial.md)：看完换一个情况，用自己的话解释即可，不需要运行代码。

本书原创文字与图使用 [CC BY 4.0](LICENSE-CONTENT.md)，构建脚本使用 [MIT](LICENSE-CODE)；上游项目、商标和第三方素材遵守各自许可。本仓公开的是持续完善的预览稿，不表示完整源码审计、外部读者验收或正式出版已经完成。[封面与书脊设计参考](book/assets/README.md)也不等同于印厂可直接使用的文件。
