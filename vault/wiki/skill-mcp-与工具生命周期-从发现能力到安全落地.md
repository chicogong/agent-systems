# Skill、MCP 与工具生命周期：从发现能力到安全落地

> Synthesized concept page maintained by Aimake LLM Wiki.

## Key Evidence & Provenance

### Source Snapshot (2026-11-22)
- **Origin**: `/Users/haorangong/Github/chicogong/experiments/agent-systems/docs/concepts/mcp-skill-tool-lifecycle.md`
- **SHA-256**: `185d3ad087e3c12a` · Raw: [[../raw/2026-11-22-skill-mcp-与工具生命周期-从发现能力到安全落地.md|2026-11-22-skill-mcp-与工具生命周期-从发现能力到安全落地.md]]
- 把 Skill 和 MCP 接进工程环境的第一天，开发者最容易掉进两个直觉陷阱：第一，看到内部知识库 MCP 服务连接成功、`kb.fetch` 出现在工具列表里，就以为 Agent 顺理成章能读到所有技术文档——结果一跑任务全卡在权限拒绝；第二，在团队共享的 `SKILL.md` 正文里写了一句“允许自动运行迁移脚本并推送分支”，就以为宿主真的会照单放行，
- 踩坑的原因，是把**目录声明**、**作业指导**与**执行门禁**混成了同一件事。一次真实的工具调用，从准备到落盘必须穿过六道关卡：**发现工具**（`tools/list`）→ **按需装载指导**（Skill）→ **模型提议调用** → **宿主参数与权限门禁** → **外部执行**（`tools/call`）→ **错误分流与防提示注入**。看清
- 图下排展示了运行主干（**模型提议 → 宿主门禁检查 → 工具执行 → 产物验收**），上排展示了方法指导、任务边界与工具清单如何注入每一步。图的文字版逐条拆解了图中连线，图源可直接打开编辑。
- 来看一个典型的研发协同场景：
- > 查阅内部知识库条目 `KB-142`（《支付网关订单重试规范》），据此修复本地仓库 `src/orders/retry.ts` 中的最大退避上限问题，并补齐回归测试。约束：只允许修改 `retry.ts` 与对应测试文件，禁止自动提交或推送；若无法取得 `KB-142` 原文，立即停下报告原因。
