# 动手：按原操作 ID 找回回执

> Synthesized concept page maintained by Aimake LLM Wiki.

## Key Evidence & Provenance

### Source Snapshot (2026-11-22)
- **Origin**: `/Users/haorangong/Github/chicogong/experiments/agent-systems/docs/labs/remote-effect.md`
- **SHA-256**: `842694915040486c` · Raw: [[../raw/2026-11-22-动手-按原操作-id-找回回执.md|2026-11-22-动手-按原操作-id-找回回执.md]]
- 很多 Agent 教程在教错误处理时，会轻描淡写写一句 `except Exception: retry()`。一旦你的工具干的是发版本、扣余额、建工单这类外部写操作，这行看似无害的重试就是定时炸弹。
- 在这个零依赖的 3 分钟小实验里，程序同时为你打开了两个视角——**客户端手里的回执**与**服务端底账里的真实副作用计数**（`effects`）。跑完下面几行命令，你会亲眼看到三幕极具冲击力的反差：
- 1. **回执明明为空，服务端副作用计数却已经是 1**（`receipt=null` 但 `effects=1`）：发版请求 `publish-v1` 其实早已在服务端登记成功，只是回程答复丢了——在客户端眼里风平浪静，在外部世界里大局已定。
- 2. **最诚实的高手敢于停在 `unknown_stop`**：当回执丢了、目标服务又没有查询接口时，宿主在 `no_lookup` 模式下果断刹车，绝不赌运气盲目重发（此时上帝视角显示 `effects=1`，而宿主诚实承认自己不知道）。
- 3. **自作聪明换个新 ID 重试，当场制造双倍事故**：在 `unsafe_new_id` 模式下，客户端给重试请求换了个带 `-retry` 后缀的新编号，直接绕过服务端去重防线，把发布副作用从 `1` 翻倍成了 `2`！
