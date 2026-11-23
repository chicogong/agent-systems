# DSH：基于插件注入的并发工具池与按序提交关口

> Synthesized concept page maintained by Aimake LLM Wiki.

## Key Evidence & Provenance

### Source Snapshot (2026-11-22)
- **Origin**: `/Users/haorangong/Github/chicogong/experiments/agent-systems/docs/systems/dsh/README.md`
- **SHA-256**: `7c9b33db43651ae0` · Raw: [[../raw/2026-11-22-dsh-基于插件注入的并发工具池与按序提交关口.md|2026-11-22-dsh-基于插件注入的并发工具池与按序提交关口.md]]
- 当大模型在一次回复里一口气开出三张工具工单——`A` 是全仓全文检索（耗时 3 秒），`B` 是读取配置文件（耗时 20 毫秒），`C` 是读取 `package.json`（耗时 15 毫秒）——运行时立刻面临一个两难抉择：如果老老实实串行排队，`B` 和 `C` 就得陪着慢吞吞的 `A` 白等 3 秒；可如果直接用 `Promise.all` 谁先跑完谁
- DeepSeek 开源的 **DeepSeek Harness**（简称 DSH）给出了两个极具工程美感的设计回答：在架构组装层，用 **Cordis 插件与服务注入**让审批、沙箱、文件系统按需插拔且缺省安全；在工具调度层，把**单批工具执行完成**与**向模型提交结果**拆成两道独立关口——执行过程允许重叠抢跑，结果落账严格按序放行。
- 如果还没熟悉基础的Agent loop，可以把 Harness 理解成让大模型持续干活的「运行底盘」。与 Pi 按上下游纵向切成三个固定包的思路不同，DSH 基于插件框架 **Cordis** 把整个运行时拆成横向的服务总线：模型会话、工具注册表、用户审批、文件系统和子进程执行器全都是可替换的插件服务。
- | 服务切面 | 插件化组装方式 | 解决的工程问题 |
- | --- | --- | --- |
