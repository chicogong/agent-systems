# 代码导读：`steer` 何时真正进入模型上下文

> Synthesized concept page maintained by Aimake LLM Wiki.

## Key Evidence & Provenance

### Source Snapshot (2026-11-22)
- **Origin**: `/Users/haorangong/Github/chicogong/experiments/agent-systems/docs/systems/kimi-code/code-walkthrough.md`
- **SHA-256**: `24bcc09b691cae24` · Raw: [[../raw/2026-11-22-代码导读-steer-何时真正进入模型上下文.md|2026-11-22-代码导读-steer-何时真正进入模型上下文.md]]
- 当测试脚本还在后台轰鸣，用户敲下一句「先解释失败原因」。这句话从进入 `TurnFlow.steer()` 到真正出现在大模型的 `messages` 数组里，中间究竟跨过了哪些状态锁、Hook 与循环关口？
- 顺着 `packages/agent-core` 的 8 个关键节点走一趟，就能把「回合互斥启动 → 忙时缓冲 → 步前优先刷盘 → 停机压哨续命 → 取消与异常收尾」整条状态机拼完整。
- 空闲时 prompt() / steer() → launch() [单活动回合互斥锁 + 分配 turnId & AbortController]
- └─ runOneTurn() 发出 turn.started → UserPromptSubmit hook → runStepLoop() → runTurn()
- ├─ 每步起点：检查 AbortSignal 与 maxSteps
