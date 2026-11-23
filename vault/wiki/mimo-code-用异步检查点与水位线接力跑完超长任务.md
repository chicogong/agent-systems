# MiMo Code：用异步检查点与水位线接力跑完超长任务

> Synthesized concept page maintained by Aimake LLM Wiki.

## Key Evidence & Provenance

### Source Snapshot (2026-11-22)
- **Origin**: `/Users/haorangong/Github/chicogong/experiments/agent-systems/docs/systems/mimo-code/README.md`
- **SHA-256**: `0aeac7e92e476cf1` · Raw: [[../raw/2026-11-22-mimo-code-用异步检查点与水位线接力跑完超长任务.md|2026-11-22-mimo-code-用异步检查点与水位线接力跑完超长任务.md]]
- 让编码 Agent 跨几十个文件做一次大型模块迁移，聊到第 35 轮时最怕两件事：一是临近上下文窗口上限才临时触发「停机全量摘要」——不仅用户要对着屏幕干等半分钟，而且此时窗口早已塞满海量报错日志，模型在摘要时极易漏掉第 1 轮定下的架构约束；二是如果改成后台异步写摘要，万一换窗口那一刻后台任务刚改了一半文件就报错退出，主 Agent 拿着半截残缺笔记重建上
- MiMo Code 用一套「**提前异步写检查点 + 成功水位线对账 + 预算化窗口重建**」的接力机制化解了这对矛盾：主 Agent 在前台一路推进代码修改与测试，宿主按窗口用量梯度在后台派生独立的 `writer`（笔记整理者）提前提炼结构化交接文件；等窗口真正告警时，再凭已确认的水位线（watermark）无缝换窗。
- 为了兼顾「审计不丢细节」与「推理不爆窗口」，MiMo Code 把同一场长任务的数据拆成生命周期各不相同的三份材料：
- | 材料层级 | 核心载体与内容 | 何时读写与生效 |
- | --- | --- | --- |
