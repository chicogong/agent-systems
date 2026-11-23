# Hermes 代码导读：追踪经验的读取、暂存、后台复盘与快照刷新

> Synthesized concept page maintained by Aimake LLM Wiki.

## Key Evidence & Provenance

### Source Snapshot (2026-11-22)
- **Origin**: `/Users/haorangong/Github/chicogong/experiments/agent-systems/docs/systems/hermes/code-walkthrough.md`
- **SHA-256**: `32eaabcef55c24e3` · Raw: [[../raw/2026-11-22-hermes-代码导读-追踪经验的读取-暂存-后台复盘与快照刷新.md|2026-11-22-hermes-代码导读-追踪经验的读取-暂存-后台复盘与快照刷新.md]]
- 当编码助手一边守着“严禁触碰生产库”的环境红线排查测试故障，一边把新摸索出的排障套路沉淀成下次可用的 Skill 时，底层代码究竟在哪一刻锁住了系统提示快照、在哪一刻把高危改动拦进 `staged` 队列、又在哪一刻拉起后台复盘？下面沿着 `NousResearch/hermes-agent@a9109b07f42685f88397008d0d5a6c3d4
- 用户发来新消息时，调用首先进入 `TurnFacadeMixin.run_conversation()`。注意它的第一个动作不是直接调模型，而是先检查并取消上一轮可能仍在后台运行的知识复查任务，避免后台整理与前台新对话争抢状态，随后在同文件 142–154 行把控制权转交给会话主循环。
- 主循环 `agent/conversation_loop.py` 负责驱动多步工具调用与模型响应，并在整轮对话结束时调用收尾器（finalizer）——那里正是盘后后台复盘的触发点。阅读 `run_agent.py` 中的 `AIAgent` 时，顺着这层 Mixin 转发就能定位各职责模块。
- Agent 启动阶段，`_init_memory()` 根据 `skip_memory` 配置与内置 memory 工具的启用情况创建 `MemoryStore` 实例，并调用 `load_from_disk()` 从磁盘装载 `MEMORY.md` 与 `USER.md`。
- 打开 `MemoryStore` 可以看到它最核心的数据结构设计：内部同时维护动态变化的当前条目（live entries）与冻结的 `_system_prompt_snapshot`。加载器在读盘时做去重并生成快照；若发现外部编辑器手工塞入了超配额内容，不会粗暴截断磁盘文件，而是在加载时记录提醒；针对特定可疑注入内容的扫描与替换也只作用于送往模型的提示快照
