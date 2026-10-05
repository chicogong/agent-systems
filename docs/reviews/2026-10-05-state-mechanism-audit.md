# 2026-10-05：状态、记忆与系统文章复核

## 这次完成了什么

通读 8 个系统的主篇与代码导读（16 篇）、机制目录与 14 篇概念文章（15 篇）、对照目录与 6 篇对照（7 篇），共 38 篇 Markdown。每个系统重新打开固定版本的一手源码，核对至少两个核心断言。概念与对照核查重点是角色分工、记忆可见性、委派、权限和恢复；下文列的是本次实际复查范围，不表示每个项目的所有实现都已审计。

随后按读者反馈，对上述 8 系统的 16 篇文章做白话编辑：先讲正常任务，解释谁负责什么，再沿材料、消息或状态说明流程；首次出现的关键英文术语补中文解释，代码导读保持可选。版本与未验证范围尽量集中在篇末，必要的执行授权提醒仍在使用位置。

这是一份源码核查与 AI 编辑记录。没有运行上游模型、数据库或完整 Agent，没有进行真人阅读测试；本次没有重跑书中以往的 Kimi 和 MiMo 模拟测试，也没有提交、推送或部署。

## 怎样核对源码位置

版本来自 sources/systems.json。GitHub raw 页经网页工具转成文本时，会压缩空行，显示行号可能与原文件不同。本次关键锚点通过 GitHub Contents API 取回固定 blob、base64 解码后按物理行号检查。曾因解析后行号怀疑 Kimi 锚点偏移，原文件检查后撤销告警；没有按网页偏移批量改锚点。

## 八个系统的证据

### Kimi Code

