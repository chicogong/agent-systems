# HTTP 回执时序图：夹具校准与图稿复核

日期：2026-09-27。仅负责 `figures/http-receipt-timeline/` 原创教学图；不修改公共索引、正文或夹具代码，没有提交或推送。

## 最新收口：已校准本地夹具，不再是待定 API 草稿

首轮校准完整阅读了 `examples/http-receipt/demo.py`、测试文件及 `docs/labs/http-receipt.md`，当时 `demo.py` 的 SHA-256 为 `d1ac497bf270aa8bdbbff18a39923cbcfa69106ec9620e7fd1c53f9f38986ba9`，该值保留为历史。随后源码增加发送后、读回执前的本地故障闸门；本次重新静态核对该改动及新增慢登记测试，最新 `demo.py` SHA-256 为 `c732e223a5bfc31fe32a5c1d73d65a7193bdd42b2db9a47d2bdaba3d06e9f3ad`。主代理报告这版 16 个测试初跑通过，本图代理没有运行 HTTP 测试；先前源码核对、PNG 目视与本次静态复核都不算这版真实运行证据。

本次只追加夹具先后的文字边界并更新源码定位，主图语义未变，没有改图或重导：`request()` 先发送，再由仅本地的 `fixture_before_read` 等到 receive／register 事件，之后才开始 `getresponse()`。图中的先登记后读超时是夹具排出的受控轨迹，不是生产客户端可以读取服务事件或任意服务都会如此调度。`late_commit` 只等 receive；宿主业务决定仍只使用 HTTP 回包。新增测试用 0.25 秒慢登记覆盖这个先后，不将测试文件中的断言写成本代理已执行的结果。

| 图中陈述 | 当前代码核对范围 | 校准结果 |
| --- | --- | --- |
| POST 带原 ID 与内容，先登记再延迟回执 | `Handler.do_POST()` 101–137；`Ledger.register()` 42–56 | `POST /operations` 的 JSON 字段是 `operation_id` / `payload`；正常恢复故障先 register，再等 release。橙色等待条延续至查询完成以后，专指原 POST，不表示整个服务阻塞。 |
| 真正读超时后关闭原连接，但没有撤销登记 | `request()` 186–205；`run()` 229–247；`READ_TIMEOUT=0.15` | 请求发送之后、读响应之前由 fixture_before_read 等待内部事件；正常恢复等到登记，late_commit 只等 received。图标的是超时配置，而不是精确的整次请求墙钟耗时；关闭连接不取消原请求，内部事件也不是宿主业务证据。 |
| GET 使用同 ID、经 URL 编码，返回 accepted | `Handler.do_GET()` 139–150；`Ledger.lookup()` 58–66；`run()` 255–258 | 请求为 `GET /operations/<原ID经URL编码>`；HTTP 200，body.status 是 `accepted`，不是初版标签 found；还携带原 ID 和 payload。 |
| 宿主核对状态、原 ID、内容，才确认且不再 POST | `accepted()` 208–211；`run()` 255–258、269–272 | 回包的 HTTP 状态及三项内容都要匹配，才进入 `host.status="confirmed_lookup"`。不把 accepted 字符串单独当证明，也不把登记当部署成功。 |
| 清理只放行旧响应尝试，不保证送达 | `running_service()` 177–183；`reply()` 83–99；`do_POST()` 132–137 | 标“清理时才放行”，没有画保证送达的迟到回执箭头。另一 GET 由 `ThreadingHTTPServer` 并发处理，不必先释放原 POST。 |
| 404 不能证明没发生或不会后到 | `lookup()` 61–64；`do_POST()` 125–129；`run()` 258、269–272 | lookup_lag 和 late_commit 只作旁注边界；保留 unknown_stop、不换 ID 盲重试，图只展开 timeout_then_lookup。 |

校准后重新用同一个固定原生渲染器导出，并打开最终 PNG 检查。曾移除回包区域一条冗余标签，避免与 accepted 字样挤在一起；最终图未见穿字、裁切或箭头方向歧义。尺寸仍为 4,108 × 3,900；A4 单图几何估算最小 10.7 pt、621 PPI，无 scene／SVG 字号差异标记。这不是实际 PDF 页面或纸样验收。

当前最终文件 SHA-256：scene `0aa49cf694d4efb24c45897d0a2bdadbd9dc94747b1e543dacf8fffaf115eedd`；SVG `f558e23e44e410d8230825395bc074229545f9b6bef7d138085cbc40478d042b`；PNG `7f55121761e3d4eb9ca25de61cda63d8c6ec2790a0cc268d0cda2decd7863ba2`。下文初版哈希只保留为历史，不是当前发布物。

图源构建编译、本图本地链接与 whitespace 检查通过；不据此宣布 HTTP 代码、完整章节、网站或 PDF 已经独立验收。MCP 未目视的限定不变，不声称非 Excalifont 图源在交互画布中字形一致。源码再变或图源再改时，需要重新核对和重导。

## 设计范围

- 三泳道时序，而不是卡片分层：客户端 → HTTP 传输 → 服务，时间向下。
- 只画先登记、响应前等待、客户端 read timeout、同 ID 查询返回 HTTP 200／`status="accepted"` 的正常恢复路径。
- 等待没有画成已返回消息，accepted 没有画成业务成功；404 和迟到旧请求放旁注，不画为自动重试。
- 等价文字明确 `unknown_stop`、不换 ID 盲重试，以及登记前等待与读滞后由正文／夹具另讲。

## 初版草稿检查（历史）

初版时图源和文字版已成稿，但夹具尚未由主代理交付；以下保留当时的草稿检查，不代表上文校准后的当前字段或哈希，不把图稿检查写成 HTTP 实验验收：

- 使用仓库 `scripts/render_native_figures.py` 与 excalidraw-agent 的固定原生 `renderer.html` 导出 SVG 与 4× PNG；只复用静态模块缓存，没有换渲染引擎或手改 SVG。
- 实际打开 PNG 检查：三泳道、正反向消息、服务侧等待、客户端超时及旁注可区分，未见截断、穿字或边缘裁切。原图 4,108 × 3,900；600–700 px 缩略展示仍需打开原图或 SVG 阅读小字。
- 两次导出结果 SHA-256 一致：scene `cce722e2aa754251096c86989a996c57cb203a048a335550c6151582eea42437`；SVG `dcb5d10319a7afb1d3be1603e05883e5fa491177766be5ea98bfdcef46bc0fe9`；PNG `4218178d9fdec036d634b6f3712c42c663b302afbebdf7f36642d5f4962681dc`。
- 单图 A4 几何估算：约 168 × 159.5 mm、621 PPI、最小 10.7 pt，无 scene／SVG 最小字号差异标记。该估算不是实际 PDF 页或纸样验收。
- `build.py` 编译检查、此目录的本地链接和 `git diff --check` 无本图问题。并行夹具尚有正文待生成，不据仓库全局检查声称其已收口。
- MCP 接受了原生图源转换后的 payload；未实际目视交互画布，不声称其字体／字形与本地导出一致。检查点仅为运行态，不存入仓库。

初版待核对项现已按顶部最新收口核对。404 读滞后和原请求登记前等待／迟到仍是旁注边界，不自动升级为本代理的已测试分支。
