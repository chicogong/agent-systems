# 按机制学习

[返回首页](../../README.md)

按“问题 → 图 → 简短解释 → 真实案例 → 失败或反例”阅读。以下是计划主题，尚未完成的页面不预建空文件。

1. [模型、Harness、CLI、Skill、MCP：究竟换了哪一层？](model-harness-cli-mcp-skill.md)
2. [Agent、工作流与多 Agent：谁决定下一步？](agent-workflow-multiagent.md)
3. [Agent loop 与工具调用：一次行动从请求到观察怎样闭环？](agent-loop.md)
4. [状态与上下文：存着不等于本轮模型看见](context-vs-memory.md)。
5. [会话、压缩与记忆：哪些内容保留，哪些只在需要时检索？](session-compaction-and-memory.md)
6. [审批、沙箱、工作目录：三个不同的边界](approval-vs-sandbox.md)。
7. [Tool、Skill、Extension、Package、MCP：到底扩展了什么？](extensibility-layers.md)。
8. [从知识库查询到仓库修改：Skill、MCP 与工具权限如何接力？](mcp-skill-tool-lifecycle.md)。
9. [Jev：把一个判断交给模型，动作仍由代码决定](jev-and-system-one.md)。
10. [委派与交接：多执行者怎样对一项任务负责？](delegation-and-handoff.md)。
11. [中断、重试与恢复：如何避免重复副作用？](interruption-recovery.md)。
12. [观察、测试与评测：一次通过能说明什么？](observation-evaluation.md)。

首张[概念总览图](../../figures/agent-loop/README.md)是教学抽象，不代替上述专题的细节图；“多 Agent”一章先解决控制权与执行者数量的区别，委派篇进一步讨论任务合同与对账，但尚无完整运行实验。
