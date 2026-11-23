# 跟着 Pi 代码走一轮：从 `prompt()` 到会话树投影

> Synthesized concept page maintained by Aimake LLM Wiki.

## Key Evidence & Provenance

### Source Snapshot (2026-11-22)
- **Origin**: `/Users/haorangong/Github/chicogong/experiments/agent-systems/docs/systems/pi/code-walkthrough.md`
- **SHA-256**: `66b54172ded2eaff` · Raw: [[../raw/2026-11-22-跟着-pi-代码走一轮-从-prompt-到会话树投影.md|2026-11-22-跟着-pi-代码走一轮-从-prompt-到会话树投影.md]]
- 自己动手写过第一个 Agent 循环的人，几乎都会在三天内撞上同一批暗礁：模型输出撞上 `max_tokens` 被拦腰截断，半截残缺的 JSON 参数直接把工具层炸崩；用户趁工具跑着的时候追发了一句话，结果两条并发循环同时往 `messages` 数组里乱塞消息；上游 API 偶发 529 过载报错，重试一次却把上一次失败的残骸留在上下文里，惹得模型一脸茫
- 这一篇我们就以「读取文件并修改代码」为主线，像拆解机械机芯一样，顺着 `pi-agent-core` 与 `pi-coding-agent` 的真实函数签名跟读一整轮，看 Pi 是怎样在几百行核心代码里把这些工程暗礁逐一排干的。
- 一切从 `Agent.prompt()` 开始。它做的第一件防呆动作，就是**严禁重入**：只要当前已经有任务在跑，第二个直接打进来的 `prompt()` 调用会被当场拒绝，逼着调用方明确表态——你到底是想中途改方向（走 `steer`），还是等干完活再加菜（走 `followUp`），从根源上杜绝两个循环并发篡改同一份内存状态。
- 通过入口检查后，用户任务进入 `runLoop`。每次真正向大模型发起流式请求前，Pi 不会把内存里的原始消息直接裸发出去，而是依次走过三步准备管线（见准备这一轮与组成模型输入）：
- 1. **请求前准备**（`prepareRequest`）：运行宿主配置的请求前异步准备逻辑（例如刷新动态状态）。
