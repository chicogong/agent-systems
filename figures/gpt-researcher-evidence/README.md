# 图的文字版：Hybrid 来源汇合

这张图对应 [`assafelovic/gpt-researcher@6f998577`](https://github.com/assafelovic/gpt-researcher/tree/6f998577d547b1e54ec662dac63583aa11e3b84b) 的非 DeepResearch、未指定 `source_urls` 或外部写作上下文的 `ReportSource.Hybrid` 路径。[返回章节](../../docs/systems/gpt-researcher/README.md)

1. 本地文档由 `DocumentLoader` 或 `OnlineDocumentLoader` 读取。一路使用这些文档形成 local context。
2. 另一路在没有预供文档的情况下规划子查询、调用网页检索器、获取 URL、抓取正文，再形成 web context。两路由 `asyncio.gather` 并发，不应画成先本地后网页。
3. `join_local_web_documents` 给两路上下文加标签并拼接；研究器保存为 `researcher.context`，之后可按配置做来源筛选。
4. `ReportGenerator` 对字符串意义上的空上下文有拒绝生成分支；有上下文时将其送入 LLM 报告提示。提示要求引用来源，但图不表示已核验每条主张。
5. 风险标注：即使双路正文为空，Hybrid 固定标签仍可能让拼接字符串非空，所以空串检查不能单独作为证据存在的证明。

图是静态源码说明，不是一次真实检索轨迹。MCP retriever、图片预生成、DeepResearch、其他来源类型和引用验收均不在本图范围。

编辑 `build.py` 后运行 `python3 figures/gpt-researcher-evidence/build.py`，再用 `excalidraw-agent` renderer 从原生 `scene.excalidraw` 导出 SVG 和 PNG。
