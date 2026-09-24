# 2026-09-24 静态源码与读图二审记录

[返回当前进度](../roadmap.md) · [写作与验收方法](../editorial-plan.md)

本轮由未参与这些章节写作的 AI 审稿任务重新打开固定版本源码，核对正文的关键因果链与发布图的事实箭头；另一个只读任务检查历史 QA 问题、网页窄屏入口和两张 PDF 实页。**这是第二视角的静态审稿，不是人类冷读、运行实测、完整上游审计或出版签收。**以下“未发现”只适用于列出的窄路径。

| 局部剖面 | 本轮核对的关键关系 | 证据入口与结论 |
| --- | --- | --- |
| [OpenHands](../systems/openhands/README.md) | `ActionEvent`、确认等待、再次 `run()` 与结果配对；图中的执行分支有条件。 | [固定版本](https://github.com/OpenHands/software-agent-sdk/tree/6ebd820d10794f1b52bb06ef6c19512888a1401b) · [代码导读](../systems/openhands/code-walkthrough.md) · [图的文字版](../../figures/openhands-action-events/README.md)。未发现需返工的主链错误。 |
| [Letta Code](../systems/letta/README.md) | local MemFS v1 的核心记忆范围、`memory()` 修改后的 Git 提交、同步成功且能力允许时的 worker 合并重编译。 | [固定版本](https://github.com/letta-ai/letta-code/tree/1f55d3dc66e238d203757fae288bb53f3adc7cd3) · [代码导读](../systems/letta/code-walkthrough.md) · [图的文字版](../../figures/letta-memory/README.md)。工具写入与 worker 合并仍按两条路径表述。 |
| [Mem0](../systems/mem0/README.md) | `infer=True` 的提取、去重、尝试写入；检索的语义候选与关键词／实体加分。 | [固定版本](https://github.com/mem0ai/mem0/tree/f8082a7345dadd9e042ebbc40b57b1498c8f6d63) · [代码导读](../systems/mem0/code-walkthrough.md) · [图的文字版](../../figures/mem0-retrieval/README.md)。主链未见错误；正文已收紧“批量 insert”措辞，保留返回 ADD 不证明逐项持久化的边界。 |
| [LangGraph](../systems/langgraph/README.md) | 指定 checkpoint 读取旧版本、`update_state` 生成带父指针的新版本、使用返回 config 续跑。 | [固定版本](https://github.com/langchain-ai/langgraph/tree/bdb85b5aa87a21de68371d2e534b81aeed398f57) · [代码导读](../systems/langgraph/code-walkthrough.md) · [图的文字版](../../figures/langgraph-checkpoints/README.md)。未把状态分叉说成外部副作用回滚。 |

历史 QA 的 Kimi Code／MiMo Code 来源登记已在 [`sources/systems.json`](../../sources/systems.json) 与正文中核对；`python3 scripts/check_sources.py` 检查 14 篇通过。OpenCode 的单个 `ToolPart.error` 不自动触发会话重试；[横向对照](../comparisons/loop-and-stop.md)已补固定版本 [`retry.ts` 的可重试判定与上限](https://github.com/anomalyco/opencode/blob/18ef3cc7c5a25b82114c953a80ccc09f4988f74e/packages/opencode/src/session/retry.ts#L85-L205)。审稿建议的初始行号与该固定文件不符，合稿时已重新打开原文件校正。

窄屏网页抽查以 390px 视口确认无横向溢出、能打开原尺寸 SVG；线上 107 页 PDF 的 LangGraph 第 78 页和 GPT Researcher 第 84 页、以及本地较新的 109 页导出均做了图页抽查，未见明显遮挡。严格图稿几何预检两图最低字号分别为 9.3 pt、9.2 pt。抽查不等于 25 张图的逐页视觉签收，也不保证实体纸面可读。

**尚未核验：**这四套系统的真实模型／provider 运行轨迹、故障注入、生产 saver、跨设备同步和外部副作用；其余系统篇的同等深度第二次源码复核；第三方权益；真实读者冷读及印刷样张。后续若改正文或图，应重新核对固定源码、`.excalidraw`、SVG／PNG 与图的文字版，而不是沿用本次结论。
