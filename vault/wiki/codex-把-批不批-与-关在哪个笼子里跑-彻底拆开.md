# Codex：把「批不批」与「关在哪个笼子里跑」彻底拆开

> Synthesized concept page maintained by Aimake LLM Wiki.

## Key Evidence & Provenance

### Source Snapshot (2026-11-22)
- **Origin**: `/Users/haorangong/Github/chicogong/experiments/agent-systems/docs/systems/codex/README.md`
- **SHA-256**: `bd16bda9a3550a73` · Raw: [[../raw/2026-11-22-codex-把-批不批-与-关在哪个笼子里跑-彻底拆开.md|2026-11-22-codex-把-批不批-与-关在哪个笼子里跑-彻底拆开.md]]
- 设想你在本地仓库里让编码 Agent 跑一句最平常不过的 `npm test`，并顺手配了「跑测试免弹窗」。如果系统天真地把「免人工审批」等同于「直接给宿主机完整权限」，那么一旦 `package.json` 的 `posttest` 脚本里藏着一句读取 `~/.ssh/id_rsa` 外发或者误删上级目录的命令，整台开发机瞬间就会失守；反过来，如果系统胆小
- OpenAI 在 Codex 的 Rust 核心（`codex-rs/core`）里，用一套非常硬核的**双层安全闸门**解开了这个死结：第一道门 `ExecPolicy` 只回答**要不要打扰人类审批**；第二道门 `ToolOrchestrator + Sandbox` 则回答**哪怕免批放行了，命令该关在哪个沙箱笼子里跑，以及万一撞上沙箱围栏后怎么区分
- 在源码主干上，一条命令请求依次穿过请求处理器（Handler）、执行策略（`ExecPolicy`）与执行编排器（`ToolOrchestrator`）：Handler 先核对工作目录与权限上限，策略层给出 `Skip / NeedsApproval / Forbidden` 三态裁决，最后由编排器串联审批、沙箱入笼与失败重判（见整理请求、作出审批决定与安排
- 可编辑图源 · PNG 预览 · 不看图的说明
- 很多自研 Agent 把权限做成一个非黑即白的单开关：白名单命令直接裸跑，非白名单命令弹窗后裸跑。Codex 之所以把审批和沙箱正交拆成两个维度，是因为**静态看命令字面量根本猜不透子进程运行时的真实触角**。
