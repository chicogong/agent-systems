# 动手：在一条可运行轨迹里分清提案、执行与验收

[返回学习路线](../learning-path.md) · [Agent loop 的机制解释](../concepts/agent-loop.md) · [完成判断的证据](../comparisons/completion-and-evidence.md)

这个小实验会完成一次配置修改：读取原文件，把超时从 30 秒改成 5 秒，保留重试次数，再读回检查。你会看到“提出下一步 → 获得许可 → 工具执行 → 返回结果”的顺序。运行后留下三样学习成果：一条正常路径、写后配置，以及你对各步分工的说明。

任务要求是：`timeout=5`、`retries=3`，先读配置、获准后再写。正常路径返回 `candidate_ready`，意思是“候选成果已经准备好，可以交给用户检查”。另外两条路径让你观察许可被拒和重试规则被改坏的情况。

这是可选的**机制小实验**，用固定 `propose()` 脚本代替真实模型，适合观察控制流程。运行前请确认：Python 3.10+，无需 API Key 或第三方包；程序只在系统临时目录创建 `config.json`，结束即清理，不改项目文件、不联网。

## 先完成一次正常修改

从仓库根目录运行，Python 3.10 或更新版本即可：

```bash
python3 examples/first-agent-loop/demo.py --mode normal
python3 -m unittest discover -s examples/first-agent-loop -p 'test_*.py'
```

程序输出 JSON；`events` 是按顺序排好的过程记录。先找到 `status=candidate_ready` 和 `config` 中的 `timeout=5, retries=3`，再沿 `events` 找到读取、许可、写入和检查。这样就把最终成果与过程对应起来了。

接着比较两个变化：

```bash
python3 examples/first-agent-loop/demo.py --mode denied
python3 examples/first-agent-loop/demo.py --mode regression
```

三种情况的关键字段如下：

| 模式 | 最终 `status` | 最终配置 | 应看到的关键事件 |
| --- | --- | --- | --- |
| `normal` | `candidate_ready` | `timeout=5, retries=3` | `proposal: read` → 读结果 → `proposal: write` → `approval.granted=true` → 写结果 → `proposal: check` → 检查通过。 |
| `denied` | `blocked` | `timeout=30, retries=3` | 会看到 `proposal: write` 和一条 `tool_result`，但 `approval.granted=false`；文件**未改**，结果说明拒绝发生在执行前。 |
| `regression` | `blocked` | `timeout=5, retries=0` | 写入获准且执行了，但 `check` 的结果是 `ok=false`、`retry rule changed`。 |

例如 `denied` 模式中，关键事件按顺序是：

```json
[
  {"event":"proposal","tool":"write","seen_results":1},
  {"event":"approval","granted":false},
  {"event":"tool_result","tool":"write","ok":false,"detail":"write denied before execution"}
]
```

这是完整 `events` 中三个相邻对象的摘录。第一条提出写入，第二条记录许可被拒，第三条把拒绝结果送回循环；文件仍保持原值。读日志时，把 `event`、工具名和 `ok` 一起看，就能认出每条记录所处的阶段。

回看正常路径：第二次提案的 `seen_results=1` 表示它已经收到读取结果；收到写入结果后才提出 `check`。宿主是组织这些步骤的外层程序，它在写入前处理许可，在 `finish` 时独立检查当前配置，再返回 `candidate_ready`。

## 沿代码看四个位置（可选）

想继续读代码，再打开 [`demo.py`](../../examples/first-agent-loop/demo.py) 和 [`test_demo.py`](../../examples/first-agent-loop/test_demo.py)。`observations` 是提案函数收到的工具结果，`events` 是给读者看的过程记录。按下面四处阅读即可，暂时跳过不熟悉的 Python 语法。

1. `propose(observations, mode)` 只返回下一步提案，不能自行写文件。它把上次工具结果当输入；错误或拒绝会让它提出 `stop`。
2. `run()` 收到 `write` 提案时先记录 `approval`。拒绝时生成一次 `ok=false` 的观察并继续循环，**不调用** `execute()`。
3. 提案触发的工具读写集中在 `execute()`；`run()` 另负责初始化临时文件和独立终态读取。工具结果的 `ok=true` 仅表示这次调用完成；`write` 并不知道用户是否要求保留重试规则。
4. `check` 同时检查 `timeout=5` 与 `retries=3`；外层 `run()` 在 `finish` 时再检查当前文件状态。测试把正常、拒绝和回归三条路径固定下来。

[Agent loop 图](../../figures/agent-loop/diagram.svg)可作为阅读地图；[不看图的文字说明](../../figures/agent-loop/README.md)说明图中的提案、授权、工具、观察、停止与验证各指什么。这里的程序是这张概念图的**教学实现**，不是 Pi、Codex 或任何项目的源码复制。

## 自己改一次，再给出证据

先只读程序，猜测把 `check` 改成仅检查 `timeout == 5` 后，`regression` 模式会变成什么；再在临时练习副本中改动并运行测试。只改 `execute()` 中的检查条件，保留其他代码。先写下你的预测、运行结果与哪一层发现问题，再看本篇末尾的参考答案。

恢复原检查后，在 `normal` 输出里核对三份证据：

| 要检查什么 | 对应输出 | 接下来查看什么 |
| --- | --- | --- |
| 写入获准 | `event=approval, granted=true` | 实际写入结果。 |
| 本例写入完成 | `event=tool_result, tool=write, ok=true`，`detail` 中是写后配置 | 写后配置是否满足两个条件。 |
| 工具检查通过 | `event=tool_result, tool=check, ok=true` | `finish` 时宿主的独立读回。 |

宿主的最终检查体现在最外层 `status` 和 `config` 中，没有单独事件。比较两个 `blocked`：`denied` 没有执行写入，`regression` 已经改错了配置。状态相同，修复位置却不同；过程记录能帮你找到区别。

## 本实验的范围与下一步

固定脚本只检查工具类型和 `ok`，不会根据读取值规划任意写入参数；这里的日志也不是模型的隐藏思考。程序还有 5 步上限，耗尽会返回 `budget_exhausted`，但上述三条路径都不会走到它。候选成果之后的用户接受环节尚未实现。

这个程序用于讲控制流程，没有真实模型、任意提案参数校验、MCP、沙箱或持久会话，也未模拟文件系统谎报成功。接入不可信模型输出前，需要另做安全设计与测试。

想了解远端操作，再选[回执丢失后的对账练习](remote-effect.md)：它用模拟服务和稳定操作 ID 观察“已接收但没拿到答复”的情况。两个程序独立，临时文件无需保留。

## 参考答案：先完成预测再看

只把 `execute()` 中的 `check` 改为检查 `timeout == 5` 时，`regression` 的工具检查会误报通过，但外层 `run()` 的独立终态检查仍会把结果标成 `blocked`；第三个单测还会因缺少 `retry rule changed` 而失败。若连外层检查也删掉，才可能误报 `candidate_ready`。对照你记录的三件事：是哪次工具检查给了假绿灯、哪一层保住了最终状态、哪条测试发现了错误说明。这里训练的是追踪证据覆盖范围，不是记住 `blocked` 这个单词。
