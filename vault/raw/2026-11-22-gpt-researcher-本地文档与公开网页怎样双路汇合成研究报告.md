---
title: "GPT Researcher：本地文档与公开网页怎样双路汇合成研究报告"
origin: "/Users/haorangong/Github/chicogong/experiments/agent-systems/docs/systems/gpt-researcher/README.md"
sha256: "6cc8d424aadb9b9394571c053d506144d1e684129153c5d583db3a0dbf9e6bd3"
ingested_at: "2026-11-22T13:54:22.828Z"
tags: []
---

# GPT Researcher：本地文档与公开网页怎样双路汇合成研究报告

# GPT Researcher：本地文档与公开网页怎样双路汇合成研究报告

[返回系统目录](../README.md) · [九步代码导读](code-walkthrough.md) · [图的文字版](../../../figures/gpt-researcher-evidence/README.md)

写一份靠谱的深度技术调研，最难的往往不是最后让大模型润色成文，而是前面那一步：**你手头既有几份内部 PDF 或本地笔记，又需要去全网搜最新进展；怎样让这两路材料按统一的子问题并行收集、剔除无关噪音，还能在最终报告里保住真实出处？**

如果把整本本地文档和几十个网页全文直接倒进模型提示词，不仅费用高昂，还会触发严重的上下文稀释（Context Rot）。GPT Researcher 在 `ReportSource.Hybrid`（混合来源）模式下的做法，是把“研究”和“写作”拆成两个职责分明的阶段：**先由研究器（ResearchConductor）兵分两路拆解子问题、抓取并压缩相关片段，拼成带来源标签的精选上下文，再移交给写作器（ReportGenerator）成稿**。

![GPT Researcher Hybrid 研究上下文的来源汇合图](../../../figures/gpt-researcher-evidence/diagram.svg)

[可编辑图源](../../../figures/gpt-researcher-evidence/scene.excalidraw) · [PNG 预览](../../../figures/gpt-researcher-evidence/preview.png) · [图的文字版](../../../figures/gpt-researcher-evidence/README.md) · [九步代码导读](code-walkthrough.md)

## 从“双路搜集”到“成文交付”的五步流水线

沿着普通研究报告（非 `DeepResearch`）的 `Hybrid` 主路径，整条数据流水线按以下五步推进：

