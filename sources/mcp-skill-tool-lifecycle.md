# 来源台账：Skill、MCP 与工具权限生命周期

核对日期：2026-09-23。范围：`docs/concepts/mcp-skill-tool-lifecycle.md` 的机制教程。示例 `KB-142`、`fix-from-kb`、`kb.search`、`kb.fetch` 和文件名均为虚构；无运行观察，无第三方源码复制。MCP 术语固定在 **2025-11-25** 规范版本；产品文档是核对当日的公开页面，可能继续变化。

| 关键主张 | 类型 | 第一方定位 | 范围与限制 |
| --- | --- | --- | --- |
| Host 管理 Client、连接权限及上下文；Client 与 Server 连接，Server 暴露能力 | 规范声明 | [MCP 架构 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25/architecture) | 不等于 Claude Code 或 Codex 的内部类图。 |
| 2025-11-25 连接先初始化/协商，再操作和关闭 | 规范声明 | [MCP 生命周期 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25/basic/lifecycle) | 后续草案可能更改生命周期；正文仅限定此版本。 |
| Server 声明 Tools；Client 用 `tools/list` 发现、`tools/call` 调用；结果可有 `isError` | 规范声明 | [MCP Tools 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25/server/tools) | 工具名、参数及实际权限由具体 Server/Host 决定。该页还区分协议错误与工具执行错误、提醒 Tool annotations 的信任边界。 |
| 官方 TypeScript SDK 用 `registerTool` 注册 Tool，返回 `content`/`structuredContent` | SDK 文档声明 | [MCP TypeScript SDK v1 Server](https://ts.sdk.modelcontextprotocol.io/server) | 本篇没有运行 SDK 或复制 SDK 示例代码；用它交叉核对 Tool 是 Server 暴露的可调用操作。 |
| Skill 提供按需使用的任务指导；Claude Code 常规会话先给描述、调用时加载正文；Codex 先给名称/描述/路径、选用后读取正文 | 产品文档声明 | [Claude Code Skills](https://code.claude.com/docs/en/skills)；[Codex Skills](https://learn.chatgpt.com/docs/build-skills) | Claude Code 有调用方式、预加载等例外，`allowed-tools` 可在当前轮授予指定工具权限；不能把两产品视为同一加载器。 |
| Claude Code 的 Tool 权限有 allow/ask/deny 规则，MCP 连接需审查外部内容风险 | 产品文档声明 | [Claude Code permissions](https://code.claude.com/docs/en/permissions)；[Claude Code MCP](https://code.claude.com/docs/en/mcp) | 只描述文档中的用户可配置行为，不推断闭源实现顺序。 |
| Codex 的审批与沙箱是不同控制点，支持 MCP Server 配置 | 产品文档声明 | [Codex approvals and security](https://learn.chatgpt.com/docs/agent-approvals-security)；[Codex MCP](https://learn.chatgpt.com/docs/extend/mcp?surface=cli) | 配置取决于实际运行环境；本篇没有核验某次运行的有效策略。 |
| MCP 安全控制需要在连接、授权与 Server 行为上落实 | 官方安全指导 | [MCP Security Best Practices](https://modelcontextprotocol.io/docs/2025-11-25/tutorials/security/security_best_practices) | 正文的多控制点建议属于工程推断，不声称规范自动实现所有防线。 |

## 推断与未验证

- **工程推断**：把知识库结果当任务数据、在本地修改后核对 diff 与测试、遇到未知结果先对账，是从信任边界和副作用分离推得的操作方法，不是 MCP 统一要求的 Agent 工作流。
- **未知**：具体知识库 Server 的工具契约、授权、重试/幂等语义；某个 Claude Code 或 Codex 安装的生效配置；示例任务在真实仓库中的修复结果。
- **待做的独立复核**：由第二位审稿者重开上表链接，检查协议版本及每条事实箭头；另用隔离练习环境验证拒绝、超时、提示注入和测试失败路径。本文没有把静态文档阅读当成实测。
