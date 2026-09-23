# 跟着 OpenClaw Gateway 读显式 `sessionKey` 路由

[返回 OpenClaw 首篇](README.md) · [固定官方源码](https://github.com/openclaw/openclaw/tree/b373c9a9bcd4954ccdab963e3ed71336302b82be)

以下是便于跟读的**控制流摘要**，不是源码复制。前提是 Gateway `agent` RPC 的请求带显式 `sessionKey`；不覆盖其他入口或参数组合。

1. `agentRunHandler` 先检查调用者 authority 是否仍有效，用 `validateAgentParams` 验证 RPC 参数，再执行 preflight 并调用 `startTurn()`。其中任一步失败，后续路由不执行。[Handler](https://github.com/openclaw/openclaw/blob/b373c9a9bcd4954ccdab963e3ed71336302b82be/src/gateway/server-methods/agent-run-handler.ts#L10-L51)
2. `startTurn()` 调 `prepareAgentRequestRouting()`；路由阶段先规范化可选 `agentId`，对不在配置列表中的 Agent 返回 `INVALID_REQUEST`。显式 `sessionKey` 优先于从 `to` 推断的 Agent key，接着交给 `resolveRequestedSessionAgentId()` 判定 owner。[接线](https://github.com/openclaw/openclaw/blob/b373c9a9bcd4954ccdab963e3ed71336302b82be/src/gateway/agent-turn/agent-turn-service.ts#L119-L149) · [参数选择](https://github.com/openclaw/openclaw/blob/b373c9a9bcd4954ccdab963e3ed71336302b82be/src/gateway/agent-turn/agent-request-routing.ts#L71-L105)
3. `resolveRequestedSessionAgentId()` 拒绝 malformed agent key、未知显式 Agent、key 前缀与显式 Agent 冲突、retired store owner 冲突；某些未限定 key 需要通过存储归属、兼容 owner 或唯一 Agent 推断，仍不能推断时要求调用者指定 Agent。全局主会话别名另有特殊处理，不能简化成字符串前缀判断。[输入与 owner 判定](https://github.com/openclaw/openclaw/blob/b373c9a9bcd4954ccdab963e3ed71336302b82be/src/gateway/session-request-agent.ts#L112-L207)
4. 选出 `requestedSessionKey` 后，路由阶段检查 `expectedExistingSessionId` 约束、不可用会话和特定 exec 审批后续绑定；然后以目标 key/Agent 保留去重标识，读取已有会话并绑定 canonical key 与 sessionId。任何早期拒绝都会在此停止，不进入 agent run。[路由后半段](https://github.com/openclaw/openclaw/blob/b373c9a9bcd4954ccdab963e3ed71336302b82be/src/gateway/agent-turn/agent-request-routing.ts#L167-L244) · [约束](https://github.com/openclaw/openclaw/blob/b373c9a9bcd4954ccdab963e3ed71336302b82be/src/gateway/server-methods/agent-expected-session.ts#L43-L67)
5. `startTurn()` 仍会进行内容、reset 等准备。本篇只继续跟显式 key 的关键点：`prepareAgentSession()` 得到 `canonicalSessionKey` 和 `sessionAgentId` 后，再对规范化目标做 session creation 与 mutation 授权。授权失败发失败响应并返回。[规范化与授权](https://github.com/openclaw/openclaw/blob/b373c9a9bcd4954ccdab963e3ed71336302b82be/src/gateway/agent-turn/agent-turn-service.ts#L279-L334)
6. 后续 `prepareAgentRunDispatch()` 还可能因为 admission、生命周期或去重结果停止；返回准备结果之后，`startAgentRunExecution()` 才被调度。这些属于另一层运行时控制，不能把“路由通过”说成“模型已经运行”。[调度边界](https://github.com/openclaw/openclaw/blob/b373c9a9bcd4954ccdab963e3ed71336302b82be/src/gateway/agent-turn/agent-turn-service.ts#L557-L583)

```text
agent RPC(sessionKey, agentId?)
  → 参数/preflight
  → 从 key 和 agentId 解析 owner；冲突或无效则拒绝
  → 检查目标约束与可用性，保留去重标识
  → prepareAgentSession 得到 canonicalKey / canonicalSessionAgentId
  → 对规范化目标授权；失败则停止
  → 交给后续 admission/dispatch（不代表已执行）
```

### 证据等级和未知

上述调用点和分支来自固定提交的**源码静态核对**。本篇没有启动 Gateway、模拟不同 client principal 或构造并发 RPC，因此不验证这些守卫在所有配置、重连或竞态下的实际效果。权限错误被准确返回给客户端、去重能否覆盖所有重试、全局 scope 别名和渠道入站是否收敛于同一路由，也需单独测试或章节核对。