1. **总控分流**：调用 `GPTResearcher.conduct_research()` 时，普通报告任务被委托给 `ResearchConductor.conduct_research()`，最终产出的精选材料存回 `self.context`（`DeepResearch` 递归研究走另一条独立分支，见[主入口源码](https://github.com/assafelovic/gpt-researcher/blob/6f998577d547b1e54ec662dac63583aa11e3b84b/gpt_researcher/agent.py#L331-L390)）。
2. **本地与网页双路并发（注意一个隐蔽的回退细节！）**：进入 `Hybrid` 分支后，程序先通过 `OnlineDocumentLoader` 或 `DocumentLoader` 读取指定文档，随后用 `asyncio.gather` 同时启动两路 `_get_context_by_web_search`——第一路传入已加载的 `document_data`，第二路传入空列表专跑网页检索，跑完后用 `prompt_family.join_local_web_documents` 拼合。**这里藏着一个光看分支名极易漏掉的细节**：如果本地目录实际上没读到任何文档（`document_data` 为空），第一路在 `_process_sub_query()` 里并不会原地返回空，而是会自动回退去跑网页搜索！因此验收来源时必须核查真实 URL 与内容，不能看见 `Hybrid` 就默认用上了本地资料（[来源并发分支](https://github.com/assafelovic/gpt-researcher/blob/6f998577d547b1e54ec662dac63583aa11e3b84b/gpt_researcher/skills/researcher.py#L164-L196) · [空文档回退网页](https://github.com/assafelovic/gpt-researcher/blob/6f998577d547b1e54ec662dac63583aa11e3b84b/gpt_researcher/skills/researcher.py#L510-L625) · [两路拼接格式](https://github.com/assafelovic/gpt-researcher/blob/6f998577d547b1e54ec662dac63583aa11e3b84b/gpt_researcher/prompts.py#L564-L566)）。
3. **拆解子查询与去重抓取**：每路先规划出一组子问题（sub-queries）并行处理；网页路径通过配置的检索器（也可接入 MCP retriever）拿到候选链接，经 `visited_urls` 集合过滤已访问网址后抓取正文或复用预取内容（[子查询规划与并发](https://github.com/assafelovic/gpt-researcher/blob/6f998577d547b1e54ec662dac63583aa11e3b84b/gpt_researcher/skills/researcher.py#L286-L407) · [单子查询执行](https://github.com/assafelovic/gpt-researcher/blob/6f998577d547b1e54ec662dac63583aa11e3b84b/gpt_researcher/skills/researcher.py#L510-L625) · [`visited_urls` 去重](https://github.com/assafelovic/gpt-researcher/blob/6f998577d547b1e54ec662dac63583aa11e3b84b/gpt_researcher/skills/researcher.py#L805-L823) · [正文抓取汇合](https://github.com/assafelovic/gpt-researcher/blob/6f998577d547b1e54ec662dac63583aa11e3b84b/gpt_researcher/skills/researcher.py#L900-L942)）。
4. **快慢双路径上下文压缩**：抓取到的原始长文不会原样塞进提示词，而是交给 `ContextManager` 驱动 `ContextCompressor` 提纯——总字数较少时直接走快路径格式化；文档较大时切块并用向量相似度（embedding）筛出与当前子查询最相关的片段，同时保留 `Source` 与 `Title` 元数据供后续标注出处；若开启了 `curate_sources` 还会再过一道来源筛选（[上下文管理](https://github.com/assafelovic/gpt-researcher/blob/6f998577d547b1e54ec662dac63583aa11e3b84b/gpt_researcher/skills/context_manager.py#L37-L63) · [压缩快慢路径](https://github.com/assafelovic/gpt-researcher/blob/6f998577d547b1e54ec662dac63583aa11e3b84b/gpt_researcher/context/compression.py#L117-L183) · [带出处格式化](https://github.com/assafelovic/gpt-researcher/blob/6f998577d547b1e54ec662dac63583aa11e3b84b/gpt_researcher/prompts.py#L556-L566) · [可选来源筛选](https://github.com/assafelovic/gpt-researcher/blob/6f998577d547b1e54ec662dac63583aa11e3b84b/gpt_researcher/skills/researcher.py#L210-L231)）。
5. **交棒写作器生成报告**：最后调用 `GPTResearcher.write_report()`，把 `self.context`（或外部显式传入的 `ext_context`）交给 `ReportGenerator` 组装写作提示词请求大模型成文（[写作入口](https://github.com/assafelovic/gpt-researcher/blob/6f998577d547b1e54ec662dac63583aa11e3b84b/gpt_researcher/agent.py#L451-L491) · [空上下文拦截](https://github.com/assafelovic/gpt-researcher/blob/6f998577d547b1e54ec662dac63583aa11e3b84b/gpt_researcher/skills/writer.py#L56-L95) · [LLM 报告生成](https://github.com/assafelovic/gpt-researcher/blob/6f998577d547b1e54ec662dac63583aa11e3b84b/gpt_researcher/actions/report_generation.py#L230-L310) · [提示词引用要求](https://github.com/assafelovic/gpt-researcher/blob/6f998577d547b1e54ec662dac63583aa11e3b84b/gpt_researcher/prompts.py#L300-L313)）。

## 读源码抓出的一个边界细节：“空壳标题”绕过非空检查

把拼接函数与写作器的守卫条件摆在一起看，会发现一个非常典型的工程边界：

在默认的**非 Granite 提示词家族**（`PromptFamily`）中，`join_local_web_documents` 会无条件拼出两行外壳标题：

```text
Context from local documents:
...
Context from web sources:
...
```

哪怕本地和网页两路颗粒无收、有效正文全是空，拼出来的字符串依然带着这两行英文标题！而下游写作器 `ReportGenerator` 目前只用 `_ctx.strip()` 检查字符串是否为空——这团“只有标题壳、没有实质材料”的字符串会顺利穿过非空守卫进入模型调用。因此，在生产应用外层做交付验收时，不能只看报告有字，必须核查是否至少有一条来源携带了非空正文，并把报告引文对回原始抓取记录（[`join_local_web_documents` 拼接](https://github.com/assafelovic/gpt-researcher/blob/6f998577d547b1e54ec662dac63583aa11e3b84b/gpt_researcher/prompts.py#L564-L566) · [Granite 模板不同覆写](https://github.com/assafelovic/gpt-researcher/blob/6f998577d547b1e54ec662dac63583aa11e3b84b/gpt_researcher/prompts.py#L756-L834) · [写作器 `_ctx.strip()` 检查](https://github.com/assafelovic/gpt-researcher/blob/6f998577d547b1e54ec662dac63583aa11e3b84b/gpt_researcher/skills/writer.py#L77-L88)）。

函数级逐步拆解可继续选读[九步代码导读](code-walkthrough.md)。

## 来源与边界

本文基于官方仓库 [`assafelovic/gpt-researcher@6f998577d547b1e54ec662dac63583aa11e3b84b`](https://github.com/assafelovic/gpt-researcher/tree/6f998577d547b1e54ec662dac63583aa11e3b84b)（核对日期 2026-09-24，Apache-2.0 许可）做静态源码剖析。覆盖范围限定于非 `DeepResearch`、未显式指定 `source_urls`、未外部注入 `ext_context` 且使用非 Granite `PromptFamily` 的 `ReportSource.Hybrid` 普通报告路径；未连接线上搜索引擎或评测生成报告的引用忠实度。
