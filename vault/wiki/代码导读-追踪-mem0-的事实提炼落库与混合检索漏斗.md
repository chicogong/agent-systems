# 代码导读：追踪 Mem0 的事实提炼落库与混合检索漏斗

> Synthesized concept page maintained by Aimake LLM Wiki.

## Key Evidence & Provenance

### Source Snapshot (2026-11-22)
- **Origin**: `/Users/haorangong/Github/chicogong/experiments/agent-systems/docs/systems/mem0/code-walkthrough.md`
- **SHA-256**: `6d1e7e5308bd8245` · Raw: [[../raw/2026-11-22-代码导读-追踪-mem0-的事实提炼落库与混合检索漏斗.md|2026-11-22-代码导读-追踪-mem0-的事实提炼落库与混合检索漏斗.md]]
- 在应用里调用 `memory.add(messages, user_id="u1")` 和 `memory.search(query, filters={"user_id": "u1"})` 看似只有两行代码，但底层其实横跨了大模型事实抽取、MD5 局部去重、向量库批量回退以及多信号归一化打分。下面固定在 Python 开源版的同步 `Memory.add(
- add(messages, user_id="u1", infer=True)
- ├─► _build_filters_and_metadata：校验作用域 (user_id / agent_id / run_id)
- ├─► 采集近期会话消息 + 向量检索最多 10 条既有记忆作为参考
- ├─► LLM 提取原子事实列表 ──► 空结果？仅保存原始消息并返回 {"results": []}
