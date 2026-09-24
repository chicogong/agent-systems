# 动手：在一条可运行轨迹里分清提案、执行与验收

[返回学习路线](../learning-path.md) · [Agent loop 的机制解释](../concepts/agent-loop.md) · [完成判断的证据](../comparisons/completion-and-evidence.md)

这是一条**不需要 API Key、仅用 Python 标准库**的练习。目标不是做一个有用的编码助手，而是亲手观察一个容易被“Agent 已完成”掩盖的区别：**提案不等于执行许可；工具调用成功不等于任务验收。**真实 Agent 的提案通常来自模型；这里的 `propose()` 用固定脚本代替模型，由宿主决定能否执行，再按原任务验证候选成果。因此实验只验证控制流，不证明真实模型的推理质量。

任务是：把配置文件中的 `timeout` 从 30 改为 5，保持 `retries=3`。要求先读配置、获准后再写、检查两个条件，最后只报告“可提交验收”（`candidate_ready`）或“受阻”（`blocked`）；**没有用户接受环节**。程序在系统临时目录创建 `config.json`，运行结束即清理，不改真实项目文件，也不调用网络。

## 运行与观察

从仓库根目录运行，Python 3.10 或更新版本即可：

```bash
python3 examples/first-agent-loop/demo.py --mode normal
python3 examples/first-agent-loop/demo.py --mode denied
python3 examples/first-agent-loop/demo.py --mode regression
python3 -m unittest discover -s examples/first-agent-loop -p 'test_*.py'
```

无需安装第三方包。三次运行都输出 JSON；`events` 按顺序记录提案、写入审批与工具结果。关键字段应为：

| 模式 | 最终 `status` | 最终配置 | 应看到的关键事件 |
| --- | --- | --- | --- |
| `normal` | `candidate_ready` | `timeout=5, retries=3` | `read → write → check`，写入获准，检查通过。 |
| `denied` | `blocked` | `timeout=30, retries=3` | 写入前 `approval.granted=false`，随后返回拒绝观察；没有写入。 |
| `regression` | `blocked` | `timeout=5, retries=0` | 写入执行了，但 `check` 报 `retry rule changed`。 |

在正常模式中，第二次提案的 `seen_results` 是 1，说明提案函数拿到了 `read` 的结果；第三次提案收到写入结果后才要求 `check`。这只模拟**下一步依赖上次观察**：固定脚本仅检查结果中的工具类型和 `ok`，不会根据读到的配置值规划写入参数。写入是练习宿主的本地工具，审批发生在调用前；`finish` 只是提案函数希望停止，外层 `run()` 仍独立检查配置，再将它标为 `candidate_ready`。这个状态不是“用户已接受”。

## 沿代码看四个控制点

完整可运行代码在仓库的 `examples/first-agent-loop/demo.py`，断言在同目录 `test_demo.py`。打开它们，按下面四个位置读，不必先理解所有 Python 语法：

1. `propose(observations, mode)` 只返回下一步提案，不能自行写文件。它把上次工具结果当输入；错误或拒绝会让它提出 `stop`。
2. `run()` 收到 `write` 提案时先记录 `approval`。拒绝时生成一次 `ok=false` 的观察并继续循环，**不调用** `execute()`。
3. 提案触发的工具读写集中在 `execute()`；`run()` 另负责初始化临时文件和独立终态读取。工具结果的 `ok=true` 仅表示这次调用完成；`write` 并不知道用户是否要求保留重试规则。
4. `check` 同时检查 `timeout=5` 与 `retries=3`；外层 `run()` 在 `finish` 时再检查当前文件状态。测试把正常、拒绝和回归三条路径固定下来。

[Agent loop 图](../../figures/agent-loop/diagram.svg)可作为阅读地图；[不看图的文字说明](../../figures/agent-loop/README.md)说明图中的提案、授权、工具、观察、停止与验证各指什么。这里的程序是这张概念图的**教学实现**，不是 Pi、Codex 或任何项目的源码复制。

## 自己改一次，再给出证据

先只读程序，猜测把 `check` 改成仅检查 `timeout == 5` 后，`regression` 模式会变成什么；再在临时练习副本中改动并运行测试。答案是：工具检查会误报通过，但外层 `run()` 的独立终态检查仍会将结果标成 `blocked`；第三个单测还会因为缺少 `retry rule changed` 而失败。若连外层检查也删掉，才可能误报 `candidate_ready`。接着恢复原检查，在实际输出里分别找出：哪一条证明**写入获准**，哪一条证明**写入执行过**，哪一条证明**两个条件均通过**。它们不能用同一个事件代替。

本练习没有真实模型、任意提案的参数模式校验、MCP、沙箱、持久会话或外部服务；临时目录里的文件写入也不模拟网络请求“服务端已接收但回执丢失”的未知状态。它不能直接改造成执行不可信模型输出的生产宿主。要研究远端结果未知，请读[超时后的对账与重试](../comparisons/permission-and-recovery.md)，不要把这里的本地拒绝路径当成远端幂等证明。下一轮可在独立练习中加入可控服务和稳定操作 ID，再记录请求、查询与重试的不同结局。
