# 开放协作协议栈：AGENTS.md、MCP 演进与 A2A 跨代理委托

> Synthesized concept page maintained by Aimake LLM Wiki.

## Key Evidence & Provenance

### Source Snapshot (2026-11-22)
- **Origin**: `/Users/haorangong/Github/chicogong/experiments/agent-systems/docs/concepts/open-agent-protocols.md`
- **SHA-256**: `0b0aa3cc2b30e486` · Raw: [[../raw/2026-11-22-开放协作协议栈-agents-md-mcp-演进与-a2a-跨代理委托.md|2026-11-22-开放协作协议栈-agents-md-mcp-演进与-a2a-跨代理委托.md]]
- 当团队从“个人在本地装个编码插件”走向“多工具、跨服务、跨团队 Agent 协同”时，往往会接连撞上三堵生态墙：
- 1. **项目规矩到处重复抄写**：同一个人仓库里既有前端又有后端，有人用 Codex、有人用 Claude Code、有人用 IDE 插件，测试命令与禁改目录写在不同私有配置里，改一处漏三处；
- 2. **远端工具鉴权与中途追问卡壳**：把内部工单或云平台封装成远端 MCP 服务后，静态环境变量密钥不敢发给全员，工具跑到一半发现缺一个必填审批人字段，只能直接抛错重来；
- 3. **拿同步工具接口硬调长耗时外部 Agent**：想让主编码 Agent 请安全团队维护的“渗透回归 Agent”做一次全链路核查，如果硬把对方包成一个普通 MCP Tool 调用，一跑十分钟不仅连接频频超时，安全团队也不可能把自家的私有提示词、漏洞库与内部子工具暴露给调用方。
- 这三类摩擦之所以反复出现，是因为它们原本就处在三个截然不同的工程切面上。随着 Linux 基金会旗下 **Agentic AI Foundation（AAIF）** 等开放治理体系成形，行业逐渐收敛出三层职责正交的标准：**`AGENTS.md` 管代码库静态进场约定，MCP 管纵向连接工具与资源，A2A（Agent2Agent）管横向委托独立黑盒 Agen
