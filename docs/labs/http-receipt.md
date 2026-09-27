# 动手：真的 HTTP 超时，结果还能判断吗？

[返回学习路线](../learning-path.md) · [先读内存版回执练习](remote-effect.md) · [权限与恢复对照](../comparisons/permission-and-recovery.md)

你已经用内存模拟器区分“没有回执”和“没有执行”。现在做下一步：客户端真的向 `127.0.0.1` 上的服务发 HTTP 请求，真的等待响应并发生读超时，再用另一条 HTTP 连接对账。读完应能说明：**超时、查询 404、同 ID 重放、换 ID 再做一次，分别提供什么证据。**

这不是云端 API 或模型驱动的 Agent。服务的业务只是把一个版本标签登记在进程内账本，故障由教学程序安排；真实发生的是本地 TCP/HTTP、并发请求和读超时，不是真正发布版本、互联网丢包或内核隔离。前置条件为 Python 3.10+、允许本机 loopback 监听，以及前一条练习的操作 ID 与对账概念。只用标准库，不需要账号。

## 先跑一条能解释的轨迹

从仓库或解压后的阅读包根目录运行：

```bash
python3 examples/http-receipt/demo.py --mode timeout_then_lookup
python3 -m unittest discover -s examples/http-receipt -p 'test_*.py'
```

