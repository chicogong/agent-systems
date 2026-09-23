# 按开源系统阅读

[返回首页](../../README.md)

剖面统一用项目类型、固定源码版本、入口与模块边界、循环、工具、上下文/记忆、权限、恢复、评测等问题审视实现；每篇只呈现已核对的局部路径，未覆盖的维度保留为未知或后续工作。新增剖面按[模板](TEMPLATE.md)起稿。

首篇从 [Pi](pi/README.md) 开始，先建立“运行循环 → 交互外壳 → 扩展资源”的阅读方法。随后可沿同一个问题去看不同实现：Codex 的执行审批、OpenCode 的工具调用状态、Letta Code 的记忆可见性。这些是各自固定版本的一条窄路径，不代表对项目整体的审计。

| 候选系统 | 想研究的差异 |
| --- | --- |
| [Pi](pi/README.md) | 已开始：运行核心、coding-agent 会话、Extension 与 Skill 边界 |
| [Codex](codex/README.md) | 已起稿：一次执行如何跨审批、沙箱与工具结果边界 |
| [OpenCode](opencode/README.md) | 已起稿：单次工具调用状态与会话状态为何不同 |
| [OpenHands](openhands/README.md) | 已起稿：SDK 中 ActionEvent、确认闸门与 ObservationEvent |
| [mini-SWE-agent](mini-swe-agent/README.md) | 已起稿：消息账本与 `role=exit` 停止契约 |
| [Letta Code](letta/README.md) | 已起稿：local MemFS v1 的记忆文件与当前上下文 |
| [Mem0](mem0/README.md) | 已起稿：OSS 同步记忆写入与多信号排序的候选边界 |
| [LangGraph](langgraph/README.md) | 已起稿：同一 thread 的 checkpoint 版本与分支 |
| [Browser Use](browser-use/README.md) | 已起稿：一次 step 的观察、模型动作、执行与历史 |
| [OpenClaw](openclaw/README.md) | 已起稿：Gateway 显式 sessionKey 的所有者解析与授权目标 |
| [GPT Researcher](gpt-researcher/README.md) | 已起稿：Hybrid 本地/网页上下文汇合及空材料边界 |
| [Qwen Code](qwen-code/README.md) | 已起稿：延迟工具的 schema 发现与执行双路径 |

Aider、Cline、Goose、Gemini CLI、Kimi Code 等先列为扩展对照，是否深读由它们能否补充新的设计取舍决定。闭源产品只可依据官方公开资料做边界清晰的参考，不标成开源源码剖面。
