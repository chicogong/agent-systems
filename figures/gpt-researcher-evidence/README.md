# 图的文字版：先收集资料，再交给写作器

[返回章节](../../docs/systems/gpt-researcher/README.md) · [手机查看原尺寸 SVG](diagram.svg) · [PNG](preview.png)

你手里已有几份文档，还想补充网上的说明。GPT Researcher 的 Hybrid（混合来源）流程先读取文档，再同时整理两路材料，最后把它们合成报告上下文，交给大模型写作。

## 按图中的顺序读

1. **先把文档读进来。** `DocumentLoader` 负责加载文档，图内“在线加载器”对应 `OnlineDocumentLoader`。若配置了向量库加载，也在这一阶段完成。先读完文档，才进入下面的两路并发处理。
2. **一路整理文档，一路查网页。** 文档有内容时，第一路从已加载文档整理出 `local context`（文档分支的上下文）；第二路以空文档输入 `[]` 开始，规划子问题、检索网址、抓取正文，形成 `web context`（网页分支的上下文）。代码用 `asyncio.gather` 同时执行两次 `_get_context_by_web_search`，图中的并发框表示这一段工作。
3. **把两份材料合起来。** `join_local_web_documents` 分别加上来源标签，再拼接内容。研究器将结果保存为 `researcher.context`，配置需要时再筛选来源。
4. **交给写作器。** `ReportGenerator` 把上下文放进报告提示，由 LLM（大模型）组织成报告。提示要求引用来源，交稿时还要将报告中的说法和引用逐项对回原文。

## 图里的两处特殊情况

**文档一路也可能转去查网页。** 加载结果为空时，`_process_sub_query()` 会回退到网页检索和抓取。`local context` 因此是分支名称，检查实际来源时，要看取得的内容和 URL。[单个子查询处理](https://github.com/assafelovic/gpt-researcher/blob/6f998577d547b1e54ec662dac63583aa11e3b84b/gpt_researcher/skills/researcher.py#L510-L625)

**有标签，还得有正文。** 写作器会拒绝真正的空上下文字符串。但本图使用的默认 `PromptFamily`（提示模板）会添加固定标签，即使两路正文都空，拼接结果仍可能含有标签文字。交稿检查因此要确认至少有一份来源带着有效正文，再核对引用。[默认拼接](https://github.com/assafelovic/gpt-researcher/blob/6f998577d547b1e54ec662dac63583aa11e3b84b/gpt_researcher/prompts.py#L564-L566) `Granite3PromptFamily` 和 `Granite33PromptFamily` 使用另一种拼接方式，需分别查看。[Granite 分支](https://github.com/assafelovic/gpt-researcher/blob/6f998577d547b1e54ec662dac63583aa11e3b84b/gpt_researcher/prompts.py#L756-L834)

## 版本与范围

图对应 [`assafelovic/gpt-researcher@6f998577`](https://github.com/assafelovic/gpt-researcher/tree/6f998577d547b1e54ec662dac63583aa11e3b84b) 的普通 `ReportSource.Hybrid` 源码路径：未使用 `DeepResearch` 或 Granite 提示模板，也未指定 `source_urls` 或外部写作上下文。这里依据源码说明流程，尚未运行一次真实检索和报告生成。

通过 MCP 接入的检索工具（MCP retriever）、图片预生成、DeepResearch、其他来源类型和实际引用检查，留在对应专题中展开。

编辑 `build.py` 后运行 `python3 figures/gpt-researcher-evidence/build.py`，再用 `excalidraw-agent` renderer 从原生 `scene.excalidraw` 导出 SVG 和 PNG。