程序临时绑定 `127.0.0.1` 的动态端口，不接受任意远端地址，不跟随重定向；每次运行结束释放故障闸门、等待服务线程退出并关闭监听，不写磁盘或访问真实账号。不要把服务绑定改成 `0.0.0.0`；Python 官方也说明 [`http.server` 不适合生产服务](https://docs.python.org/3/library/http.server.html)。

刚才指定的 `timeout_then_lookup` 结果应是：`host.status=confirmed_lookup`，第一次 `submit` 有 `transport=timeout`、`http_status=null`，随后 `lookup` 收到 HTTP 200，正文包含原操作 ID 和 `payload=publish-v1`。事后观察者看到 `registered_effects=1`。省略 `--mode` 时程序默认运行 `normal`，不是这条故障路径。字段读法如下：

| 输出位置 | 谁取得的信息 | 能说明什么 |
| --- | --- | --- |
| `host.events` | 客户端取得的 HTTP 回执或超时 | 宿主用来决定继续、确认或保持未知的证据 |
| `host.status` | 宿主依据上面的证据做的判断 | 只对本练习的登记合同负责，不验收真实版本发布质量 |
| `observer_after_cleanup` | 教学观察者在清理后读取服务内部账本 | 给读者比较事实与宿主认知，不能倒推宿主超时时已知道什么 |

![服务先登记，客户端超时后用另一条连接按原 ID 对账](../../figures/http-receipt-timeline/diagram.svg)

[图源](../../figures/http-receipt-timeline/scene.excalidraw) · [PNG 预览](../../figures/http-receipt-timeline/preview.png) · [不看图的说明](../../figures/http-receipt-timeline/README.md)

这张图只画 `timeout_then_lookup`：`POST /operations` 携带 `operation_id` 和 `payload`；服务先登记，却在回响应前等待；客户端读超时关闭原连接，再经另一条连接 `GET /operations/<原ID>`，匹配 200 回执后确认登记，不发起第二次写入。响应尝试可能发生在客户端已关闭之后，不画成客户端一定收到了那份迟到回执。后面两种 404 的含义不同，不塞进主路径。

## 先预测，再比较七种情况

先选 `normal`、已跑过的 `timeout_then_lookup`、`same_id_retry`，回答每次会登记几条；再看 `lookup_lag` 和 `late_commit` 的两种 404。最后两条是反例和冲突，不是推荐恢复策略。

```bash
python3 examples/http-receipt/demo.py --mode normal
python3 examples/http-receipt/demo.py --mode same_id_retry
python3 examples/http-receipt/demo.py --mode lookup_lag
python3 examples/http-receipt/demo.py --mode late_commit
python3 examples/http-receipt/demo.py --mode unsafe_new_id
python3 examples/http-receipt/demo.py --mode payload_conflict
```

| 模式 | 客户端在决策时看见 | 宿主结论 | 清理后的登记数 |
| --- | --- | --- | --- |
| `normal` | POST 201，ID 与内容匹配 | `confirmed_receipt` | 1 |
| `timeout_then_lookup` | 读超时；原 ID 的 GET 200 | `confirmed_lookup` | 1 |
| `same_id_retry` | 读超时；同 ID、同内容再次 POST 得 200、`replayed=true` | `confirmed_replay` | 1 |
| `lookup_lag` | 读超时；第一次 GET 404 | `unknown_stop` | 1；其实已登记，只是故意隐藏一次读回 |
| `late_commit` | 读超时；GET 404 | `unknown_stop` | 1；原请求在宿主停止判断之后才获准登记 |
| `unsafe_new_id` | 读超时；查询已确认，却仍用新 ID POST | `duplicate_effect` | 2 |
| `payload_conflict` | 读超时；同 ID 换内容 POST 得 409 | `conflict_stop` | 1；原内容没有被替换 |

前三种确认路径退出码为 **0**；后四种为 **2**，表示未确认、冲突或刻意的错误恢复，不等于“服务未登记”。看到终端返回 2，仍要读 JSON。测试命令应通过 **16 个测试**；测试通过不改变某个场景应当保持未知的结论。同 ID 重放若再次超时，也保持未知；只有匹配原 ID 的真实 409 冲突回执才标记 `conflict_stop`。

两种 404 的返回结构相同。`lookup_lag` 已有记录，却故意让第一次查询看不见；`late_commit` 查询时尚未登记，旧请求还在处理，清理阶段释放闸门后才登记。**即使某次查询是真实的当前状态，也不能证明旧请求以后不会继续生效。** 宿主在这两个例子里都只报告 `unknown_stop`，不靠事后读者视角改成成功，也不把原连接关闭当作取消或回滚。

## 同 ID 重放靠什么，不靠什么

操作 ID 是本服务 JSON 请求中的应用字段，不是标准 HTTP 自带的幂等承诺。这里只保证在**同一个服务进程、同一账本**内：同 ID 和同 payload 重放返回原登记；同 ID 不同 payload 返回 409；核对与新增在同一把锁下完成，避免两个线程同时查无记录后各写一次。

这就是为什么 `same_id_retry` 可以确认，而 `unsafe_new_id` 会多登记一次。将 request ID 打进日志、给请求加一个自定义字段，或在模型提示中写“不要重复”，都没有实现这套服务端合同。HTTP 标准关于[幂等与重试的说明](https://www.rfc-editor.org/rfc/rfc9110.html#section-9.2.2)也没有让任意 POST 自动变成安全重试；本练习是应用明确实现了较窄的重放语义。

不要把这套实现称为分布式“恰好一次”：账本不持久化，进程退出就丢；没有键的有效期、租户作用域、业务事务、跨机器协调或灾难恢复。登记成功也不意味着外部部署完成。真正接 API 前，还要核对同键内容、键保留时间、可信终态查询、是否能取消、重试策略与业务验收。

## 沿五个位置读代码

打开 [`demo.py`](../../examples/http-receipt/demo.py)，不必逐行背网络 API：

1. `running_service()` 启动 loopback 服务，并在 `finally` 中先释放闸门，再 `shutdown()`、`server_close()` 和等待线程。清理是收尾，不是撤销业务；`late_commit` 正是先让原请求完成收尾，再给观察者读账本。
2. `Handler.do_POST()` 收到并验证请求。`late_commit` 在登记前等闸门；其余故障在 `Ledger.register()` 之后、响应之前等。故障点放在哪，决定超时后账本已经发生了什么。
3. `Ledger.register()` 在锁内核对 ID 与内容。重复返回原登记，冲突不写，不让两条并发请求分别绕过去重。
4. `request()` 使用 [`HTTPConnection` 的超时与响应读取](https://docs.python.org/3/library/http.client.html)。它遇到 `socket.timeout` 输出传输超时，不凭此写“业务失败”。初次故障请求在发送后、开始阻塞读响应前，额外运行本地 `fixture_before_read` 回调：按所选模式等待“已登记”或“已收到但暂不登记”的事件，固定教学先后关系；之后仍是真的 socket 读超时。这个回调不是生产客户端能力，远端客户端不能据此读取服务内部事件。
5. `run()` 只按 HTTP 回执决定 `host.status`：确认时核对状态码、ID 和内容，不只看 `accepted`。内部同步仅安排故障；未建立预期夹具会抛异常，不能算完成。账本仅在独立的事后观察中出现，不是宿主的业务证据。慢登记测试延迟 0.25 秒，确认登记早于读超时。

## 改一处，然后证明结论

先预测这三个问题，再运行测试或对照代码：

- `same_id_retry` 的第二次内容改成 `publish-v2`，应发生什么？答案是 409、`conflict_stop`，原 `publish-v1` 留在账本；现成的 `payload_conflict` 已覆盖这个修改，不必真改文件。
- 如果两条并发 POST 使用同 ID、同内容，会有几次登记？`test_atomic_parallel_deduplication` 发四个真实请求，断言一个 201、三个 200 和一条登记。这个结果只验证当前进程内的锁和合同。
- 把第一次查询 404 当成失败并生成新 ID，为什么危险？`lookup_lag` 的原记录已经存在，`late_commit` 的旧请求还会后到；新的 ID 都会绕过原键去重。安全的下一步取决于可信查询和服务合同，不是由模型把“未知”改写成“失败”。

下一步再把内存账本换成专用临时持久存储，并测试进程重启、冲突和读回；那是新的实验与证据，不属于本章已验证范围。学习目标不是背七个模式，而是在超时后分别写清楚：**我发出了什么、我收到了什么、服务合同保证什么、我还不知道什么。**
