# Mem0：外挂记忆层的事实提炼、混合打分与调用方边界

> Synthesized concept page maintained by Aimake LLM Wiki.

## Key Evidence & Provenance

### Source Snapshot (2026-11-22)
- **Origin**: `/Users/haorangong/Github/chicogong/experiments/agent-systems/docs/systems/mem0/README.md`
- **SHA-256**: `5139f9fb484ede2c` · Raw: [[../raw/2026-11-22-mem0-外挂记忆层的事实提炼-混合打分与调用方边界.md|2026-11-22-mem0-外挂记忆层的事实提炼-混合打分与调用方边界.md]]
- 不少团队把 Mem0 这类外挂记忆组件接进应用时，默认它会自动替 Agent 打理好一切：对话结束丢进去，下次提问搜出来，新旧事实自动覆盖、上下文自动对齐。真正跑起来才会撞上三道现实落差：第一，直接把原始聊天切片塞进向量库会搜出一堆没有主语的半截废话，而开启模型提炼（`infer=True`）后，开源版当前 V3 路径实际执行的是 **ADD-only**（
- 与 Letta Code 在宿主内部统筹目录层级与系统提示重编译不同，Mem0 把边界切得很薄：**它只做对话事实的提取存储（`add`）与作用域检索排序（`search`），不接管 Agent 的上下文编排**。看清这条边界，才能用好外挂记忆层。
- 可编辑图源 · PNG 预览 · 图的文字版
- 按阅读顺序跟代码
- 如果把用户原话“太啰嗦了，以后先给三行结论再贴链接，对了今天北京挺冷的”原封不动存进向量库，寒暄噪音会拉偏向量表示。`Memory.add()` 的核心价值，是在落库前加了一道由大模型驱动的**事实蒸馏漏斗**：
