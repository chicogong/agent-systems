# 沿一次 checkpoint 与 rebuild 走读 MiMo Code 源码

> Synthesized concept page maintained by Aimake LLM Wiki.

## Key Evidence & Provenance

### Source Snapshot (2026-11-22)
- **Origin**: `/Users/haorangong/Github/chicogong/experiments/agent-systems/docs/systems/mimo-code/code-walkthrough.md`
- **SHA-256**: `e5066e34e3427b0c` · Raw: [[../raw/2026-11-22-沿一次-checkpoint-与-rebuild-走读-mimo-code-源码.md|2026-11-22-沿一次-checkpoint-与-rebuild-走读-mimo-code-源码.md]]
- 主 Agent 已经连续改完好几个模块，正埋头排查单测报错，上下文窗口眼看就要见底。MiMo Code 是怎样做到平时在后台悄悄攒好交接笔记、到溢出那一刻安全换窗，又在开关关闭或后台报错时守住退路的？
- 沿着主 Agent 的 8 个代码节点顺流而下，就能把「梯度触发 → 子会话写盘 → 水位线落锁 → 溢出门禁与窗口投影」的每一个分支看个通透。
- 每轮 assistant 回复完成 → 读取 token 用量
- ├─ 1. SessionPrune.fireCheckpoints：跨过梯度阈值且无活跃 writer？
- │      └─ 拉起独立 child session 后台运行 writer → 写父会话 checkpoint.md
