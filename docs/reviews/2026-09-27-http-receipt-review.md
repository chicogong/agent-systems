# 本地 HTTP 回执练习：独立代码审查

日期：2026-09-27。审查者未参与实现，仅写本记录，不修改示例、主稿、图或公共索引，不提交。先只读仓库协作约定、写作规则与旧 `remote-effect`；主代理明确通知新稿完成并授权后，逐行阅读 `examples/http-receipt/demo.py`、`test_demo.py`、README 与 `docs/labs/http-receipt.md`，独立运行测试、七种 CLI 和受限只读探针。

**最终状态：** 首轮 P2 已由主代理修复，同一错误路径探针复验通过；另一位冷读审查者提出的时序问题也已修订，本审查者最终重跑 **16 个测试、七种 CLI 和同进程清理探针**，通过。第二次超时回到 `unknown_stop`，确认冲突须有匹配原 ID 的 409；故障夹具在阻塞读响应前建立所需事件先后。以下保留各轮缺陷及返修证据，不把首轮 13 测试当作修订版本的结果。

## 首轮结论与发现

七条规定路径和现有 13 个测试通过；故障点、进程内幂等合同与事后观察者边界表达清楚。发现一项需要返修的 **P2**，不能只用主路径全绿宣布未知状态处理完整。

### P2：第二次 POST 超时被误报为内容冲突

首轮位置：`examples/http-receipt/demo.py:234`。

```python
status = "confirmed_replay" if accepted(result, OPERATION_ID, PAYLOAD) else "conflict_stop"
```

触发：`same_id_retry` 或 `payload_conflict` 的第二次 POST 没有获得答复，或得到不符合合同的其他响应。影响：任意非 accepted 结果都被报告为冲突，而冲突应该来自可信的 409 及对应操作 ID / `payload_conflict` 内容；没有回执只能保持未知。

只读探针在独立 Python 进程加载模块，把第二次 `request()` 的返回暂时替换成 `{"transport": "timeout", "http_status": None}`，其他请求仍走真实 loopback。两模式都输出 `conflict_stop`，`host.events[1]` 却没有 409。这是**内存中的错误路径注入**，不是声称制造了第二次真实网络超时；没有改代码文件。

最小修复：确认回执与确认冲突分别检查；只有 409、匹配 ID 和冲突状态才进入 `conflict_stop`；传输超时或不匹配回复进入 `unknown_stop`（也可在严格夹具中显式抛错，但不得凭空报告冲突）。补同 ID 重试第二次超时、错误操作 ID 的 409、其他 HTTP 错误或不匹配回执等回归测试。

## 首轮运行记录

环境：本机 Python **3.14.6**；仅绑定 `127.0.0.1` 动态端口，无外网业务请求，无凭据、生产账号或磁盘账本。运行命令：

```bash
python3 -m unittest discover -s examples/http-receipt -p 'test_*.py' -v
python3 examples/http-receipt/demo.py --mode <下表模式>
```

测试输出：`Ran 13 tests in 1.220s`、`OK`。七种 CLI 均能解析 JSON，stderr 为空：

| 模式 | 退出码 | 宿主结论 | HTTP 证据 | 事后登记数 |
| --- | --- | --- | --- | --- |
| normal | 0 | confirmed_receipt | POST 201 | 1 |
| timeout_then_lookup | 0 | confirmed_lookup | timeout → GET 200 | 1 |
| same_id_retry | 0 | confirmed_replay | timeout → 同 ID POST 200 | 1 |
| lookup_lag | 2 | unknown_stop | timeout → GET 404 | 1 |
| late_commit | 2 | unknown_stop | timeout → GET 404 | 1 |
| unsafe_new_id | 2 | duplicate_effect | timeout → GET 200 → 新 ID POST 201 | 2 |
| payload_conflict | 2 | conflict_stop | timeout → 同 ID、异内容 POST 409 | 1 |

