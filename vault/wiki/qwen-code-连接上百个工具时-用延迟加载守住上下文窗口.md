# Qwen Code：连接上百个工具时，用延迟加载守住上下文窗口

> Synthesized concept page maintained by Aimake LLM Wiki.

## Key Evidence & Provenance

### Source Snapshot (2026-11-22)
- **Origin**: `/Users/haorangong/Github/chicogong/experiments/agent-systems/docs/systems/qwen-code/README.md`
- **SHA-256**: `68afded525922ab7` · Raw: [[../raw/2026-11-22-qwen-code-连接上百个工具时-用延迟加载守住上下文窗口.md|2026-11-22-qwen-code-连接上百个工具时-用延迟加载守住上下文窗口.md]]
- 给编码 Agent 接上 GitHub、Jira、Postgres、Sentry 等五六个 MCP 服务后，很多团队会发现一个荒诞现象：用户连一句 `"你好"` 都还没发出去，光是一百多个工具的 JSON Schema 声明就已经先吃掉了三万多 token。更棘手的是，把上百份结构近似的参数表每轮原样塞进 `tools` 列表，不仅拖慢首字延迟，还会严重稀释
- Qwen Code 用**延迟工具加载**（Deferred Tools：`tool_search` → `tool_call`）解开了这个「工具广度」与「上下文精度」的死结：程序在本地注册表里保管全量工具，但开局只向模型暴露高频核心工具与两个轻量元入口；低频外部工具平时隐身，等模型真正需要时先搜 Schema、再借壳发起调用。
- 图的文字版 · 可编辑图源 · 关键代码导读
- 所有工具启动时都会进入本地 `ToolRegistry`，但 `getFunctionDeclarations()` 在构造发给大模型的原生 `tools` 列表时，会主动筛掉仍处于隐藏状态的延迟工具。通过 MCP 协议接入的外部工具默认标记 `shouldDefer=true`（除非配置了强制常驻 `alwaysLoad`、命中 `visibleTools
- 当模型意识到手头缺少某类外部能力时，先调用常驻可见的 `tool_search`：既可以用关键词在隐藏的延迟工具池里模糊检索，也可以用 `select:<name>` 按精确名称点名查看（包括重看已显示工具的说明）。
