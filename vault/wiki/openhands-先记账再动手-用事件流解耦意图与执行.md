# OpenHands：先记账再动手，用事件流解耦意图与执行

> Synthesized concept page maintained by Aimake LLM Wiki.

## Key Evidence & Provenance

### Source Snapshot (2026-11-22)
- **Origin**: `/Users/haorangong/Github/chicogong/experiments/agent-systems/docs/systems/openhands/README.md`
- **SHA-256**: `149d749b87d1a79d` · Raw: [[../raw/2026-11-22-openhands-先记账再动手-用事件流解耦意图与执行.md|2026-11-22-openhands-先记账再动手-用事件流解耦意图与执行.md]]
- 写一个 50 行的玩具 Agent 很容易：拿到模型的 `tool_call`，直接调函数改文件或跑命令，再把返回值塞回 `messages`。一旦进入真实工程，这种「函数直连循环」立刻会撞上三堵墙：
- 1. **人工审批会卡死调用栈**：模型准备执行 `rm -rf dist/` 或修改线上配置，必须等用户点「批准」。你不能让后台线程干等二十分钟；可如果直接退出函数，下次恢复时怎么知道模型刚才打算执行哪条命令、参数是什么？
- 2. **中断与拒绝会留下半截账本**：要是用户点了「拒绝」，或者工具参数校验失败，没有配对结果的 `tool_call` 留在上下文里，下一轮请求模型接口就会直接报错。
- 3. **多端观测与执行耦合**：界面渲染、审计日志、持久化存储都需要同时知道「Agent 打算做什么」和「实际做出了什么」，硬塞进同一个循环只会变成胶水代码泥潭。
- OpenHands（核心引擎位于独立拆出的 `software-agent-sdk`）借用了数据库预写日志（WAL）的思路，把整个循环改造成一条**只追加的事件流**（Action / Observation Event Stream）：模型意图、环境执行与会话记录不再互相直接调用，而是全部通过标准事件总线对账。
