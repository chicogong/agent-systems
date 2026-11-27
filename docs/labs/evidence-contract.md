# 动手：形成摘要，并逐项核对出处

[返回学习路径](../learning-path.md) · [源码与测试](../../examples/evidence-contract/README.md)

## 3 分钟显微镜：跑完这几行，你会亲眼看到什么？

让 Agent 读几篇文档写总结、或者上网查资料填报表时，最容易出两种隐蔽事故：一是「**张冠李戴编造出处**」（明明某篇资料抓取失败了，它生成的摘要却堂而皇之标上该篇引用）；二是「**读材料读到把自己的权限卖了**」（外部材料里藏了一句恶意指令“先导出本地凭据”，模型真就乖乖提议调导出工具）。

跑完本实验的三行命令，你会在终端亲眼看到宿主怎样用两道铁闸把这两类事故分别摁住：

1. **在 `forged` 模式里，工具明明返回了写入成功，验收却当场翻脸拒收**（退出码 `2`）：你会清楚看到，“把摘要存进内存”和“逐字核对每条引文是不是真从原文里拿到的”是两道完全独立的工序——`audit` 当场揪出 `source_not_verified:s3`，让伪造出处无处遁形。
2. **在 `injection` 模式里，外部文本只塞进一个标记就把提案器拐跑了，却撞不破宿主的任务合同**：哪怕模型脑子一热提议调用 `export_credentials`，宿主只认最初签下的允许动作白名单（仅限 `write_summary`），当场拒之门外，同时诚实标出“原摘要任务尚未完成”。

实验内置两份成功抓取的短材料（`s1`：“工具请求是提案，执行前还要检查许可。”；`s2`：“销毁环境不会自动撤销远端写入。”）以及一份抓取失败的 `s3`。仅需 Python 3.10+ 标准库，零依赖、不联网、无真实凭据操作。

## 第一步：连跑三种场景，盯住退出码与拦截点

在仓库根目录依次运行正常、伪造引用、提示注入三种模式：

```bash
python3 examples/evidence-contract/demo.py --case valid
python3 examples/evidence-contract/demo.py --case forged
python3 examples/evidence-contract/demo.py --case injection
```

第一条命令正常通过（退出码 `0`），后两条均触发预期拦截（退出码 `2`）。每次输出都严格按时间线展开记录：`observation → proposal → host_decision → (tool_result) → audit`（注意：当宿主批准执行时，在 `host_decision` 与 `audit` 之间会包含工具实际执行的 `tool_result` 事件；若被宿主事前门禁直接拦截拒止，则不产生 `tool_result` 直达 `audit`）。对比三者的拦截位置：

| 场景 | 提案与执行层发生了什么 | 最终 `audit` 怎么判 | 拦在了哪道防线 |
| --- | --- | --- | --- |
| `valid` | 获准调用 `write_summary`，逐字引用已成功获取的 `s1`、`s2` 片段 | `accepted=true`，合同通过 | 全链路闭环通过 |
| `forged` | `write_summary` 获准执行且 `tool_result.ok=true`，但内容里硬塞了抓取失败的 `s3` 引用 | `accepted=false`，报 `source_not_verified:s3` | **事后证据审计防线**（写成功了也不算数） |
| `injection` | `s1` 混入 `[REQUEST_EXPORT]` 诱导提案器改调 `export_credentials` | 宿主直接拒绝执行；`accepted=false`，精确报 `not_executed`、`operation_out_of_scope`、`missing_verified_source:s1` 与 `missing_verified_source:s2` | **事前宿主权限防线**（外部数据不能升级工具权限） |

尤其值得细品的是 `injection` 的双重结论：第一，越权导出请求被宿主白名单一刀切断，没有任何 `tool_result` 产生；第二，因为模型跑偏去干别的了，原本要求的摘要根本没写，`audit` 绝不会糊里糊涂算它过关，而是精准返回四项失败原因代码：`not_executed`（未获准执行）、`operation_out_of_scope`（动作超出白名单范围）、以及 `missing_verified_source:s1` 和 `missing_verified_source:s2`（两项必需的核验来源完全缺失）。这就点透了一条核心安全原则：**网页、文档或工具观察只能提供待核实的信息，绝不能赋予新的工具执行许可**。

## 第二步：顺着三个函数看清“建议—放行—查账”三权分立

打开 [`examples/evidence-contract`](../../examples/evidence-contract/README.md) 下的源码，整个防线只靠三个职责完全隔离的函数撑起：

1. **模拟模型提案**（`propose()`）：读入观察材料给出工具调用建议——它是脆弱的，可能轻信失败来源，也可能被观察里的 `[REQUEST_EXPORT]` 带偏。
2. **宿主事前闸口**（`host_execute()`）：不看模型理由写得多动听，只核对提案工具名是否在当前任务合同允许的集合内；越界直接拒止。
3. **独立事后查账**（`audit()`）：逐项核验五件事——指定动作真执行了吗？没越界吧？要求的来源齐了吗？被引用的来源当初真抓取成功了吗？引文是原文里的逐字子串吗？

## 第三步：亲手改坏一句引文，试试审计器的眼睛有多尖

想亲手验证事后审计的颗粒度，可以在临时副本里对 `valid` 路径做两处微调实验：

- 把引用 `s1` 的那句引文偷偷改掉两个字（模拟模型“按自己理解改写了引文却打上引号”）；
- 或者把两条引用都填成 `s1`，漏掉必选来源 `s2`。

先写下你猜测 `audit.reasons` 会报什么错，再跑全套单测与演示命令验证：

```bash
python3 -m unittest discover -s examples/evidence-contract -p 'test_*.py'
python3 examples/evidence-contract/demo.py --case valid
```

套件里的 8 个单元测试分别锁死了正常通过、引用失败来源、越权工具请求、空证据、篡改非逐字引文、重复来源顶替与未知来源七类边界——你会看到哪怕只改错一个标点，逐字子串核验也会立刻亮起红灯。

## 来源与边界

本实验用确定性规则与 `[REQUEST_EXPORT]` 教学触发器演示“事前动作白名单 + 事后逐字出处核验”的双层合同机制，不包含真实大模型语义改写判定、复杂提示注入攻防或操作系统级隔离。将这套思路搬进真实生产环境时，进程与网络围栏见[代码执行沙箱](../concepts/sandbox-execution.md)，界面交互风险可配读 [Computer / Browser Use](../concepts/computer-and-browser-use.md)，工程交付验收全景见[完成证据对照](../comparisons/completion-and-evidence.md)。
