# 跟着 OpenClaw Gateway 读显式 `sessionKey` 路由

[返回 OpenClaw 首篇](README.md) · [固定官方源码](https://github.com/openclaw/openclaw/tree/b373c9a9bcd4954ccdab963e3ed71336302b82be)

假设你分别用两个助手维护项目和整理资料，现在要给指定会话发送一项任务。请求带上 `sessionKey` 后，Gateway（请求网关）先检查调用者是否获准发起请求，再解析会话归属；确定实际目标后，还要检查创建和修改权限，通过后才安排执行。下面跟着这次 RPC（远程调用）读代码：owner 表示会话归属，canonical key 表示系统最终使用的会话标识。

1. `agentRunHandler` 先检查调用者的授权状态，再用 `validateAgentParams` 校验参数、做开始前检查，通过后调用 `startTurn()`。检查失败就返回错误。[Handler](https://github.com/openclaw/openclaw/blob/b373c9a9bcd4954ccdab963e3ed71336302b82be/src/gateway/server-methods/agent-run-handler.ts#L10-L51)
2. `startTurn()` 调 `prepareAgentRequestRouting()`；路由阶段先规范化可选 `agentId`，对不在配置列表中的 Agent 返回 `INVALID_REQUEST`。显式 `sessionKey` 优先于从 `to` 推断的 Agent key，接着交给 `resolveRequestedSessionAgentId()` 判定 owner。[接线](https://github.com/openclaw/openclaw/blob/b373c9a9bcd4954ccdab963e3ed71336302b82be/src/gateway/agent-turn/agent-turn-service.ts#L119-L149) · [参数选择](https://github.com/openclaw/openclaw/blob/b373c9a9bcd4954ccdab963e3ed71336302b82be/src/gateway/agent-turn/agent-request-routing.ts#L71-L105)
3. `resolveRequestedSessionAgentId()` 根据 key 前缀、显式助手标识和已保存的会话归属选择助手。不带助手前缀的 key，还可以按存储归属、兼容规则或唯一助手来选择；仍选不出时，要求调用者补充助手标识。key 格式错误、显式助手未知、key 前缀与显式助手冲突，或存储中的已退役 owner 与请求冲突时，都会被拒绝。全局主会话别名另有规则。[输入与 owner 判定](https://github.com/openclaw/openclaw/blob/b373c9a9bcd4954ccdab963e3ed71336302b82be/src/gateway/session-request-agent.ts#L112-L207)
4. 选出 `requestedSessionKey` 后，路由程序检查目标是否符合 `expectedExistingSessionId`、会话是否可用，以及特定 exec 审批后续请求的绑定条件。通过后，它按目标 key/Agent 保留去重标识，读取已有会话，并绑定 canonical key 和 `sessionId`；检查被拒绝时，流程在这里结束。[路由后半段](https://github.com/openclaw/openclaw/blob/b373c9a9bcd4954ccdab963e3ed71336302b82be/src/gateway/agent-turn/agent-request-routing.ts#L167-L244) · [约束](https://github.com/openclaw/openclaw/blob/b373c9a9bcd4954ccdab963e3ed71336302b82be/src/gateway/server-methods/agent-expected-session.ts#L43-L67)
5. `startTurn()` 继续准备内容、处理 reset（重置）等事项。随后，`prepareAgentSession()` 得到 `canonicalSessionKey` 和 `sessionAgentId`，也就是实际要操作的会话与助手。程序再对这个目标检查创建和修改权限，授权失败就返回失败响应。[规范化与授权](https://github.com/openclaw/openclaw/blob/b373c9a9bcd4954ccdab963e3ed71336302b82be/src/gateway/agent-turn/agent-turn-service.ts#L279-L334)
6. `prepareAgentRunDispatch()` 检查能否接纳这次运行，同时处理生命周期和去重结果。这些条件允许继续、并返回准备结果后，程序才调度 `startAgentRunExecution()`。要追踪模型怎样运行，可以从这个函数之后的事件接着读。[调度边界](https://github.com/openclaw/openclaw/blob/b373c9a9bcd4954ccdab963e3ed71336302b82be/src/gateway/agent-turn/agent-turn-service.ts#L557-L583)

```text
agent RPC(sessionKey, agentId?)
  → 参数/preflight
  → 从 key 和 agentId 解析 owner；冲突或无效则拒绝
  → 检查目标约束与可用性，保留去重标识
  → prepareAgentSession 得到 canonicalKey / canonicalSessionAgentId
  → 对规范化目标授权；失败则停止
  → 交给接纳与派发，再启动后续执行
```

### 版本与待验证项

上述流程来自固定提交的**源码静态核对**，本篇没有启动 Gateway、模拟不同客户端身份（client principal）或构造并发 RPC。不同配置、重连和并发请求中的处理效果仍需运行观察：权限错误怎样返回客户端、去重怎样处理重试，以及全局 scope 别名和渠道入站走哪条路，都需要分别检查。
