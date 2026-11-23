# 前缀缓存（KV Cache）与上下文经济学：为什么乱改提示词会让账单暴涨十倍

> Synthesized concept page maintained by Aimake LLM Wiki.

## Key Evidence & Provenance

### Source Snapshot (2026-11-22)
- **Origin**: `/Users/haorangong/Github/chicogong/experiments/agent-systems/docs/concepts/cache-and-cost-economics.md`
- **SHA-256**: `96bde213d88ffba2` · Raw: [[../raw/2026-11-22-前缀缓存-kv-cache-与上下文经济学-为什么乱改提示词会让账单暴涨十倍.md|2026-11-22-前缀缓存-kv-cache-与上下文经济学-为什么乱改提示词会让账单暴涨十倍.md]]
- 不少团队第一次把多步编码或网页操作 Agent 推上生产时，都会被月底账单和首字响应速度吓一跳：明明每一步模型只吐出百来个 Token 的工具调用 JSON，跑完一单 30 步的修 Bug 任务，累计消耗的输入 Token 却高达 90 万，每一步等模型吐第一个字（TTFT）还要干等好几秒。翻开代码一查，罪魁祸首往往只是一行看似无害的习惯写法——有人在 Sy
- 在单轮问答里，这种写法无关痛痒；但在 Agent 循环里，它会直接废掉现代大模型推理底座最重要的一项硬件级红利——**前缀缓存**（Prefix Caching / Prompt Caching）。
- 图的文字版逐条拆解了上排失效链路与下排高命中拼装顺序。看懂这张图背后的物理机制，是区分“玩具提示词拼接”与“生产级 Harness 上下文工程”的分水岭。
- 普通聊天机器人一问一答，输入与输出长度大致在 `2:1` 到 `5:1` 之间。而 Agent 是一个围绕工具反馈运转的多步循环：每执行完一次 `grep`、读完一个文件、跑完一轮单测，宿主都要把**系统指令 + 工具 Schema 列表 + 之前所有轮次的对话与工具观察 + 刚刚拿到的一小段新输出**重新打包发给模型。
- 假设基础系统提示与工具定义占 `6,000` Token，每步新增工具观察与回复共 `1,000` Token，连续跑 25 步：
