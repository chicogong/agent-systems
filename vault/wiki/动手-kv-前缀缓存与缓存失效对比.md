# 动手：KV 前缀缓存与缓存失效对比

> Synthesized concept page maintained by Aimake LLM Wiki.

## Key Evidence & Provenance

### Source Snapshot (2026-11-22)
- **Origin**: `/Users/haorangong/Github/chicogong/experiments/agent-systems/docs/labs/prefix-cache.md`
- **SHA-256**: `5f237513839d1cdc` · Raw: [[../raw/2026-11-22-动手-kv-前缀缓存与缓存失效对比.md|2026-11-22-动手-kv-前缀缓存与缓存失效对比.md]]
- 在多步 Agent 循环中，输入与输出 Token 量的比例常常高达 100:1。现代大模型底座依靠 Transformer 因果注意力的前缀缓存（KV Cache）将多轮输入的计费单价降低 50%～90%，并大幅降低首字延迟（TTFT）。
- 然而，前缀匹配是**逐字节从左向右严格比对**的：如果第 1 块 Token 发生哪怕 1 个字符的变动，整段几万 Token 的历史缓存就会全盘击穿。
- 在这个零依赖的 3 分钟小实验里，跑完下面三行命令，你会在终端 JSON 中亲眼观察到三种典型装配策略下的 Token 账单与状态流转差异：
- python3 examples/prefix-cache/demo.py --mode layered_hit
- python3 examples/prefix-cache/demo.py --mode dynamic_timestamp
