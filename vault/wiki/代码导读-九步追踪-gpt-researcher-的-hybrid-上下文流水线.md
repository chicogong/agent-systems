# 代码导读：九步追踪 GPT Researcher 的 Hybrid 上下文流水线

> Synthesized concept page maintained by Aimake LLM Wiki.

## Key Evidence & Provenance

### Source Snapshot (2026-11-22)
- **Origin**: `/Users/haorangong/Github/chicogong/experiments/agent-systems/docs/systems/gpt-researcher/code-walkthrough.md`
- **SHA-256**: `0cb143a326311548` · Raw: [[../raw/2026-11-22-代码导读-九步追踪-gpt-researcher-的-hybrid-上下文流水线.md|2026-11-22-代码导读-九步追踪-gpt-researcher-的-hybrid-上下文流水线.md]]
- 本篇供希望对照 Python 源码细看数据流转的读者选读。我们锁定一条明确路径：普通研究报告（`ResearchReport`，非 `DeepResearch`）、混合来源（`ReportSource.Hybrid`）、默认非 Granite 的 `PromptFamily`、未额外传入 `source_urls` 或 `ext_context`（提示词家族
- conduct_research()
- ├─ DocumentLoader 加载本地/指定文档
- ├─ asyncio.gather 双路并发：
- │    ├─ 路 A：带 document_data 拆子问题提取（若文档为空会回退搜网页！）
