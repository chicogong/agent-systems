# 固定输入预算的教学模拟

完整教程：[存下的历史不等于本轮可见上下文](../../docs/labs/context-budget.md)。

Python 3.10+，仅使用标准库，不需 API Key、第三方包或网络。所有记录是虚构数据，保存在本次进程的固定元组中；这里没有真实模型、持久记忆库、tokenizer、向量检索或 Mem0／Letta 调用，也不执行发布。

从仓库根目录运行：

```bash
python3 examples/context-budget/demo.py --mode full
python3 examples/context-budget/demo.py --mode recent
python3 examples/context-budget/demo.py --mode retrieve
python3 -m unittest discover -s examples/context-budget -p 'test_*.py'
```

`full` 默认预算 1200；`recent` 与 `retrieve` 默认预算 220。三种模式都用同一个装配器，逐条尝试完整记录：先放显式检索命中的记录，再从最新记录开始；放不下就跳过，继续尝试后面的记录。`full` 只是预算较大，不绕过预算检查。预算统计规则、问题、记录 ID、正文与换行的 Python `len(str)`，**是 Unicode 码点数，不一定等于显示字形数；这里只用它度量教学输入，不是 token 数或 UTF-8 字节数**。默认三轮实际占用依次为 248、212、217，必要规则与问题占 56。

输出分开呈现 `stored_records`（完整历史）、`context`（本轮输入）、`answer`（固定规则判读器的结果）、`audit`（验收端对照完整记录）。判读器只收到 `context`，不会读取完整历史、检索结果或验收信息；它只匹配固定的禁止发布短语，不能泛化理解自然语言。

试着修改预算，先预测再运行：

```bash
python3 examples/context-budget/demo.py --mode recent --budget 248
python3 examples/context-budget/demo.py --mode retrieve --budget 91
python3 examples/context-budget/demo.py --mode recent --budget 10
```

第一条可装入全部 5 条记录；第二条虽检索命中 `r1`，该完整记录仍放不下，最终只装入 `r3`，占满 91 字符；第三条连必要规则与问题也放不下，返回 `budget_too_small`，不调用判读器，CLI 退出码为 **2**（预期拒绝，不是程序崩溃）。不把预算错误通过截断问题隐藏掉。
