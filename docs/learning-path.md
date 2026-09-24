# 从零开始读懂 Agent 系统

[返回首页](../README.md) · [术语表](glossary.md) · [当前书稿范围](roadmap.md)

Agent 可以先理解为一个反复执行的过程：接收目标，依据已有信息决定下一步，调用工具，观察结果，再决定继续、停止或请人处理。本书按**机制问题**组织阅读；项目是回答问题的实例，不是性能或流行度排行榜。下面四层可以顺读，也可以从自己正遇到的问题进入。

教程与站外文档链接可能搬家或改版；本书对系统的事实断言以[来源台账](../sources/README.md)与各篇固定的上游 commit 为准，不以临时外链为准。

## 1. 零基础：认出循环和控制权

**要回答：**模型的一次回答，何时变成了能影响外部世界的动作？先读本书的 [Agent loop](concepts/agent-loop.md) 和 [五层职责](concepts/model-harness-cli-mcp-skill.md)，再读 [Hugging Face Agents Course 第一单元](https://huggingface.co/learn/agents-course/unit1/introduction) 的 Think → Act → Observe 示例，以及 [Anthropic 的 Agent 构建模式](https://www.anthropic.com/engineering/building-effective-agents) 对固定工作流与动态 Agent 的区分。前者适合看清最小循环，后者帮助判断什么时候需要多一步路由、并行或委派。

**动手：**拿“查询天气并写一句出门建议”画四格：用户目标、模型提出的工具调用、工具返回的天气、最终建议。在每条箭头旁写谁决定它。再把天气工具改成“发送消息”，标出需要增加的授权检查。纸笔即可，不必运行模型。想看一条可复跑的授权、拒绝与验收轨迹，可接着试读[本地 Agent loop 练习](labs/first-agent-loop.md)：它只用 Python 标准库和固定脚本模拟提案，尚未收入本书 PDF。

**验收：**你能指出工具返回错误时下一轮由谁发起，也能解释为什么提示词里的“请小心”不能代替执行权限。

## 2. 能用工具：区分接口、指令和执行边界

**要回答：**工具是怎样被发现、授权和执行的？先读本书的 [Skill、MCP 与工具权限接力](concepts/mcp-skill-tool-lifecycle.md)和 [Codex 执行与审批](systems/codex/README.md)，再对照 [MCP 的 Host／Client／Server 架构规范](https://modelcontextprotocol.io/specification/2025-11-25/architecture)与 [Agent Skills 格式规范](https://github.com/agentskills/agentskills/blob/main/docs/specification.mdx)。MCP 解释外部能力怎样接入；Skill 是按需加载的操作说明；Codex 案例帮助把模型提议、审批和沙箱执行画在不同位置。这三者解决的问题不同。

**动手：**为一个只读文件搜索工具写一张卡片：输入、输出、错误、调用者、允许目录。再设计一个 `SKILL.md`，说明何时使用它和如何核对搜索结果。最后把工具改成写文件，补上审批点、可写范围和失败后的核对动作。不要在真实仓库执行写入。

**验收：**你能把“模型看得见某工具”“用户允许这次调用”“操作系统允许访问该文件”说成三件事，并指出各自的执行者。

## 3. 读源码：沿一条窄路径追到停止条件

**要回答：**一次请求具体怎样穿过运行循环、工具和会话？从本书的 [Pi 局部剖面](systems/pi/README.md) 和[官方源码](https://github.com/earendil-works/pi)开始；它把模型接口、Agent 核心与交互外壳分开，适合第一次追调用链。接着选一个不同取舍：[mini-swe-agent](systems/mini-swe-agent/README.md) 用简短消息账本说明停止契约；[OpenCode](systems/opencode/README.md) 区分工具调用状态与会话状态；[Kimi Code](systems/kimi-code/README.md) 展示忙时 steer 缓冲与 step 边界续跑；[MiMo Code](systems/mimo-code/README.md) 展示长任务 checkpoint 与重建。它们的官方源码入口依次是 [SWE-agent](https://github.com/SWE-agent/mini-swe-agent)、[Anomaly](https://github.com/anomalyco/opencode)、[MoonshotAI](https://github.com/MoonshotAI/kimi-code) 和 [XiaomiMiMo](https://github.com/XiaomiMiMo/MiMo-Code)。每次只选**一个**差异阅读，不必把五个仓库从头读完。

**动手：**任选一个项目，从本书给出的固定 commit 打开三个源码位置：请求入口、工具结果写回、结束或继续的分支。用不超过八步写出正常路径，再提出一个可证伪的问题，例如“工具超时后会不会重复写入？”找不到代码或运行证据时写“未知”。

**验收：**每个实现断言都能指回固定版本的文件；你不会把静态阅读写成实测，也不会把后来版本的功能补进旧图。项目的源码链接和已读范围以各剖面及[来源台账](../sources/README.md)为准。

## 4. 做工程：让状态、证据和恢复可检查

**要回答：**任务暂停、跨轮记忆、并行研究和外部副作用怎样对账？按问题选读：[LangGraph checkpoint](systems/langgraph/README.md) 看暂停与恢复；[Letta Code 记忆](systems/letta/README.md) 看已存信息与本轮可见上下文的差别；[GPT Researcher](systems/gpt-researcher/README.md) 看检索材料怎样进入报告；[Microsoft Agent Framework](https://github.com/microsoft/agent-framework) 看显式 workflow 和多执行者编排。前三项的官方源码分别在 [LangGraph](https://github.com/langchain-ai/langgraph)、[Letta Code](https://github.com/letta-ai/letta-code) 和 [GPT Researcher](https://github.com/assafelovic/gpt-researcher)。框架并不会替应用自动证明“写入只发生一次”或“结论有来源支持”。

**动手：**设计一个“搜三份资料并写摘要”的小任务合同，写出允许的来源、每一步产物、引用位置、最长运行时间和停止条件。在“抓取完成后、摘要保存前”假设进程崩溃，分别记录已完成、未完成、结果未知的动作。对结果未知的外部写入安排读回或人工对账，再考虑重试。

**验收：**你能分别展示任务结果、工具轨迹、来源证据和恢复记录；其中任何一项缺失，都不把任务标为已验证。进一步的缺口和发布门槛看[路线页](roadmap.md)。

## 怎样继续选材料

读完四层后，用“它能解释哪一个尚未讲清的取舍”选下一项。截至 **2026-09-23**，[AutoGen 官方 README](https://github.com/microsoft/autogen/blob/main/README.md)将项目标为维护模式，适合作编排演进史；[CrewAI](https://github.com/crewAIInc/crewAI)可辅助比较 Crew 与 Flow。两者不需要替代已完成的源码练习。[Claude Code](https://code.claude.com/docs/en/how-claude-code-works)可作官方公开行为对照，其公开仓库不等于完整 CLI 源码；[Jev 官方文档](https://docs.typesafe.ai/introduction)讲有类型的判断层，不是完整 Agent。速度、成本和判断质量需用自己的任务独立验证。

以上链接用于阅读，不授予复制代码、图片或教程的权利。**上游素材许可、具体版本与维护状况在复用或公开前逐项核对；未核实的记为待核。**本书系统篇是固定版本的局部源码阅读，尚未运行验证的结论会单独标明。
