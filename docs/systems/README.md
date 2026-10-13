# 按开源系统阅读

[返回首页](../../README.md)

想知道一个 Agent 项目怎样工作，可以先选一条具体路径：一条命令如何得到批准，一次工具调用如何记录进度，或一份记忆怎样进入下一轮输入。下面每篇都从这样的任务出发，再带你找到固定版本中的关键代码。章末说明所用版本、来源和未读范围；新增文章按[模板](TEMPLATE.md)起稿。

初次读源码，可以从 Pi 开始，按“运行循环 → 交互外壳 → 扩展资源”逐层看。也可以直接进入你关心的机制，例如 Codex 的执行审批、OpenCode 的工具调用状态或 Letta Code 的记忆可见性。各项目的组织方式不同，这些文章分别解释其中一条路径。

| 系统切面 | 本篇关注的差异 |
| --- | --- |
| [Pi](pi/README.md) | 运行核心、coding-agent 会话、Extension 与 Skill 边界 |
| [DSH / DeepSeek Harness](dsh/README.md) | 插件服务接缝、并发执行与有序结果提交 |
| [Codex](codex/README.md) | 一次执行如何跨审批、沙箱与工具结果边界 |
| [OpenCode](opencode/README.md) | 单次工具调用状态与会话状态为何不同 |
| [OpenHands](openhands/README.md) | SDK 中 ActionEvent、确认闸门与 ObservationEvent |
| [mini-SWE-agent](mini-swe-agent/README.md) | 消息账本与 `role=exit` 停止契约 |
| [Letta Code](letta/README.md) | local MemFS v1 的记忆文件与当前上下文 |
| [Hermes Agent](hermes/README.md) | 内置记忆快照、Skill 写入审批与任务后知识审视 |
| [Mem0](mem0/README.md) | OSS 同步记忆写入与多信号排序的候选边界 |
| [LangGraph](langgraph/README.md) | 同一 thread 的 checkpoint 版本与分支 |
| [Browser Use](browser-use/README.md) | 一次 step 的观察、模型动作、执行与历史 |
| [OpenClaw](openclaw/README.md) | Gateway 显式 sessionKey 的所有者解析与授权目标 |
| [GPT Researcher](gpt-researcher/README.md) | Hybrid 本地/网页上下文汇合及空材料边界 |
| [Qwen Code](qwen-code/README.md) | 延迟工具的 schema 发现与执行双路径 |
| [Kimi Code](kimi-code/README.md) | 忙时 steer 缓冲如何在 step 边界进入当前 turn |
| [MiMo Code](mimo-code/README.md) | 长会话 writer、checkpoint watermark 与窗口重建 |

Aider、Cline、Goose、Gemini CLI 等先列为扩展对照，是否深读由它们能否补充新的设计取舍决定。闭源产品只可依据官方公开资料做边界清晰的参考，不标成开源源码剖面。
