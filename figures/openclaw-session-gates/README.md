# OpenClaw Gateway 路由闸门：文字版

[返回 OpenClaw 首篇](../../docs/systems/openclaw/README.md) · [图源](scene.excalidraw) · [SVG](diagram.svg) · [PNG](preview.png)

读图从左到右：带显式 `sessionKey` 的 Gateway `agent` RPC 先经参数/preflight，再依据 key 与可选 `agentId` 解析会话 owner。身份错误或不一致直接退出。接着检查目标约束、不可用状态并保留去重标识；`prepareAgentSession()` 将请求目标变成 `canonicalKey` 与 `canonicalSessionAgentId`。最后对**规范化后的真实目标**做创建和修改授权，通过后才交给 admission/dispatch。每个下方红色出口是该阶段可能停止的路径；它们不是同一种错误。

本图只来自官方 [`openclaw/openclaw@b373c9a9bcd4954ccdab963e3ed71336302b82be`](https://github.com/openclaw/openclaw/tree/b373c9a9bcd4954ccdab963e3ed71336302b82be) 的 Gateway `agent` RPC 显式 key 路径，属于静态源码图。`chat.send`、各渠道入站、无 key/仅 sessionId、实际 agent harness、消息投递和重试未画入。逐步来源见[代码导读](../../docs/systems/openclaw/code-walkthrough.md)。