- 核对版本：MoonshotAI/kimi-code，75a894e9ad5e8d49509664b3daaa1bbc9bb39432。
- 忙时 steer 收到输入后放入 steerBuffer；下一步 beforeStep 取出并追加为用户消息。[接收与缓冲 L130–143](https://github.com/MoonshotAI/kimi-code/blob/75a894e9ad5e8d49509664b3daaa1bbc9bb39432/packages/agent-core/src/agent/turn/index.ts#L130-L143) · [取出 L265–273](https://github.com/MoonshotAI/kimi-code/blob/75a894e9ad5e8d49509664b3daaa1bbc9bb39432/packages/agent-core/src/agent/turn/index.ts#L265-L273) · [下一步准备 L578–604](https://github.com/MoonshotAI/kimi-code/blob/75a894e9ad5e8d49509664b3daaa1bbc9bb39432/packages/agent-core/src/agent/turn/index.ts#L578-L604)
- 模型准备停时，停止回调先检查新输入，再看目标与 Stop hook；工具执行另接权限回调。[停止检查 L612–669](https://github.com/MoonshotAI/kimi-code/blob/75a894e9ad5e8d49509664b3daaa1bbc9bb39432/packages/agent-core/src/agent/turn/index.ts#L612-L669) · [取消 L205–217](https://github.com/MoonshotAI/kimi-code/blob/75a894e9ad5e8d49509664b3daaa1bbc9bb39432/packages/agent-core/src/agent/turn/index.ts#L205-L217)
- 编辑：用“跑测试时补充要求”讲等待区、下一步和收尾检查；解释 turn、step、steer，保留取消、步数与授权条件。未验证真实交互延迟、并发与取消竞争。

### MiMo Code

- 核对版本：XiaomiMiMo/MiMo-Code，a273d3450ee05ba5163320eae59d7716b778e480。
- writer 总在新子会话运行，目标文件仍按父会话路径计算；成功结束后才推进 last_checkpoint_message_id。[子会话与路径 L943–993](https://github.com/XiaomiMiMo/MiMo-Code/blob/a273d3450ee05ba5163320eae59d7716b778e480/packages/opencode/src/session/checkpoint.ts#L943-L993) · [成功位置标记 L1009–1068](https://github.com/XiaomiMiMo/MiMo-Code/blob/a273d3450ee05ba5163320eae59d7716b778e480/packages/opencode/src/session/checkpoint.ts#L1009-L1068)
- 默认整理阈值按上下文容量分档，与设计文章中的示意比例区分；提前整理和溢出重建分别判断。[默认阈值 L24–58](https://github.com/XiaomiMiMo/MiMo-Code/blob/a273d3450ee05ba5163320eae59d7716b778e480/packages/opencode/src/session/prune.ts#L24-L58)
- 编辑：改为“提前写交接笔记、再换窗口”，解释 writer、watermark、token；修正导读中“路径图省略禁用开关”的旧说法，因为图中已有开关出口。未运行 writer 或完整重建，文件与数据库位置标记的失败一致性仍待测。

### Letta Code

- 核对版本：letta-ai/letta-code，1f55d3dc66e238d203757fae288bb53f3adc7cd3。
- local MemFS 判为 v1，核心块取 system/ 下的 Markdown；非本地且有根 MEMORY.md 才判 v2。[格式与核心范围 L6–29](https://github.com/letta-ai/letta-code/blob/1f55d3dc66e238d203757fae288bb53f3adc7cd3/src/agent/memory-format.ts#L6-L29)
- estimateSystemPromptSize 按格式统计核心文件，用 UTF-8 字节数除以 4 粗估 token。内置提示区分核心块、外部文件与历史 recall。[容量估计](https://github.com/letta-ai/letta-code/blob/1f55d3dc66e238d203757fae288bb53f3adc7cd3/src/agent/system-prompt-size.ts#L1-L106) · [内置提示 L8–55](https://github.com/letta-ai/letta-code/blob/1f55d3dc66e238d203757fae288bb53f3adc7cd3/src/agent/prompts/letta_local_memfs.md#L8-L55)
- 编辑：以“工作台上的常用信息、参考手册和过去对话”讲取用方式，保留文件、Git、同步与提示重编译的区别。没有验证模型实际可见内容或跨设备同步。

### Mem0

- 核对版本：mem0ai/mem0，f8082a7345dadd9e042ebbc40b57b1498c8f6d63。
- 同步 infer=True 分支提取事实、embedding、对本次读到的记录及批次排重，再尝试新增；逐条插入失败只记日志，构造的返回记录仍可能保留。[提取与插入 L955–1076](https://github.com/mem0ai/mem0/blob/f8082a7345dadd9e042ebbc40b57b1498c8f6d63/mem0/memory/main.py#L955-L1076)
- 默认检索候选来自语义搜索；排序先过语义阈值，再叠加可用的关键词与实体分数。[候选 L1628–1690](https://github.com/mem0ai/mem0/blob/f8082a7345dadd9e042ebbc40b57b1498c8f6d63/mem0/memory/main.py#L1628-L1690) · [排序 L60–139](https://github.com/mem0ai/mem0/blob/f8082a7345dadd9e042ebbc40b57b1498c8f6d63/mem0/utils/scoring.py#L60-L139)
- 编辑：从一句用户偏好讲写入与找回，解释 embedding、BM25、top_k，用“先入围、再加分”讲排序。保留故障读回提醒。提取质量、适配器行为及结果进入模型后的效果尚未运行检查。

### LangGraph

- 核对版本：langchain-ai/langgraph，bdb85b5aa87a21de68371d2e534b81aeed398f57。
- InMemorySaver 按 thread、namespace、checkpoint ID 存储；指定 ID 精确读取，省略时取最新；新版本记录旧 ID 为 parent。[读取 L230–309](https://github.com/langchain-ai/langgraph/blob/bdb85b5aa87a21de68371d2e534b81aeed398f57/libs/checkpoint/langgraph/checkpoint/memory/__init__.py#L230-L309) · [保存与父版本 L421–466](https://github.com/langchain-ai/langgraph/blob/bdb85b5aa87a21de68371d2e534b81aeed398f57/libs/checkpoint/langgraph/checkpoint/memory/__init__.py#L421-L466)
- StateSnapshot 保存值、待做节点和版本配置；durability 默认 async，sync 在下一步前保存，exit 在退出时保存；内存示例明确用于调试和测试。[快照字段 L711–729](https://github.com/langchain-ai/langgraph/blob/bdb85b5aa87a21de68371d2e534b81aeed398f57/libs/langgraph/langgraph/types.py#L711-L729) · [保存时机 L2705–2711](https://github.com/langchain-ai/langgraph/blob/bdb85b5aa87a21de68371d2e534b81aeed398f57/libs/langgraph/langgraph/pregel/main.py#L2705-L2711) · [示例用途 L33–44](https://github.com/langchain-ai/langgraph/blob/bdb85b5aa87a21de68371d2e534b81aeed398f57/libs/checkpoint/langgraph/checkpoint/memory/__init__.py#L33-L44)
- 编辑：从“查资料后调整写作要求”说明取旧进度、建立新分支，解释 graph、thread、checkpoint、saver、superstep。外部动作对账仍保留。未运行分支测试、生产数据库或故障恢复。

### OpenClaw

- 核对版本：openclaw/openclaw，b373c9a9bcd4954ccdab963e3ed71336302b82be。
- 显式 sessionKey 与 agentId 的归属冲突、退役所有者等在解析时检查；会话准备后，再以规范化目标检查创建与修改权限。[归属解析 L112–207](https://github.com/openclaw/openclaw/blob/b373c9a9bcd4954ccdab963e3ed71336302b82be/src/gateway/session-request-agent.ts#L112-L207) · [最终目标授权 L279–334](https://github.com/openclaw/openclaw/blob/b373c9a9bcd4954ccdab963e3ed71336302b82be/src/gateway/agent-turn/agent-turn-service.ts#L279-L334)
- 调度准备返回可继续的结果后，才调用 startAgentRunExecution。[派发交接 L557–585](https://github.com/openclaw/openclaw/blob/b373c9a9bcd4954ccdab963e3ed71336302b82be/src/gateway/agent-turn/agent-turn-service.ts#L557-L585)
- 编辑：用两个助手会话解释“找归属—定目标—授权—派发”，解释 Gateway、RPC、owner、canonical key。仍限定显式 key 路径，未运行 Gateway、渠道入站或并发重试。

### GPT Researcher

- 核对版本：assafelovic/gpt-researcher，6f998577d547b1e54ec662dac63583aa11e3b84b。
- Hybrid 两路并行获取内容；文档为空时，一路也可转网页；汇合调用提示模板的拼接方法。[并行 L172–186](https://github.com/assafelovic/gpt-researcher/blob/6f998577d547b1e54ec662dac63583aa11e3b84b/gpt_researcher/skills/researcher.py#L172-L186) · [空文档回退 L595–606](https://github.com/assafelovic/gpt-researcher/blob/6f998577d547b1e54ec662dac63583aa11e3b84b/gpt_researcher/skills/researcher.py#L595-L606)
- 非 Granite 拼接无条件添加两个标签；写作器仅检查去空白后非空。从条件可推得“只剩标签也可通过检查”的风险，没有实际触发或测得虚假引文。[拼接 L564–566](https://github.com/assafelovic/gpt-researcher/blob/6f998577d547b1e54ec662dac63583aa11e3b84b/gpt_researcher/prompts.py#L564-L566) · [空内容保护 L77–88](https://github.com/assafelovic/gpt-researcher/blob/6f998577d547b1e54ec662dac63583aa11e3b84b/gpt_researcher/skills/writer.py#L77-L88) · [Granite 另一格式 L756–834](https://github.com/assafelovic/gpt-researcher/blob/6f998577d547b1e54ec662dac63583aa11e3b84b/gpt_researcher/prompts.py#L756-L834)
- 编辑：从手头材料加网页的调研开始，依次讲收集、整理和写作，引用核查集中于交稿检查。未运行检索器、模型或真实报告验收。

### Hermes

- 核对版本：NousResearch/hermes-agent，a9109b07f42685f88397008d0d5a6c3d481b3b28。
- 内置存储保留当前条目和加载时提示快照；普通写入更新条目，format_for_system_prompt 仍返回快照。[加载与容量 L88–164](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/tools/memory_tool_store.py#L88-L164) · [修改顺序 L245–274](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/tools/memory_tool_store.py#L245-L274) · [快照读取 L463–481](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/tools/memory_tool_store.py#L463-L481)
- 无人值守复查的 replace/remove 操作先走额外暂存门禁；Skill 审批门禁在动作处理前返回 blocked 或 staged，且导入失败时存在 fail-open 分支。[后台门禁 L167–204](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/tools/memory_tool.py#L167-L204) · [Skill 门禁 L618–648](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/tools/skill_manager_tool.py#L618-L648)
- 新发现：落盘失败与审批拒绝要分开。记忆先改当前条目再原子写文件；Skill 一条路径先写文件再扫描，扫描拒绝时尝试恢复。原子替换防止半截文件，不是内存、磁盘、回包和整个知识操作的总事务。[文件 helper L264–326](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/utils.py#L264-L326) · [写后扫描与恢复 L350–369](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/tools/skill_manager_tool.py#L350-L369)
- 编辑：以便签和参考手册解释两类知识、用照片解释提示快照；新增报错后读回提醒。已向图稿负责人建议把“拒绝/失败→不写”收紧为“审批拒绝→不提交；失败→读回核对”。未运行写入失败、审批交互、提示刷新或复查任务。

## 概念与对照的复查范围

以下文章在本次通读；概念与对照的白话重写由主协调者另行安排。本报告保留本次选点核查，不将它扩写成每个项目的运行结论。

| 文章 | 本次核查依据与结论 | 仍未验证 |
| --- | --- | --- |
| agent-loop | [Anthropic 架构说明](https://www.anthropic.com/engineering/building-effective-agents)：工具结果进入下一次决策，宿主安排循环 | 各系统完整循环实测 |
| model-harness-cli-mcp-skill | [Claude Code Skills](https://code.claude.com/docs/en/skills)、[MCP Tools 规范](https://modelcontextprotocol.io/specification/2025-11-25/server/tools)：工作方法、协议和宿主执行分开；allowed-tools 有宿主权限含义 | 产品全部附加字段及所有宿主实现 |
| agent-workflow-multiagent | [Anthropic 模式说明](https://www.anthropic.com/engineering/building-effective-agents)：预定路径与动态决策按控制方式区分 | 多执行者同任务效果比较 |
| context-vs-memory | 上述 Letta、Mem0、LangGraph 固定源码：存储对象与本轮模型输入各有路径 | 真正请求的可见内容与效果 |
| session-compaction-and-memory | Letta、MiMo 的固定路径：保存历史、整理摘要与组织当前输入分别处理 | Pi 压缩由另一组负责；跨窗口实测未做 |
| approval-vs-sandbox | [OpenAI 安全说明](https://learn.chatgpt.com/docs/agent-approvals-security)：审批与操作系统隔离分别控制，联网工具还要看各自策略 | 不同平台的实际配置和隔离测试 |
| extensibility-layers | Skills 官方说明与固定 Hermes 写入/读取：方法正文、宿主扩展和实际工具调用分别查看 | Pi 扩展由另一组负责，未审计所有加载器 |
| mcp-skill-tool-lifecycle | MCP 工具错误使用 isError；Claude allowed-tools 可在调用轮预授权，权限持续时间与正文持续时间不同 | 没有调用远端 MCP 或实际安装 Skill |
| jev-and-system-one | [TypeSafe 置信度](https://docs.typesafe.ai/confidence)、[SDK 快速开始](https://docs.typesafe.ai/introduction/quickstart)：Choice.confidence 是分布集中度，教学阈值需调校 | 没有调用 Jev、测延迟或分类质量 |
| delegation-and-handoff | [固定 Send 定义 L732–804](https://github.com/langchain-ai/langgraph/blob/bdb85b5aa87a21de68371d2e534b81aeed398f57/libs/langgraph/langgraph/types.py#L732-L804)：动态输入分发与示例列表聚合；合同、授权和对账是应用设计 | 多 Agent 故障、冲突和交接实验 |
| interruption-recovery | LangGraph 保存时机、[AWS 幂等与迟到请求](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/)、[Stripe 幂等合同](https://docs.stripe.com/api/idempotent_requests) | Pi 取消路径由另一组负责，未做外部 API 故障注入 |
| observation-evaluation | [OpenTelemetry trace](https://opentelemetry.io/docs/concepts/signals/traces/)、[LangSmith 评测](https://docs.langchain.com/langsmith/evaluation-concepts)：执行观察与带参考样本的评测用途不同 | 本书所有评测器及实际用户验收 |
| sandbox-execution | [gVisor 架构](https://gvisor.dev/docs/architecture_guide/intro/)、[Firecracker 固定设计 L78–102](https://github.com/firecracker-microvm/firecracker/blob/edb60617c31ebd610c530f67706ec5c79d4c2725/docs/design.md#L78-L102)、[Daytona 生命周期](https://www.daytona.io/docs/en/sandboxes/)、[E2B 持久化](https://docs.e2b.dev/sandbox/persistence)：隔离层和暂停/停止保留范围分别判断；Firecracker 的网络出口过滤交给宿主 | 未安装运行时、做逃逸或资源限制测试 |
| computer-and-browser-use | 通读，检查观察内容、宿主动作与账户身份的区分 | Browser Use 等项目细节由另一组复核；未操作真实账户 |
| comparisons/README | 已写成六篇对照；移除“计划中的首批问题”的过时语气 | 没有新增排行榜 |
| loop-and-stop | 重查 Kimi 的步数与停止回调；比较限定各自固定路径 | Pi、mini-SWE-agent、OpenCode 由另一组负责，未同任务实测 |
| persisted-vs-visible | 重查 Letta 核心范围及内置提示，与当前输入区分 | 运行可见性仍待测 |
| four-kinds-of-state | Letta、Mem0、LangGraph 的保存与取用边界均有上述固定依据 | 不将保存成功当作学习效果 |
| claude-code-codex | Claude Skill 权限与 OpenAI 审批/隔离官方文档；保留两侧证据粒度不同 | Codex 固定执行路径由另一组负责 |
| permission-and-recovery | 与中断恢复篇统一可信终态与有效幂等重放的要求 | 外部动作真实对账与重试待测 |
| completion-and-evidence | Kimi completed 表示回合正常结束；文章另列工具、产物和验收 | 没有真人任务验收 |

## 此前的小修与后续分工

- interruption-recovery：补充一次查无记录可能是查询滞后或请求仍在途；安全重发要有可靠终态或有效幂等合同，同一键配同一参数并核对有效期。引用 AWS 与 Stripe 一手说明。
- mcp-skill-tool-lifecycle：把“展开下一行”改为“看下方答案”，与普通 Markdown 显示一致。
- comparisons/README：把“计划中的首批问题”改为现有对照介绍。后续这些目录由主协调者接手，未继续修改。
- 后续重点：独立复读白话版本，查看长段落在网页与 PDF 中的可读性；图稿收紧 Hermes 失败出口；再以隔离合成数据选择性验证关键路径。代码校验通过不代替这些阅读与运行检查。

## 本地检查

- 本次编辑路径的 git diff --check：通过。
- python3 scripts/check_repo.py：Figure bundles and local Markdown links: OK。
- 这些是格式、图稿文件组合及本地链接检查。未执行整书 PDF 导出、图像视觉验收、站点部署或外部读者测试。
