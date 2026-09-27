# 从零开始读懂 Agent 系统

[返回首页](../README.md) · [术语表](glossary.md) · [当前书稿范围](roadmap.md)

Agent 可以先理解为一个反复执行的过程：接收目标，依据已有信息决定下一步，调用工具，观察结果，再决定继续、停止或请人处理。本书按**机制问题**组织阅读；项目是回答问题的实例，不是性能或流行度排行榜。下面四层可以顺读，也可以从自己正遇到的问题进入。

不用先会搭框架。前两层可只读图、画纸笔流程；要运行练习才需要 Python 3.10 或更新版本。文中的**宿主**指组织模型与工具的程序，**提案**是尚未执行的下一步建议，**副作用**是文件或外部服务实际发生的变化。先把这三个角色分开，再学习接口名称。

## 1. 零基础：认出循环和控制权

**要回答：** 模型的一次回答，何时变成了能影响外部世界的动作？先只读本书的 [Agent loop](concepts/agent-loop.md)，再做[本地 Agent loop 练习](labs/first-agent-loop.md)；读懂提案、授权、执行和验收后，再回头看[五层职责](concepts/model-harness-cli-mcp-skill.md)。想看更多例子，可选读 [Hugging Face Agents Course 第一单元](https://huggingface.co/learn/agents-course/unit1/introduction) 的 Think → Act → Observe 示例，以及 [Anthropic 的 Agent 构建模式](https://www.anthropic.com/engineering/building-effective-agents) 对固定工作流与动态 Agent 的区分。外部课是延伸阅读，不是完成本书第一层的前置条件。

**动手：** 拿“查询天气并写一句出门建议”画四格：用户目标、模型提出的工具调用、工具返回的天气、最终建议。在每条箭头旁写谁决定它。再把天气工具改成“发送消息”，标出需要增加的授权检查。纸笔即可，不必运行模型。随后运行[本地 Agent loop 练习](labs/first-agent-loop.md)，亲眼比较获准写入、写入被拒与写错配置三条轨迹；它只用 Python 标准库和固定脚本模拟提案，不需要模型账号。

**验收：** 你能指出工具返回错误时下一轮由谁发起，也能解释为什么把“请小心”写进模型输入仍不能代替宿主在执行前拒绝一次写入。对照答案：练习中的 `run()` 把错误结果交给 `propose()`；提案函数据此提出停止。提示词影响提案，真正阻止文件写入的是宿主没有调用执行函数。

## 2. 能用工具：区分接口、指令和执行边界

**要回答：** 工具是怎样被发现、授权和执行的？先读本书的 [Skill、MCP 与工具权限接力](concepts/mcp-skill-tool-lifecycle.md)和 [Codex 执行与审批](systems/codex/README.md)，再对照 [MCP 的 Host／Client／Server 架构规范](https://modelcontextprotocol.io/specification/2025-11-25/architecture)与 [Agent Skills 格式规范](https://github.com/agentskills/agentskills/blob/main/docs/specification.mdx)。MCP 解释外部能力怎样接入；Skill 是按需加载的操作说明；Codex 案例帮助把模型提议、审批和沙箱执行画在不同位置。这三者解决的问题不同。

**动手：** 为一个只读文件搜索工具写一张卡片：输入、输出、错误、调用者、允许目录。再设计一个 `SKILL.md`，说明何时使用它和如何核对搜索结果。最后把工具改成写文件，补上审批点、可写范围和失败后的核对动作。不要在真实仓库执行写入。

**验收：** 你能把“模型看得见某工具”“用户允许这次调用”“操作系统允许访问该文件”说成三件事。对照检查：宿主把工具描述提供给模型；用户或既定策略决定许可，宿主执行这道门禁；操作系统及执行环境约束实际文件访问。可见不等于获准，获准也不等于操作一定成功。

## 3. 读源码：沿一条窄路径追到停止条件

进入项目之前，可先做[上下文预算练习](labs/context-budget.md)：同样保存的五条记录、同样的输入预算，选择新近记录与优先检索旧约束会产生不同输入。用 `stored_records`、`visible_ids`、`context` 和 `audit` 分别核对，回答“记录还在，为什么这轮看不见”。它不使用真实模型，也不测量 token；读完后再看项目的会话投影与记忆检索，更容易找到各自的边界。

**要回答：** 一次请求具体怎样穿过运行循环、工具和会话？从本书的 [Pi 局部剖面](systems/pi/README.md) 和[官方源码](https://github.com/earendil-works/pi)开始；它把模型接口、Agent 核心与交互外壳分开，适合第一次追调用链。接着选一个不同取舍：[mini-SWE-agent](systems/mini-swe-agent/README.md) 用简短消息账本说明停止契约；[OpenCode](systems/opencode/README.md) 区分工具调用状态与会话状态；[Kimi Code](systems/kimi-code/README.md) 展示忙时 steer 缓冲与 step 边界续跑；[MiMo Code](systems/mimo-code/README.md) 展示长任务 checkpoint 与重建。它们的官方源码入口依次是 [SWE-agent](https://github.com/SWE-agent/mini-swe-agent)、[Anomaly](https://github.com/anomalyco/opencode)、[MoonshotAI](https://github.com/MoonshotAI/kimi-code) 和 [XiaomiMiMo](https://github.com/XiaomiMiMo/MiMo-Code)。每次只选**一个**差异阅读，不必把五个仓库从头读完。

**动手：** 任选一个项目，从本书给出的固定 commit 打开三个源码位置：请求入口、工具结果写回、结束或继续的分支。用不超过八步写出正常路径，再提出一个可证伪的问题，例如“工具超时后会不会重复写入？”找不到代码或运行证据时写“未知”。

**验收：** 每个实现断言都能指回固定版本的文件；你不会把静态阅读写成实测，也不会把后来版本的功能补进旧图。项目的源码链接和已读范围以各剖面及[来源台账](../sources/README.md)为准。

## 4. 做工程：让状态、证据和恢复可检查

**要回答：** 任务暂停、跨轮记忆、并行研究和外部副作用怎样对账？按问题选读：[LangGraph checkpoint](systems/langgraph/README.md) 看暂停与恢复；[Letta Code 记忆](systems/letta/README.md) 看已存信息与本轮可见上下文的差别；[GPT Researcher](systems/gpt-researcher/README.md) 看检索材料怎样进入报告；[Microsoft Agent Framework](https://github.com/microsoft/agent-framework) 看显式 workflow 和多执行者编排。前三项的官方源码分别在 [LangGraph](https://github.com/langchain-ai/langgraph)、[Letta Code](https://github.com/letta-ai/letta-code) 和 [GPT Researcher](https://github.com/assafelovic/gpt-researcher)。框架并不会替应用自动证明“写入只发生一次”或“结论有来源支持”。

**动手：** 设计一个“搜三份资料并写摘要”的小任务合同，写出允许的来源、每一步产物、引用位置、最长运行时间和停止条件。在“抓取完成后、摘要保存前”假设进程崩溃，分别记录已完成、未完成、结果未知的动作。对结果未知的外部写入安排读回或人工对账，再考虑重试。

**验收：** 你能分别展示任务结果、工具轨迹、来源证据和恢复记录；其中任何一项缺失，都不把任务标为已验证。进一步的缺口和发布门槛看[路线页](roadmap.md)。

**再做一次最小实验：** 先完成第一层的本地练习，再运行[回执丢失后的对账练习](labs/remote-effect.md)。不必先读完本层列出的几个项目：实验沿用“宿主根据证据决定下一步”，只新增远端服务账本和稳定操作 ID。它用四条可重复轨迹说明：操作已发出、收到回执、远端实际接受是三件事；查询不可用时应停在“未知”，而不是盲重试。两个程序彼此独立，不共享配置或运行记录。

## 怎样继续选材料

读完四层后，用“它能解释哪一个尚未讲清的取舍”选下一项。截至 **2026-09-23**，[AutoGen 官方 README](https://github.com/microsoft/autogen/blob/main/README.md)将项目标为维护模式，适合作编排演进史；[CrewAI](https://github.com/crewAIInc/crewAI)可辅助比较 Crew 与 Flow。两者不需要替代已完成的源码练习。[Claude Code](https://code.claude.com/docs/en/how-claude-code-works)可作官方公开行为对照，其公开仓库不等于完整 CLI 源码；[Jev 官方文档](https://docs.typesafe.ai/introduction)讲有类型的判断层，不是完整 Agent。速度、成本和判断质量需用自己的任务独立验证。

以上链接用于阅读，不授予复制代码、图片或教程的权利。**上游素材许可、具体版本与维护状况在复用或公开前逐项核对；未核实的记为待核。** 本书系统篇是固定版本的局部源码阅读，尚未运行验证的结论会单独标明。
