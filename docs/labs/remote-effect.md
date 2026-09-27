# 动手：回执丢失后，先对账还是再执行？

[返回学习路线](../learning-path.md) · [审批与恢复的机制对照](../comparisons/permission-and-recovery.md) · [第一次本地练习](first-agent-loop.md)

上一条练习把“提案、批准、执行、验收”分开。这一次把镜头移到执行之后：请求可能已送达远端，宿主却没收到回执。**本地超时只能说明没有拿到答复，不能证明远端没做事。** 这是一个纯 Python、内存中的确定性模拟；不会连网、发布内容或调用真正的 Agent。它没有运行时计时器，而是直接用 `None` 模拟回执丢失。先理解上一条练习中的宿主与事件即可，两条程序不共享文件或状态。

设想任务是发布版本 `v1`。宿主在发送前分配稳定的 `operation_id=task-42:publish-v1`。模拟服务按这个 ID 记录已经接受的操作。它在 `lost_receipt` 路径里先接受请求，再故意丢掉答复；在 `no_lookup` 路径里连查询接口都不可用；`unsafe_new_id` 则故意用新 ID 发起第二次操作，展示一个常见错误。

这里的**操作 ID**是服务用来辨认“是否同一次操作”的标记；**回执**是服务给调用方的答复；**对账**是用其他证据查清请求是否已被接受。`accepted` 只表示假服务登记了操作，`effects` 数的是登记产生的模拟副作用，不验证版本内容、部署健康或用户验收。

## 跑四条轨迹

从仓库根目录执行，使用 Python 3.10 或更新版本，无第三方依赖：

```bash
python3 examples/remote-effect/demo.py --mode normal
python3 examples/remote-effect/demo.py --mode lost_receipt
python3 examples/remote-effect/demo.py --mode no_lookup
python3 examples/remote-effect/demo.py --mode unsafe_new_id
python3 -m unittest discover -s examples/remote-effect -p 'test_*.py'
```

| 路径 | 宿主拿到什么证据 | 宿主下一步 | 模拟的实际副作用数 |
| --- | --- | --- | --- |
| `normal` | 收到 `accepted` 回执 | 记录已确认 | 1 |
| `lost_receipt` | 回执为 `null`；按原 ID 查询到 `accepted` | 记录查询证据，不再发起新操作 | 1 |
| `no_lookup` | 回执为 `null`；查询能力不可用 | 标记 `unknown_stop`，暂停并让人对账 | 1；宿主此时**并不知道**这个数 |
| `unsafe_new_id` | 回执为 `null`；查询已确认原操作，却仍换 ID 重试 | 错误地制造第二次操作 | 2 |

程序输出的 `effects` 是教学模拟器给读者的**上帝视角**，不是宿主在真实超时后一定看得见的状态。尤其在 `no_lookup` 中，宿主只有“没有回执、不能查询”两个证据；即使这一次模拟里服务实际做了事，也只能报告未知，不能写“已失败”或“已成功”。

## 顺着代码辨认三本账

打开 [`demo.py`](../../examples/remote-effect/demo.py)，找出下面三个位置：

1. `run()` 在发送前确定 `operation_id`。如果调用方每次重试都换一个 ID，服务就无法把它识别为同一次操作。
2. `FakeService.submit()` 先把操作写进自己的 `operations`，然后才决定是否返回回执。`None` 是**回执丢失**，不是副作用未发生。只有这个假服务明确保证同一 ID 去重；换成真实 API 时必须核对其幂等语义和有效期。
3. `run()` 在回执丢失后按 ID 查询；`no_lookup` 模式中，宿主已知道服务没有查询能力，直接记录 `unavailable` 并停止，没有真的调用 `lookup()` 再捕获异常。`unsafe_new_id` 是刻意写出的反例，不是推荐恢复方式。

注意：即使查询暂时返回“查无记录”，也不能自动推断旧请求永远不会抵达；读回可能滞后，请求也可能仍在途。这个练习只实现“已找到”和“查询不可用”两个分支，没有模拟最终一致性、ID 过期或旧请求迟到。真实系统若不提供可信终态查询或相同 ID 的安全重放，就应保持未知并人工处理，而不是让模型凭语言判断。

## 自测：把“我知道什么”写清楚

先不看结果，预测 `lost_receipt` 和 `unsafe_new_id` 的副作用数。运行后对照：前者是 **1**，后者是 **2**。分别找出支持“请求已发出”“服务已接受”“又发起了另一操作”的事件：

| 结论 | 可核对事件 | 范围 |
| --- | --- | --- |
| 宿主调用了发送接口 | `event=submit`，原始操作 ID，`receipt=null` | 没拿到回执，本事件单独不能证明服务接受。 |
| 假服务已登记原操作 | `event=lookup, result=accepted` | 是按原 ID 取得的查询证据，不证明真实部署质量。 |
| 宿主又发起另一操作 | `event=unsafe_retry`，ID 以 `-retry` 结尾，`receipt=accepted` | 新 ID 没有命中原操作的去重记录。 |

如果只看第一次回执，`lost_receipt` 与 `unsafe_new_id` 有什么差别？答案是**没有**，两者都是 `null`；区别来自后续查询和操作 ID 的处理。为什么 `no_lookup` 输出 `effects=1`，状态却不是成功？因为这个数是模拟器揭示的内部状态，不是宿主取得的证据；宿主只能停在 `unknown_stop`。

最后，假设真实服务只支持“创建任务”，不支持按 ID 查询，也没有幂等键。给它加一个漂亮的 Agent UI、checkpoint 或“请勿重复”的提示词，能证明只执行一次吗？不能。这些分别改善交互、本地恢复和模型行为，却不替代远端的操作契约。对应的[四系统静态源码对照](../comparisons/permission-and-recovery.md)说明为什么批准、工具状态和 checkpoint 都不是远端收据。本文代码只证明模拟器内的四条路径，不证明那四个产品在真实部署中恰好一次执行。
