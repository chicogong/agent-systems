---
title: "代码走读：跟着 OpenClaw Gateway 追踪一次显式 `sessionKey` 请求"
origin: "/Users/haorangong/Github/chicogong/experiments/agent-systems/docs/systems/openclaw/code-walkthrough.md"
sha256: "1c03903e6641481f685e5c060f164df52a6f97a24c6e95dd1aaa32c5551080d6"
ingested_at: "2026-11-22T13:54:22.941Z"
tags: []
---

# 代码走读：跟着 OpenClaw Gateway 追踪一次显式 `sessionKey` 请求

# 代码走读：跟着 OpenClaw Gateway 追踪一次显式 `sessionKey` 请求

[返回 OpenClaw 首篇](README.md) · [固定官方源码](https://github.com/openclaw/openclaw/tree/b373c9a9bcd4954ccdab963e3ed71336302b82be)

本篇供希望对照 TypeScript 源码追踪网关门禁的读者选读。我们沿着一条携带显式 `sessionKey`（以及可选 `agentId`）的 `agent` RPC 请求，从网络入口一路走到模型执行派发前夜，看清六个关键关口如何衔接。

## 1. 入口预检：`agentRunHandler`

请求抵达网关后，`agentRunHandler` 第一时间核验调用方的基础连接授权，随后用 `validateAgentParams` 校验入参结构与前置运行条件。任何格式残缺或未授权连接都在这一步直接拦截，不会触碰后续的会话存储（[`agentRunHandler` 入口](https://github.com/openclaw/openclaw/blob/b373c9a9bcd4954ccdab963e3ed71336302b82be/src/gateway/server-methods/agent-run-handler.ts#L10-L51)）。

## 2. 路由分流：`prepareAgentRequestRouting`

进入 `startTurn()` 后立即调用 `prepareAgentRequestRouting()`。代码先规范化可选的 `agentId`——只要调用方传了不在当前配置表里的助手 ID，立刻返回 `INVALID_REQUEST`。在寻址优先级上，**显式传入的 `sessionKey` 高于从收件人 `to` 推导出的隐式会话键**，选定后交由下一步判定归属（[`startTurn` 接线](https://github.com/openclaw/openclaw/blob/b373c9a9bcd4954ccdab963e3ed71336302b82be/src/gateway/agent-turn/agent-turn-service.ts#L119-L149) · [路由参数优先级](https://github.com/openclaw/openclaw/blob/b373c9a9bcd4954ccdab963e3ed71336302b82be/src/gateway/agent-turn/agent-request-routing.ts#L71-L105)）。

## 3. 归属裁决：`resolveRequestedSessionAgentId`

这是防“串台”的核心函数。它综合三方面线索裁定这段会话归哪个 Agent 管：`sessionKey` 自带的前缀、请求显式传入的 `agentId`、以及磁盘上已有会话记录的 owner：

- 若 key 前缀与显式 `agentId` 互相打架，或者存储里记录的原 owner 已退役且与当前请求冲突，立即报错拒绝；
- 若传入的是不带前缀的裸 key，则依次尝试按已存归属、兼容映射或“全场唯一助手”规则推导；依然无法唯一确定时，明确要求调用方补齐 `agentId`（[归属裁决逻辑](https://github.com/openclaw/openclaw/blob/b373c9a9bcd4954ccdab963e3ed71336302b82be/src/gateway/session-request-agent.ts#L112-L207)）。

## 4. 会话可用性与期望绑定校验

确定 `requestedSessionKey` 与归属助手后，路由后半段继续核查：`expectedExistingSessionId`（调用方期望续接的会话 ID）是否与实际一致、目标会话当前是否处于可用状态、以及特定命令审批续接请求是否满足绑定约束。通过后保留请求去重标识（dedupe key），读取已有会话元数据并关联 `sessionId`（[路由后半段校验](https://github.com/openclaw/openclaw/blob/b373c9a9bcd4954ccdab963e3ed71336302b82be/src/gateway/agent-turn/agent-request-routing.ts#L167-L244) · [`expectedExistingSessionId` 约束](https://github.com/openclaw/openclaw/blob/b373c9a9bcd4954ccdab963e3ed71336302b82be/src/gateway/server-methods/agent-expected-session.ts#L43-L67)）。

## 5. 坐标归一化与目标级验权：`prepareAgentSession`

回到 `startTurn()` 处理输入准备与可选的会话重置（reset）后，`prepareAgentSession()` 产出最终落库的 `canonicalSessionKey` 与 `sessionAgentId`。紧接着，网关拿着这组最终坐标执行目标级权限核查——判断该客户端身份是否有权创建或修改这段具体会话，未获准则立即终止并返回错误响应（[规范化与目标授权](https://github.com/openclaw/openclaw/blob/b373c9a9bcd4954ccdab963e3ed71336302b82be/src/gateway/agent-turn/agent-turn-service.ts#L279-L334)）。

## 6. 运行接纳与派发：`prepareAgentRunDispatch`

最后一道闸门是 `prepareAgentRunDispatch()`：它负责运行生命周期登记与重复请求拦截（防止网络抖动重发导致同一回合被并发拉起两次）。确认放行后，才正式调用 `startAgentRunExecution()` 进入模型推理与工具循环（[运行接纳与派发边界](https://github.com/openclaw/openclaw/blob/b373c9a9bcd4954ccdab963e3ed71336302b82be/src/gateway/agent-turn/agent-turn-service.ts#L557-L583)）。

把整条门禁链浓缩成一张速查图：

```text
agent RPC(sessionKey, agentId?)
  ├─ 1. agentRunHandler           → 连接身份与参数格式预检
  ├─ 2. prepareAgentRequestRouting → 校验 agentId，确立显式 sessionKey 优先级
  ├─ 3. resolveRequestedSessionAgentId → 交叉核对前缀 / 参数 / 已存 owner，冲突即拒
  ├─ 4. expectedSession & 去重预留 → 核验会话可用性与绑定约束
  ├─ 5. prepareAgentSession       → 归一化 canonicalKey，对最终目标验创建/修改权
  └─ 6. prepareAgentRunDispatch   → 生命周期与幂等去重放行 → startAgentRunExecution()
```

## 来源与边界

本篇基于 [`openclaw/openclaw@b373c9a9bcd4954ccdab963e3ed71336302b82be`](https://github.com/openclaw/openclaw/tree/b373c9a9bcd4954ccdab963e3ed71336302b82be) 静态核对；不同客户端角色（principal）的细粒度权限报错码、断线重连时的去重窗口表现及全局主会话别名分支需结合运行实例进一步观察。
