# 读懂 `DefaultAgent`：不到两百行代码如何把消息列表变成状态机

> Synthesized concept page maintained by Aimake LLM Wiki.

## Key Evidence & Provenance

### Source Snapshot (2026-11-22)
- **Origin**: `/Users/haorangong/Github/chicogong/experiments/agent-systems/docs/systems/mini-swe-agent/code-walkthrough.md`
- **SHA-256**: `22f5048bf4ef478f` · Raw: [[../raw/2026-11-22-读懂-defaultagent-不到两百行代码如何把消息列表变成状态机.md|2026-11-22-读懂-defaultagent-不到两百行代码如何把消息列表变成状态机.md]]
- 在很多工程代码里，跨层传递停止原因是一件很啰嗦的事：`env.execute()` 得返回 `(output, is_submitted)`，`step()` 得返回 `(continue_flag, stop_reason)`，外层再写一串 `if/elif` 更新一堆实例属性，稍有疏漏就会出现「内存标志说停了，落盘日志却少记了最后一步」的分裂现场。
- `mini-swe-agent` 的 `DefaultAgent` 之所以读起来像水晶一样通透，是因为它立下了两条极简铁律：**第一，所有运行状态只往 `self.messages` 里追加，绝不另设平行账本；第二，用携带消息字典的自定义异常跨越调用栈，把「预算超限」「交卷停机」和「格式报错」全部统一成「往列表末尾塞消息」这同一个动作**。
- 先把整台机器的浓缩骨架摊在桌面上：
- self.messages = [system, user(task)]
- ├─ query()           ──► 核查步数/成本/时长限额 → model.query(messages) → 追加 assistant 消息
