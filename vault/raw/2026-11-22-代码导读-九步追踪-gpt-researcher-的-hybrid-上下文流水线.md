---
title: "代码导读：九步追踪 GPT Researcher 的 Hybrid 上下文流水线"
origin: "/Users/haorangong/Github/chicogong/experiments/agent-systems/docs/systems/gpt-researcher/code-walkthrough.md"
sha256: "0cb143a3263115486492d19d801cec3e38c36e8485c1d9f1892923b584fe2eb2"
ingested_at: "2026-11-22T13:54:22.832Z"
tags: []
---

# 代码导读：九步追踪 GPT Researcher 的 Hybrid 上下文流水线

# 代码导读：九步追踪 GPT Researcher 的 Hybrid 上下文流水线

[返回 GPT Researcher 剖面](README.md) · [固定源码版本 `6f998577`](https://github.com/assafelovic/gpt-researcher/tree/6f998577d547b1e54ec662dac63583aa11e3b84b)

本篇供希望对照 Python 源码细看数据流转的读者选读。我们锁定一条明确路径：普通研究报告（`ResearchReport`，非 `DeepResearch`）、混合来源（`ReportSource.Hybrid`）、默认非 Granite 的 `PromptFamily`、未额外传入 `source_urls` 或 `ext_context`（[提示词家族分发](https://github.com/assafelovic/gpt-researcher/blob/6f998577d547b1e54ec662dac63583aa11e3b84b/gpt_researcher/prompts.py#L879-L903)）。

```text
conduct_research()
  ├─ DocumentLoader 加载本地/指定文档
  ├─ asyncio.gather 双路并发：
  │    ├─ 路 A：带 document_data 拆子问题提取（若文档为空会回退搜网页！）
  │    └─ 路 B：传空列表拆子问题 → 搜索去重抓取网页
  ├─ ContextCompressor 快/慢双路径压缩（附 Source / Title / Content）
  └─ join_local_web_documents 合并存入 self.context → write_report()
```

## 沿调用链走完九步

1. **初始化状态容器**：`GPTResearcher.__init__()` 保存 `report_source`、`source_urls`、`document_urls`、`query_domains`，并初始化 URL 去重集合 `visited_urls` 与存放研究材料的 `self.context`。调用 `conduct_research()` 后，非 `DeepResearch` 任务统一交给 `ResearchConductor.conduct_research()` 执行并将返回值赋给 `self.context`（[构造函数状态](https://github.com/assafelovic/gpt-researcher/blob/6f998577d547b1e54ec662dac63583aa11e3b84b/gpt_researcher/agent.py#L138-L180) · [`conduct_research` 入口](https://github.com/assafelovic/gpt-researcher/blob/6f998577d547b1e54ec662dac63583aa11e3b84b/gpt_researcher/agent.py#L331-L401)）。
2. **注意 `source_urls` 的抢先分支**：在 `ResearchConductor.conduct_research()` 中，程序会**先检查调用方是否传入了显式 `source_urls`**，没有传才会进入后面的 `report_source == ReportSource.Hybrid` 分支——这意味着一旦传了 `source_urls`，并不会走下面的混合并发逻辑，而是改走 `_get_context_by_urls()`（[来源分支优先级](https://github.com/assafelovic/gpt-researcher/blob/6f998577d547b1e54ec662dac63583aa11e3b84b/gpt_researcher/skills/researcher.py#L144-L186)）。
3. **装载文档并发起双路 `gather`**：进入 `Hybrid` 后，有 `document_urls` 则用 `OnlineDocumentLoader`，否则用 `DocumentLoader` 从 `doc_path` 加载文档（若配置了 `vector_store` 会顺带写入向量库）。随后 `asyncio.gather()` 并发调用两次 `_get_context_by_web_search()`：第一路带上 `document_data`，第二路传空列表 `[]`（[Hybrid 装载与并发调用](https://github.com/assafelovic/gpt-researcher/blob/6f998577d547b1e54ec662dac63583aa11e3b84b/gpt_researcher/skills/researcher.py#L172-L186)）。
4. **两路各自拆解子问题（留意规划阶段的联网调用）**：在 `_get_context_by_web_search()` 内，无论文档路还是网页路都会先调 `plan_research()` 生成子问题提纲——而 `plan_research()` 默认会先用首个检索器（retriever）做一次初始搜索来辅助列提纲！因此即便你以为“文档路只看本地文件”，规划阶段仍可能按检索器配置触发外部查询。拿到子问题列表后，程序把原始总问题追加进去，再次用 `asyncio.gather()` 并发处理各个子问题（[`plan_research` 初始检索](https://github.com/assafelovic/gpt-researcher/blob/6f998577d547b1e54ec662dac63583aa11e3b84b/gpt_researcher/skills/researcher.py#L50-L95) · [子问题并发执行](https://github.com/assafelovic/gpt-researcher/blob/6f998577d547b1e54ec662dac63583aa11e3b84b/gpt_researcher/skills/researcher.py#L362-L398)）。
5. **获取原文与空文档回退**：`_process_sub_query()` 在收到非空文档列表时直接从中提取材料；**但当 `scraped_data` 为空（包括本地目录没加载到文档的情况）时，条件分支会自然滑向 `_scrape_data_by_urls()` 去搜网页**！网页路径根据 retriever 的 `requires_scraping` 决定重新抓取还是直接复用 `raw_content`，并通过 `visited_urls` 跳过重复链接（[子问题回退条件](https://github.com/assafelovic/gpt-researcher/blob/6f998577d547b1e54ec662dac63583aa11e3b84b/gpt_researcher/skills/researcher.py#L595-L606) · [网页去重与抓取](https://github.com/assafelovic/gpt-researcher/blob/6f998577d547b1e54ec662dac63583aa11e3b84b/gpt_researcher/skills/researcher.py#L826-L935)）。
6. **快慢两档上下文提纯**：`ContextManager.get_similar_content_by_query()` 调用 `ContextCompressor`。当材料总字符数低于 `COMPRESSION_THRESHOLD`（默认 8,000 字符）且文档数未超上限时，直接走快路径格式化；超出阈值时才做分块与 embedding 相似度检索。输出统一格式化为带 `Source`、`Title`、`Content` 三要素的文本块，为后续写引文留好锚点（[压缩管理入口](https://github.com/assafelovic/gpt-researcher/blob/6f998577d547b1e54ec662dac63583aa11e3b84b/gpt_researcher/skills/context_manager.py#L37-L64) · [8,000 字符阈值与压缩分支](https://github.com/assafelovic/gpt-researcher/blob/6f998577d547b1e54ec662dac63583aa11e3b84b/gpt_researcher/context/compression.py#L127-L188) · [三要素输出格式](https://github.com/assafelovic/gpt-researcher/blob/6f998577d547b1e54ec662dac63583aa11e3b84b/gpt_researcher/prompts.py#L554-L566)）。
7. **两路汇合落入 `researcher.context`**：各自拼完非空子问题结果后，`PromptFamily.join_local_web_documents()` 把两路字符串嵌进“本地文档”与“网页来源”两段标签中存入 `researcher.context`；若开启了 `curate_sources` 则在落定前再做一轮来源精选（Granite 模板覆写了另一套拼接格式，见[子问题结果汇总](https://github.com/assafelovic/gpt-researcher/blob/6f998577d547b1e54ec662dac63583aa11e3b84b/gpt_researcher/skills/researcher.py#L380-L398) · [默认拼接实现](https://github.com/assafelovic/gpt-researcher/blob/6f998577d547b1e54ec662dac63583aa11e3b84b/gpt_researcher/prompts.py#L563-L566) · [Granite 覆写实现](https://github.com/assafelovic/gpt-researcher/blob/6f998577d547b1e54ec662dac63583aa11e3b84b/gpt_researcher/prompts.py#L756-L834) · [保存与可选筛选](https://github.com/assafelovic/gpt-researcher/blob/6f998577d547b1e54ec662dac63583aa11e3b84b/gpt_researcher/skills/researcher.py#L209-L241)）。
8. **写作交接与重试回退**：`GPTResearcher.write_report()` 把 `self.context` 传给 `ReportGenerator.write_report()`；确认 `_ctx.strip()` 非空后调用 `generate_report()` 请求 LLM 撰写报告，若首次消息组织方式报错还会尝试备用组织格式重试一次（[写作交接](https://github.com/assafelovic/gpt-researcher/blob/6f998577d547b1e54ec662dac63583aa11e3b84b/gpt_researcher/agent.py#L451-L492) · [非空检查](https://github.com/assafelovic/gpt-researcher/blob/6f998577d547b1e54ec662dac63583aa11e3b84b/gpt_researcher/skills/writer.py#L77-L124) · [LLM 生成与重试](https://github.com/assafelovic/gpt-researcher/blob/6f998577d547b1e54ec662dac63583aa11e3b84b/gpt_researcher/actions/report_generation.py#L249-L326)）。
9. **空结果边界核对**：单个子问题抛异常时会被捕获记日志并返回空串；若两路所有子问题均返回空，默认 `join_local_web_documents()` 仍会返回仅含两行英文标题的非空字符串，从而通过 `_ctx.strip()` 检查。因此上层应用验收报告时应独立核查有效来源条数与正文引文对应关系（[空结果汇集](https://github.com/assafelovic/gpt-researcher/blob/6f998577d547b1e54ec662dac63583aa11e3b84b/gpt_researcher/skills/researcher.py#L380-L398) · [子问题异常兜底](https://github.com/assafelovic/gpt-researcher/blob/6f998577d547b1e54ec662dac63583aa11e3b84b/gpt_researcher/skills/researcher.py#L644-L653) · [拼接模板](https://github.com/assafelovic/gpt-researcher/blob/6f998577d547b1e54ec662dac63583aa11e3b84b/gpt_researcher/prompts.py#L563-L566) · [`_ctx.strip()` 判断](https://github.com/assafelovic/gpt-researcher/blob/6f998577d547b1e54ec662dac63583aa11e3b84b/gpt_researcher/skills/writer.py#L77-L88)）。

## 来源与边界

本篇基于 [`assafelovic/gpt-researcher@6f998577d547b1e54ec662dac63583aa11e3b84b`](https://github.com/assafelovic/gpt-researcher/tree/6f998577d547b1e54ec662dac63583aa11e3b84b) 静态核对，根许可证记录见[来源台账](../../../sources/systems.json)；未实际运行联网检索器、向量库写入或大模型报告生成。
