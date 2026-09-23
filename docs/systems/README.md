# 按开源系统阅读

[返回首页](../../README.md)

剖面统一记录：项目类型、研究问题、固定源码版本、入口与模块边界、Agent loop、工具、上下文/记忆、权限、恢复、评测，以及不能从公开证据得出的结论。新增剖面按[模板](TEMPLATE.md)起稿。

首篇从 Pi 开始：它的代码分层紧凑，适合先建立“运行循环 → 交互外壳 → 扩展资源”的阅读方法。[Pi 剖面](pi/README.md)会按固定版本逐节落地。

| 候选系统 | 想研究的差异 |
| --- | --- |
| [Pi](pi/README.md) | 已开始：运行核心、coding-agent 会话、Extension 与 Skill 边界 |
| [Codex](https://github.com/openai/codex) | 本地 coding agent 的执行和控制边界 |
| [OpenCode](https://github.com/anomalyco/opencode) | 会话、专用 agent 与多入口组织 |
| [OpenHands](https://github.com/OpenHands/OpenHands) | SDK、运行环境和界面分层 |
| [mini-SWE-agent](https://github.com/SWE-agent/mini-swe-agent) | 极简 loop 与软件工程任务 |
| [Letta Code](https://github.com/letta-ai/letta-code) | 跨会话状态与 agent 自身记忆 |
| [Browser Use](https://github.com/browser-use/browser-use) | 浏览器观察与动作空间 |
| [OpenClaw](https://github.com/openclaw/openclaw) | 常驻 agent、消息入口和本地状态 |
| [GPT Researcher](https://github.com/assafelovic/gpt-researcher) | 多源研究与引用 |
| [Qwen Code](https://github.com/QwenLM/qwen-code) | coding agent 与开源模型生态 |

Aider、Cline、Goose、Gemini CLI、Kimi Code 等先列为扩展对照，是否深读由它们能否补充新的设计取舍决定。闭源产品只可依据官方公开资料做边界清晰的参考，不标成开源源码剖面。
