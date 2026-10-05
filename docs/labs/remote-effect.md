# 动手：按原操作 ID 找回回执

[返回学习路线](../learning-path.md) · [审批与恢复的机制对照](../comparisons/permission-and-recovery.md) · [第一次本地练习](first-agent-loop.md)

这次先看一个正常过程：宿主发送登记请求，服务接收并返回答复，宿主记下结果。然后让这份答复丢失，再用原操作 ID 查询。你会看到“登记了”和“收到答复”是发生在两边的两件事，也会得到一条可以解释的恢复路径。

设想任务是发布版本 `v1`。本实验用内存服务登记这个操作，宿主发送前分配 `operation_id=task-42:publish-v1`，服务按 ID 识别同一次操作。正常路径收到答复后结束；`lost_receipt` 则在登记后丢掉答复，让宿主改用查询。另有无法查询和错误换 ID 的两个对照。

三个词先认清：**操作 ID** 标记同一次操作；**回执** 是服务的答复；**对账** 是查询并核对服务结果。`accepted` 表示假服务已登记，`effects` 是登记次数。

这是可选的 Python 机制小实验。运行前请确认 Python 3.10+；不用第三方库，不联网、不发布内容，不调用真实 Agent。回执丢失用 `None` 模拟，没有实际计时器；两条练习独立，不需要上一课的文件。

## 先跑正常路径，再比较丢回执

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

先看 `normal` 的发送事件和回执，再看 `lost_receipt` 的查询事件：两次服务都登记 1 条，宿主只是用不同途径取得确认。`no_lookup` 则停在 `unknown_stop`，意思是“结果还不知道，需要其他方式核对”。

输出中的 `effects` 由教学模拟器直接读内部状态，供你对照。宿主只能依据自己收到的回执或查询结果行动。因此在 `no_lookup` 中，读者看见 1 条登记，宿主仍保持未知。

## 顺着代码看三个位置（可选）

打开 [`demo.py`](../../examples/remote-effect/demo.py)，找出下面三个位置：

1. `run()` 在发送前确定 `operation_id`。如果调用方每次重试都换一个 ID，服务就无法把它识别为同一次操作。
2. `FakeService.submit()` 先把操作写进自己的 `operations`，然后才决定是否返回回执。`None` 是**回执丢失**，不是副作用未发生。只有这个假服务明确保证同一 ID 去重；换成真实 API 时必须核对其幂等语义和有效期。
3. `run()` 在回执丢失后按 ID 查询；`no_lookup` 模式中，宿主已知道服务没有查询能力，直接记录 `unavailable` 并停止，没有真的调用 `lookup()` 再捕获异常。`unsafe_new_id` 是刻意写出的反例，不是推荐恢复方式。

真实系统的查询还可能暂时看不见记录，或原请求仍在途中。本实验先只处理“已找到”和“查询不可用”；带 HTTP 的下一课再观察读回滞后与迟到登记。

## 把发送、查询和重试连起来

先不看结果，预测 `lost_receipt` 和 `unsafe_new_id` 的副作用数。运行后对照：前者是 **1**，后者是 **2**。分别找出支持“请求已发出”“服务已接受”“又发起了另一操作”的事件：

| 要检查的步骤 | 对应事件 | 这一步记录了什么 |
| --- | --- | --- |
| 宿主调用发送接口 | `event=submit`，原操作 ID，`receipt=null` | 发送后未拿到回执。 |
| 宿主查到原登记 | `event=lookup, result=accepted` | 按原 ID 取得查询确认。 |
| 宿主发起另一次操作 | `event=unsafe_retry`，ID 以 `-retry` 结尾，`receipt=accepted` | 换 ID 建了另一条登记。 |

把 `lost_receipt` 与 `unsafe_new_id` 的事件排在两列：第一次回执同为 `null`，真正的差别在之后。前者按原 ID 查到结果后停止；后者还换了 ID，增加另一条登记。标出这个分岔点，就能说明登记次数怎样从 1 变为 2。

## 应用前还要核对什么

同 ID 去重由这个假服务明确实现。换真实 API 时，先查它的幂等规则、有效期和结果查询；服务既不能可靠查询，也不支持同 ID 安全重放时，就记录未知并交给人处理。界面、checkpoint 和提示词主要帮助交互与本地恢复，远端重复操作仍由服务规则决定。

本实验没有真正发布版本，也没测试部署健康、用户验收、最终一致性、ID 过期或迟到请求。接着可读[四系统恢复对照](../comparisons/permission-and-recovery.md)，或选择[HTTP 回执实验](http-receipt.md)。四套产品的实际部署表现需要各自测试。
