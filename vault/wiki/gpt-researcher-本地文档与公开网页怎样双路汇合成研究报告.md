# GPT Researcher：本地文档与公开网页怎样双路汇合成研究报告

> Synthesized concept page maintained by Aimake LLM Wiki.

## Key Evidence & Provenance

### Source Snapshot (2026-11-22)
- **Origin**: `/Users/haorangong/Github/chicogong/experiments/agent-systems/docs/systems/gpt-researcher/README.md`
- **SHA-256**: `6cc8d424aadb9b93` · Raw: [[../raw/2026-11-22-gpt-researcher-本地文档与公开网页怎样双路汇合成研究报告.md|2026-11-22-gpt-researcher-本地文档与公开网页怎样双路汇合成研究报告.md]]
- 写一份靠谱的深度技术调研，最难的往往不是最后让大模型润色成文，而是前面那一步：**你手头既有几份内部 PDF 或本地笔记，又需要去全网搜最新进展；怎样让这两路材料按统一的子问题并行收集、剔除无关噪音，还能在最终报告里保住真实出处？**
- 如果把整本本地文档和几十个网页全文直接倒进模型提示词，不仅费用高昂，还会触发严重的上下文稀释（Context Rot）。GPT Researcher 在 `ReportSource.Hybrid`（混合来源）模式下的做法，是把“研究”和“写作”拆成两个职责分明的阶段：**先由研究器（ResearchConductor）兵分两路拆解子问题、抓取并压缩相关片段，
- 可编辑图源 · PNG 预览 · 图的文字版 · 九步代码导读
- 沿着普通研究报告（非 `DeepResearch`）的 `Hybrid` 主路径，整条数据流水线按以下五步推进：
- 1. **总控分流**：调用 `GPTResearcher.conduct_research()` 时，普通报告任务被委托给 `ResearchConductor.conduct_research()`，最终产出的精选材料存回 `self.context`（`DeepResearch` 递归研究走另一条独立分支，见主入口源码）。
