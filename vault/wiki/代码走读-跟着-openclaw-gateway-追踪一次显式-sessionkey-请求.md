# 代码走读：跟着 OpenClaw Gateway 追踪一次显式 `sessionKey` 请求

> Synthesized concept page maintained by Aimake LLM Wiki.

## Key Evidence & Provenance

### Source Snapshot (2026-11-22)
- **Origin**: `/Users/haorangong/Github/chicogong/experiments/agent-systems/docs/systems/openclaw/code-walkthrough.md`
- **SHA-256**: `1c03903e6641481f` · Raw: [[../raw/2026-11-22-代码走读-跟着-openclaw-gateway-追踪一次显式-sessionkey-请求.md|2026-11-22-代码走读-跟着-openclaw-gateway-追踪一次显式-sessionkey-请求.md]]
- 本篇供希望对照 TypeScript 源码追踪网关门禁的读者选读。我们沿着一条携带显式 `sessionKey`（以及可选 `agentId`）的 `agent` RPC 请求，从网络入口一路走到模型执行派发前夜，看清六个关键关口如何衔接。
- 请求抵达网关后，`agentRunHandler` 第一时间核验调用方的基础连接授权，随后用 `validateAgentParams` 校验入参结构与前置运行条件。任何格式残缺或未授权连接都在这一步直接拦截，不会触碰后续的会话存储（`agentRunHandler` 入口）。
- 进入 `startTurn()` 后立即调用 `prepareAgentRequestRouting()`。代码先规范化可选的 `agentId`——只要调用方传了不在当前配置表里的助手 ID，立刻返回 `INVALID_REQUEST`。在寻址优先级上，**显式传入的 `sessionKey` 高于从收件人 `to` 推导出的隐式会话键**，选定后交由下一
- 这是防“串台”的核心函数。它综合三方面线索裁定这段会话归哪个 Agent 管：`sessionKey` 自带的前缀、请求显式传入的 `agentId`、以及磁盘上已有会话记录的 owner：
- - 若 key 前缀与显式 `agentId` 互相打架，或者存储里记录的原 owner 已退役且与当前请求冲突，立即报错拒绝；
