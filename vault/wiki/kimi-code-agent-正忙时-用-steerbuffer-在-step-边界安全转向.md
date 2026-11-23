# Kimi Code：Agent 正忙时，用 steerBuffer 在 step 边界安全转向

> Synthesized concept page maintained by Aimake LLM Wiki.

## Key Evidence & Provenance

### Source Snapshot (2026-11-22)
- **Origin**: `/Users/haorangong/Github/chicogong/experiments/agent-systems/docs/systems/kimi-code/README.md`
- **SHA-256**: `2ba3fc015f05a32e` · Raw: [[../raw/2026-11-22-kimi-code-agent-正忙时-用-steerbuffer-在-step-边界安全转向.md|2026-11-22-kimi-code-agent-正忙时-用-steerbuffer-在-step-边界安全转向.md]]
- 你让编码 Agent 修一个测试报错。它正紧锣密鼓地跑 `pytest`，你在滚动日志里一眼揪出了真凶，赶紧敲下一句：「先别改 `auth.ts`，把夹具竞态的原因给我讲清楚。」
- 这句中途插话把 Agent 运行时逼进了一个两难死角：
- - **如果当场强杀当前工具**：测试进程被拦腰斩断，磁盘上可能留下半截临时文件或锁文件；更致命的是，上下文里多出一条没有 `tool_result` 配对的悬空 `tool_use`，下一次调用大模型 API 会因为违反消息协议直接报错。
- - **如果锁死输入框等整轮跑完**：一个复杂回合（`turn`）往往连跑十几个步骤（`step`），等它彻底停下来，三四个无辜文件早就被改得面目全非了。
- Kimi Code 的 `TurnFlow` 选了一条既不留脏状态、又不让任务跑偏的中间路线：**忙时先把补充指令暂存进 `steerBuffer` 缓冲区，等当前工具原子化收尾，立刻在下一个 `step` 起点和回合结束关口把新指令刷入上下文**。