`listener_closed` 是实现成功退出 context 后设置的报告字段，本身不独立证明端口关闭。端口关闭另由现有 `test_closed_even_when_caller_raises` 实际重新连接失败验证。额外真实 loopback 探针并发发送同 ID、异内容，两条请求得到 **201 与 409**，账本仅一条；竞争胜者取决于调度，本次为 v2，不能把此内容当固定胜者。额外连续运行 `late_commit`、`lookup_lag`、`timeout_then_lookup` 各三次，返回后相对基线没有新存活线程。

首轮快照 SHA-256：`demo.py` 为 `26ba1c60003d34cc42fd327648fd1694cb35fe2d4312e0c55ea90cd381b43ce4`，`test_demo.py` 为 `b1a5525240ed217e028bdfde65247d33a8782cd0cae60313ceb838e15da7bee1`，主稿为 `8cb2193c7c205451a641fc43a3c7e56dd8c8a6149c48352386086d8d69f076cc`。后续返修必须另记复验，不借首轮 13 个测试覆盖新增分支。

## 已核对的代码边界

- `Ledger.register()` 在同一把锁下检查 key / payload 与插入，重复登记返回 200、冲突不覆盖原值；这是当前内存进程合同，不是 POST、自定义 request ID 或 HTTP 标准自动保证。
- `lookup_lag` 首次读回隐藏已有记录，`late_commit` 在登记前停住原请求；两个 404 均保持 `unknown_stop`，不会按 404 自动换新 ID。宿主判断在释放迟到请求前冻结，事后 `observer_after_cleanup` 未覆盖原判断。
- `request()` 固定 loopback `HTTPConnection`，不接受 URL / proxy / host，也不跟重定向；超时路径关闭客户端连接。客户端关闭与服务端取消/回滚不同，late_commit 证明这一局部机制。
- 故障以线程事件控制先后；`received`、`committed` 的等待是夹具编排，不是远端客户端业务证据，正文已明说。真实的是 HTTP 请求、读等待和连接，非互联网随机丢包。
- `LabServer` 明确 non-daemon request threads、`block_on_close=True`，handler socket 有 5 秒上限；context 先 release gate，再从另一线程调用 shutdown、关闭服务器并等待 serve 线程。迟到 handler 可以先完成登记，清理不会被说成撤销业务。
- 输入长度、ID 与 payload 校验可拒绝现有非法输入；不据此将 `http.server` 教学夹具写成完整防攻击服务或沙箱。没有生产部署、认证、租户、持久事务、键到期、跨机器或灾难恢复保证。

## 第一方资料复核

