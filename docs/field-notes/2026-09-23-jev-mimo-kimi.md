# Jev、MiMo Code、Kimi Code：候选研究笔记

> 2026-09-23 的选题记录；不是已完成的系统章节，也不进入 `book/manifest.txt`。以下“已核对”仅指重开第一方网页或仓库入口，**不等于**固定源码版本审计、运行验证、独立基准复现或许可终审。

## 先分清研究对象

| 名称 | 本次归类 | 不应混同为 |
| --- | --- | --- |
| Jev | TypeSafe 的结构化**决策模型**及托管 API；公开可读的是文档和客户端 SDK。 | 能自行规划、调用工具和维持会话的编码 Agent。 |
| MiMo Code | 小米 MiMo 团队的开源**编码 Agent／CLI 与 harness**；可连接不同模型。 | “MiMo 模型”本身；Agent 仓库开源不自动意味着模型权重开源。 |
| Kimi Code CLI | Moonshot 的新版开源**编码 Agent／CLI 与运行时**；可配置不同 provider。 | Kimi 模型，或逐步退场的旧 `kimi-cli` 仓库。 |

教学上先讲“模型给出什么，运行时决定什么，工具执行什么”，再把三者放进各自层级；不做同类产品功能打分表。

## 候选卡 1：MiMo Code（优先做系统篇）

