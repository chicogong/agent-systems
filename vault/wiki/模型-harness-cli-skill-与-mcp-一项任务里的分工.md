# 模型、Harness、CLI、Skill 与 MCP：一项任务里的分工

> Synthesized concept page maintained by Aimake LLM Wiki.

## Key Evidence & Provenance

### Source Snapshot (2026-11-22)
- **Origin**: `/Users/haorangong/Github/chicogong/experiments/agent-systems/docs/concepts/model-harness-cli-mcp-skill.md`
- **SHA-256**: `9411f5ab98183f71` · Raw: [[../raw/2026-11-22-模型-harness-cli-skill-与-mcp-一项任务里的分工.md|2026-11-22-模型-harness-cli-skill-与-mcp-一项任务里的分工.md]]
- 刚开始接触编码与办公 Agent 时，最让人头晕的往往不是代码本身，而是满屏混在一起的名词：明明底层接的是同一款大模型，为什么换了个命令行工具，代码修复的成功率就天差地别？装了三个 MCP 服务和五份 Skill 文档，为什么遇到写文件照样弹权限拦截，或者刚聊几轮就把上下文窗口塞爆了？
- 答案很直接：你日常使用的 AI 助手从来不是“一颗裸奔的模型”，而是**五层各司其职的系统栈**。只要分清哪一层管判断、哪一层管调度与铁丝网、哪一层递手册、哪一层接外部插座，换工具或排故障时就能一眼定位问题出在哪一层。
- | 层级 | 核心角色 | 它解决什么工程矛盾 | 缺了它或配错它会怎样 |
- | --- | --- | --- | --- |
- | **模型**（Model） | 认知与推理大脑 | 读懂当前上下文，判断下一步该查什么或怎样作答 | 理解偏差、提议错乱，再好的外层工具也救不回来 |
