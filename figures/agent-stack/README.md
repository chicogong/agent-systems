# 一项任务穿过哪些边界

这是一张**生成式编码 Agent 的教学抽象图**，不是某个产品的进程图，也不适用于每一种模型。任务可从 CLI 或 IDE 输入；harness 装配本轮上下文、调用模型、处理模型建议的动作，并按具体实现的执行策略路由工具。图中“权限与路由”表示必须查清谁拥有执行权，**不保证每个 Harness 都内建独立审批或沙箱**；有些实现只继承宿主进程权限。工具结果回到下一轮上下文。Skill 提供按需读取的流程知识；MCP 是连接外部能力的一种协议，而不是所有工具调用都必须经过的通道。模型和外部服务都不因为出现在图中而自动拥有执行权限。

主图仅画一轮最小路径。它省略了用户审批的交互细节、MCP Host/Client/Server 的内部握手、不同产品的会话持久化和失败重试；这些应分别读[审批与沙箱](../../docs/concepts/approval-vs-sandbox.md)、[扩展层](../../docs/concepts/extensibility-layers.md)。

图的抽象依据：[Claude Code 如何工作](https://code.claude.com/docs/en/how-claude-code-works)、[OpenAI Sandbox Agents 的 harness/compute 边界](https://developers.openai.com/api/docs/guides/agents/sandboxes)、[Codex 的扩展层说明](https://developers.openai.com/codex/concepts/customization)、[MCP 协议架构](https://modelcontextprotocol.io/specification/2025-11-25/architecture)。具体产品可能不用这些名称，也可能将不同职责放进同一进程；箭头只表示职责顺序，不宣称公开了闭源内部调用栈。