- **新问题：** 长任务的状态由主 Agent 自己记，还是由 harness 在上下文耗尽前委派独立 writer、写入 checkpoint、重建下一窗口？这能把“上下文压缩”从提示词技巧变成有状态生命周期的工程设计。
- **已核对的第一方证据：** [MIT 仓库与 README](https://github.com/XiaomiMiMo/MiMo-Code)明确定位为基于 OpenCode 的终端编码 Agent，列出项目记忆、checkpoint、历史检索、任务树、子 Agent、MCP 与 Skill；[设计文章](https://mimo.xiaomi.com/blog/mimo-code-long-horizon)解释 computation／memory／evolution 三种时间尺度以及 checkpoint writer、context rebuild；[运行时服务拼装入口](https://github.com/XiaomiMiMo/MiMo-Code/blob/main/packages/opencode/src/effect/app-runtime.ts)可见 SessionPrompt、SessionCheckpoint、Memory、History、MCP、Skill 等服务边界；[会话文档](https://mimo.xiaomi.com/mimocode/sessions)说明会话和 compaction 的用户层行为。
- **目前范围：** 这些是官方声明与可见源码入口；尚未沿具体入口追踪 checkpoint 触发、writer 写盘、失败重试及重建注入的完整代码链，也未运行长会话。设计文章把 Max Mode 标为实验功能，并明确受约束命令式工具调用格式**尚未迁移**；不能把构想写成已上线实现。文章中的成绩和可靠性数字是厂商给出的，未经本书复现。
- **晋级前核查：** 固定仓库 commit 和 MIT 许可文本；沿 `SessionPrompt → SessionCheckpoint → writer → rebuild` 定位关键分支与持久化结构；核对 README、文章、当前代码在功能状态上是否一致；构造一次可复现的跨窗口恢复与异常路径；请第二人审查每个事实箭头。

## 候选卡 2：Kimi Code CLI（优先做系统篇）

- **新问题：** 一次用户请求如何穿过 CLI/TUI、Agent turn loop、provider 抽象、工具审批与持久化事件流；子 Agent 的上下文隔离在哪一层发生？可与 MiMo Code 的 checkpoint 方案对照，但比较维度先限定为会话连续性与控制边界。
- **已核对的第一方证据：** [新版 MIT 仓库](https://github.com/MoonshotAI/kimi-code)将其定义为终端编码 Agent；[仓库模块地图](https://github.com/MoonshotAI/kimi-code/blob/main/AGENTS.md)区分 `apps/kimi-code`、`packages/agent-core`、`agent-core-v2`、`kosong`、`kaos` 等职责；[固定提交的 TurnFlow 源码](https://github.com/MoonshotAI/kimi-code/blob/75a894e9ad5e8d49509664b3daaa1bbc9bb39432/packages/agent-core/src/agent/turn/index.ts)显示一次 turn 的启动、steer 缓冲、取消、工具执行审批与结束续跑入口；[会话与上下文文档](https://moonshotai.github.io/kimi-code/en/guides/sessions)描述 `wire.jsonl`、恢复、压缩和 fork；[子 Agent 文档](https://moonshotai.github.io/kimi-code/en/customization/agents)描述独立上下文与权限继承。
- **目前范围：** 已见一个固定 SHA 的 turn 文件，但尚未确认该提交与当前发布二进制对应，也未打通服务端 v2 路径；文档是会变化的第一方说明，不能用来替代固定源码结论或运行轨迹。[旧 `kimi-cli`](https://github.com/MoonshotAI/kimi-cli) 自称正迁往新版，代码与许可不能混用。
- **晋级前核查：** 选定 release/tag 与完整 commit，记录新版 MIT 许可；从 CLI 入口追到实际启用的 agent-core/v2、provider 调用、工具审批、事件写入与恢复；验证一条正常路径、一条中断／拒绝路径，并说明版本开关；明确旧仓库仅作迁移背景。

## 候选卡 3：Jev（先做机制旁栏，不列编码 Agent 系统篇）

- **新问题：** 在 Agent 的 skill 选择、路由或结果校验中，哪些**有界判断**可交给结构化决策模型，而把阈值、控制流和副作用留在普通代码里？它适合解释“模型能力不等于 Agent 自主性”。
- **已核对的第一方证据：** [TypeSafe 发布文](https://typesafe.ai/blog/introducing-system-one-models-and-jev)把 Jev 定位为 System One 模型；[架构文档](https://docs.typesafe.ai/concepts/how-to-build-with-system-one.md)明确说它不是 Agent，不生成代码或自行选择下一步；[API 快速入门](https://docs.typesafe.ai/introduction/quickstart.md)展示 `state + typed questions → answers`；[Skill 选择 cookbook](https://docs.typesafe.ai/cookbooks/skill_suggestion.md)提供与本书主题直接相关的应用案例；[JavaScript SDK](https://github.com/typesafe-ai/typesafe-sdk-js)与 [Python SDK](https://github.com/typesafe-ai/typesafe-sdk-python) 有 MIT 开源仓库。
- **目前范围：** 官方发布文称模型可避免“幻觉”，只能按**输出 schema 不产生越界字符串或类型错误**理解，绝不能引申为语义判断永不出错。[官方已知问题](https://docs.typesafe.ai/model-jaggedness/jev-1.13.md)承认数学、日期、间接推理、无关长状态、对抗内容等失败方式；[模型页](https://docs.typesafe.ai/models.md)指出英文最强、别名会移动。官方称早期访问；本次未找到第一方公开权重或 Agent 运行时源码，不能声称模型开源，也不能在没有 API 凭据及实验记录时声称实测。发布文和 cookbook 的效果数字均为第一方报告。
- **晋级前核查：** 固定 Jev 模型版本和 SDK commit；复述 cookbook 的任务、样本、对照与评测局限，不直接搬用效果结论；设计一个“低置信度交人工、代码负责最终执行”的小例子；如有合法 API 访问，再做可记录的边界测试，否则保留为文档案例。

## 写作与图稿建议

优先完成 MiMo Code、Kimi Code 的**一条窄源码路径**，各用一张与因果链匹配的图：MiMo 画“checkpoint 写入—窗口重建”的状态／时间图，Kimi 画“turn—审批—工具结果—持久化”的时序图。Jev 只需机制图“有界问题 → 概率 → 代码阈值／人审 → 动作”，不能画成自己调用工具的 Agent。每图另附文字等价说明，固定版本并经过图文交叉审稿后才考虑加入书稿清单。
