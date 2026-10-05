# 一项任务怎样把模型和工具接起来

沿着“读工单、修代码”的例子看这张图，几种组件就容易认清了。工单就是记录问题和修复要求的任务单。

1. 你从 CLI（命令行界面）或 IDE（开发环境）交代任务。
2. Harness，也就是安排模型和工具的运行器，准备这次输入并调用模型。模型建议先读工单。
3. 宿主检查可用工具和实际权限，把读取请求交给工具。这个例子的工单工具由 MCP Server 提供，它是可以运行在本机或远端的工具服务；本地读取工具也可以直接调用。
4. 工具带回工单原文，运行器把它放进下一次模型输入，模型据此继续修复。需要方法时，再读取 Skill 提供的工作指导。

图中“宿主程序／检查权限”指的是第三步。执行权限来自宿主、工具凭据和具体设置；Skill 的指导本身只提供方法。有些运行器另有审批和沙箱，有些主要继承启动进程的权限，使用前要分别检查。

虚线框圈出一轮处理过程。框里的角色可以分布在不同进程中。这张图用模型建议读取的路径讲分工；程序也可以提前读取资料，再调用模型，那是另一种安排。

这是帮助学习的概念图。它只画最小路径，审批细节、连接握手、历史保存和失败重试可接着读[审批与沙箱](../../docs/concepts/approval-vs-sandbox.md)、[扩展层](../../docs/concepts/extensibility-layers.md)。

## 对照来源

[Claude Code 如何工作](https://code.claude.com/docs/en/how-claude-code-works)、[OpenAI Sandbox Agents 的 harness/compute 边界](https://developers.openai.com/api/docs/guides/agents/sandboxes)、[Codex 的扩展层说明](https://developers.openai.com/codex/concepts/customization)、[MCP 协议架构](https://modelcontextprotocol.io/specification/2025-11-25/architecture)。实际产品可能用不同名称，或把几种职责放进同一个进程；闭源产品的内部函数仍以公开资料为限。