重新打开 [Python http.server](https://docs.python.org/3/library/http.server.html)，核对其不推荐生产使用的明确警告；[socketserver ThreadingMixIn](https://docs.python.org/3/library/socketserver.html#socketserver.ThreadingMixIn) 核对 `server_close` 等待 non-daemon handler 与 `block_on_close` 行为，及 shutdown 须在不同于 serve_forever 的线程调用。没有将关闭监听误说为业务撤销。

RFC Editor 页面本轮浏览抓取失败，改读 [IETF 官方 RFC 9110 §9.2.2](https://datatracker.ietf.org/doc/html/rfc9110#section-9.2.2)。其幂等/非幂等重试规则支持正文“不把任意 POST 当安全重放”的表述；本例安全重放来源仍是具体账本实现。文件链接可用性与资料声明不替代本地运行证据。

## 未覆盖

本轮没有检验图、PDF、网站或移动端显示；不宣称整个 Python 3.10+ 矩阵已测试，仅运行本机版本。没有真实服务、数据库事务、网络分区、真实模型驱动或安全审计。半包、慢客户端、连接重置、磁盘损坏、进程崩溃和恶意并发的完整测试属于后续专门实验，不据正常夹具测试全绿推断通过。

## 返修与关闭

主代理通知修订完成后，独立重读 `demo.py:209–216` 的 `replay_status()` 和 `run()` 调用处。它先确认匹配 key / payload 的 accepted 回执，再确认 HTTP 409、`payload_conflict` 与相同 operation ID，其他结果保持 `unknown_stop`。新增两个单元测试覆盖重试超时、错误 ID 的冲突回执及 HTTP 500；正文也已更新为 15 个测试，并明确再次超时仍未知。

独立复跑得到 `Ran 15 tests in 1.221s`、`OK`；七种 CLI 的退出码、宿主结论及登记数与首轮主路径表相同，stderr 仍为空。同一只读内存探针重跑：

```text
same_id_retry  unknown_stop  retry_same_id: transport=timeout, http_status=None
payload_conflict  unknown_stop  retry_same_id: transport=timeout, http_status=None
```

该探针仍不是第二次真实网络超时的测量；它检查整条 run 调用链在既定错误结果下怎样冻结宿主判断，补足仅测试分类 helper 的覆盖。首轮 P2 据此关闭。本轮范围内未留下阻断性代码问题，后续内容/图/PDF 验收仍按上面的未覆盖项处理。

第一轮返修快照 SHA-256：`demo.py` 为 `d1ac497bf270aa8bdbbff18a39923cbcfa69106ec9620e7fd1c53f9f38986ba9`，`test_demo.py` 为 `af0b01f6e36d0e2a62a778c3b999373448a35d95fb520357042fea85d472a517`，正文为 `403df4cbbd9587fdd5b46af72c74f398f858156934284e8f303b062389374f50`。该轮 `git diff --check` 通过；这不是发布提交或全仓检查记录。

## 时序修订最终复验

问题由另一位冷读审查者提出：旧夹具在首个请求已经返回超时后才等待 `committed`，不能严格支持图示“先登记、后读超时”的先后关系。本审查者没有把它记为自己发现，也不以第一轮正常调度下的测试替代此次验证。

独立重读 `demo.py:186–199`、`run()` 的 `establish_fault()` 与新增慢登记测试。`fixture_before_read` 在发送请求后、调用 `getresponse()` 前等待夹具事件；非 `late_commit` 模式等待已收到且已登记，`late_commit` 仅等待收到，登记仍由后续释放闸门触发。未建立预期事件时抛异常；宿主分类仍仅查看 HTTP 回执或传输超时，不使用 `committed` 推定业务成功。这个本地同步钩子不是生产远端客户端能力，0.15 秒也不是整个请求含夹具等待的端到端期限。

最终独立运行：`Ran 16 tests in 1.642s`、`OK`。新增 `test_registration_precedes_read_timeout_even_if_processing_is_slow` 把登记处理延迟到 0.25 秒（超过 0.15 秒的 socket 超时），用单调时钟断言登记时间早于超时返回时间，并核对宿主为 `confirmed_lookup`。结合回调位于响应阻塞读取之前的代码证据，关闭此次夹具时序缺口；不据此推断真实远端服务也具有同样事件同步机制。

七种 CLI 各在独立子进程再次运行，JSON、退出码、结论和登记数均与首轮表相同，stderr 均为空。另在同一 Python 进程依次运行全部七种模式，context 返回后相对基线的新存活线程为 `[]`。这覆盖正常清理及指定故障夹具，不是恶意连接、进程崩溃或任意故障下的资源回收保证。本轮没有重复 PDF 或图像验收。

最终快照 SHA-256：

- `examples/http-receipt/demo.py`：`c732e223a5bfc31fe32a5c1d73d65a7193bdd42b2db9a47d2bdaba3d06e9f3ad`
- `examples/http-receipt/test_demo.py`：`bca7a6cae77a52ef6a10d10197845d3849c46af7ee4bd6c5bf5e5a2068d3f1e3`
- `docs/labs/http-receipt.md`：`e9f588753fb0054a57f2ccbda1eec0b3b768083191f504e72b677dbfa14a8cca`

本轮范围内未留阻断性问题；首轮 P2 的发现、修订和关闭记录仍保留，后续验收范围仍按“未覆盖”节执行。
