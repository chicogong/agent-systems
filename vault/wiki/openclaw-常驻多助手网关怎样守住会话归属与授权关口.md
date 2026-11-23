# OpenClaw：常驻多助手网关怎样守住会话归属与授权关口

> Synthesized concept page maintained by Aimake LLM Wiki.

## Key Evidence & Provenance

### Source Snapshot (2026-11-22)
- **Origin**: `/Users/haorangong/Github/chicogong/experiments/agent-systems/docs/systems/openclaw/README.md`
- **SHA-256**: `832b087ed3ef4178` · Raw: [[../raw/2026-11-22-openclaw-常驻多助手网关怎样守住会话归属与授权关口.md|2026-11-22-openclaw-常驻多助手网关怎样守住会话归属与授权关口.md]]
- 在本地命令行里跑一个单人编码助手很简单：一个终端窗口就是一个进程、一段对话，谁发的消息一目了然。但只要把 Agent 变成**常驻后台服务**——同时挂着“代码维护助手”和“私人资料助手”，还要接收来自网页、桌面端或聊天软件的远程请求——麻烦立刻就来了：
- 如果请求里带了一个会话名 `sessionKey: "daily-notes"`，同时又传了 `agentId: "coder"`，而这段会话原本属于资料助手，系统该听谁的？如果调用者随便猜了一个别人的会话键，能不能直接往里塞指令甚至覆盖上下文？
- OpenClaw 的 Gateway（请求网关）专门解决这类“**在模型真正开口之前，先把请求送到对的房间、验明正身**”的接线难题。下面沿着一次携带显式 `sessionKey` 的 `agent` RPC 调用，看它如何用三道门禁防止串台与越权。
- 可编辑图源 · PNG 预览 · 不看图的说明
- 很多早期网关最容易犯的安全错误，是“先拿用户传进来的原始字符串做权限检查，后面路由解析时又因为别名或默认回退跑到了另一个实际会话上”。OpenClaw 在这段路径里严格执行三步递进（RPC 入口 · 请求路由 · 规范化后授权）：
