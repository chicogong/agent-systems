# 按开源系统阅读

[返回首页](../../README.md)

剖面统一用项目类型、固定源码版本、入口与模块边界、循环、工具、上下文/记忆、权限、恢复、评测等问题审视实现；每篇只呈现已核对的局部路径，未覆盖的维度保留为未知或后续工作。新增剖面按[模板](TEMPLATE.md)起稿。

Pi 是最早写成的系统案例，用来建立“运行循环 → 交互外壳 → 扩展资源”的阅读方法；它不是本书的通用 Agent 模板。也可以从你关心的机制直接进入 Codex 的执行审批、OpenCode 的工具调用状态或 Letta Code 的记忆可见性。这些都是各自固定版本的一条窄路径，不代表对项目整体的审计。

| 系统切面 | 本篇关注的差异 |
| --- | --- |
| [Pi](pi/README.md) | 运行核心、coding-agent 会话、Extension 与 Skill 边界 |
| [Codex](codex/README.md) | 一次执行如何跨审批、沙箱与工具结果边界 |
| [OpenCode](opencode/README.md) | 单次工具调用状态与会话状态为何不同 |
| [OpenHands](openhands/README.md) | SDK 中 ActionEvent、确认闸门与 ObservationEvent |
| [mini-SWE-agent](mini-swe-agent/README.md) | 消息账本与 `role=exit` 停止契约 |
| [Letta Code](letta/README.md) | local MemFS v1 的记忆文件与当前上下文 |
| [Mem0](mem0/README.md) | OSS 同步记忆写入与多信号排序的候选边界 |
| [LangGraph](langgraph/README.md) | 同一 thread 的 checkpoint 版本与分支 |
| [Browser Use](browser-use/README.md) | 一次 step 的观察、模型动作、执行与历史 |
| [OpenClaw](openclaw/README.md) | Gateway 显式 sessionKey 的所有者解析与授权目标 |
| [GPT Researcher](gpt-researcher/README.md) | Hybrid 本地/网页上下文汇合及空材料边界 |
| [Qwen Code](qwen-code/README.md) | 延迟工具的 schema 发现与执行双路径 |

Aider、Cline、Goose、Gemini CLI、Kimi Code 等先列为扩展对照，是否深读由它们能否补充新的设计取舍决定。闭源产品只可依据官方公开资料做边界清晰的参考，不标成开源源码剖面。
