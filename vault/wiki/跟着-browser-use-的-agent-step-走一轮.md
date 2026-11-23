# 跟着 browser-use 的 `Agent.step()` 走一轮

> Synthesized concept page maintained by Aimake LLM Wiki.

## Key Evidence & Provenance

### Source Snapshot (2026-11-22)
- **Origin**: `/Users/haorangong/Github/chicogong/experiments/agent-systems/docs/systems/browser-use/code-walkthrough.md`
- **SHA-256**: `6976c7881a2ebbd4` · Raw: [[../raw/2026-11-22-跟着-browser-use-的-agent-step-走一轮.md|2026-11-22-跟着-browser-use-的-agent-step-走一轮.md]]
- 翻开 `Agent.step()` 的源码，有两处细节最值得细品：第一，上一轮的 `last_result` 为什么不在上一轮末尾清零，非要拖到本轮 `_prepare_context()` 之后才清空？第二，为什么 `_finalize(summary)` 必须包在 `finally` 块里，还要反复核对 `last_result` 和 `summary`
- 顺着下面这条骨架走一遍，这两个状态生命周期的设计意图就会一目了然：
- summary = _prepare_context()           // 采集当前页摘要 + 把「上一步 last_result」拼进本轮模型输入
- clear(last_model_output, last_result)   // 旧结果已完成使命，此刻清零，防止本轮中途失败时串入脏数据
- _get_next_action(summary)               // 带超时与重试请求模型，产出结构化 AgentOutput.action
