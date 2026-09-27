# HTTP 回执时序：同一个 ID 找回记录

[SVG](diagram.svg) · [4× PNG](preview.png) · [可编辑图源](scene.excalidraw)

状态：已按本仓库[本地 HTTP 夹具源码](../../examples/http-receipt/demo.py)与[教材正文](../../docs/labs/http-receipt.md)校准的教学图。图不是上游系统的源码图；图稿作者本轮做了源码核对与导出目视，没有自行运行 HTTP 测试，不把图当实验记录。

## 不看图的说明

三条泳道从左到右是客户端、HTTP 传输、服务；时间从上向下。主路径只讲一件事：**服务已经按稳定 ID 登记，客户端却因等待回执超时，随后查询同一个 ID 找回记录。**

1. 客户端 `POST /operations`，JSON 含稳定的 `operation_id` 与 `payload`，传输层送达服务。
2. 服务先通过 `Ledger.register()` 按该 ID 登记原内容。
3. 服务在 `release` 事件上等待，再尝试返回原 POST 的响应。图中的橙色等待条专指原 POST，请求仍在等待时另一服务线程可处理 GET；不是整个服务禁止处理新请求，也不是已经送达客户端的响应。
4. 客户端使用 `http.client` 的 0.15 秒超时，在等待回执时发生 read timeout，并在 `finally` 中关闭原连接；这不能证明服务没有登记，也没有取消原请求。
5. 宿主用另一条连接 `GET /operations/<原ID经URL编码>`，代码使用 `quote(operation_id, safe="")`；不生成新的 ID，也不盲目再执行一次。
6. 本条正常恢复路径收到 HTTP 200，JSON 的 `status="accepted"`，还含原 `operation_id` 与 `payload`。图中的 accepted 是应用字段，不是 HTTP 自带的业务保证；实际 API 不返回字面值 found。
7. `accepted()` 同时核对 HTTP 状态码、body.status、原 ID 与内容，`run()` 才设置 `host.status="confirmed_lookup"`，不发起第二次 POST。这里确认的是本练习的登记合同，不是任意业务已完成或业务结果已验收。

上述先后是**本地故障夹具安排出的轨迹**：`request()` 发送请求后、进入 `getresponse()` 之前调用仅供夹具的 `fixture_before_read`；正常恢复故障等 `received` 与 `committed` 事件，确保先登记再开始等待响应，即使登记处理慢于 0.15 秒的超时配置。`late_commit` 只等 received，不等登记。这些服务内部事件不是生产客户端可取得的远端证据，不能把它们当作宿主确认业务的理由；宿主确认仍只核对 HTTP 回包。图省略这条夹具控制通道，不把受控次序推广成任意 API 的保证。

最后清理时会释放 `release` 闸门，服务才尝试那份旧 POST 回执；客户端已关闭原连接，不能据尝试写回证明回执送达。为避免误读，图不补画一条保证送达的迟到响应箭头。

另一种查询可能返回 `404 not_found`。这既不能证明旧操作没有发生，也不能证明尚在途的旧请求以后不会登记；读取还可能被人为延迟可见。不能把 404 当作换 ID 重试的许可证，无法确认时应进入 `unknown_stop`。为保持图的主要问题清晰，这条不确定路径只写旁注，登记前等待／放行旧请求的分支由夹具及正文另讲。

## 构建与校准

`build.py` 只生成原生 Excalidraw scene，不发 HTTP 请求。正文使用 Normal 6，标识与回包使用 Code 8；2 px 轻手绘框线、3 px 主箭头、细虚线 lifeline。颜色辅助角色与状态，不代替箭头方向和文字。

从本目录的 `scene.excalidraw` 用仓库 `scripts/render_native_figures.py` 导出 SVG 和 4× PNG。该脚本缓存的是固定原生渲染器所需的 jsDelivr 静态资源，不是另外拼装 SVG。导出后须打开 PNG 检查泳道、箭头、汉字回退、裁切与缩排可读性。MCP 字体可能强制切换到 Excalifont，不能承诺与本地 SVG／PNG 字形一致。

本轮已核对：实际路由与 JSON 字段、登记／等待／超时／查询的事件次序、accepted 与宿主确认的含义，以及 404 与未知停止的范围。`ThreadingHTTPServer` 允许原 POST 等待时另一连接处理 GET；它不是串行服务保证。不把图稿校准升级为上游安全审计、生产 API 证据或本代理的运行结果；导出和校准范围见 [HTTP 图稿复核](../../docs/reviews/2026-09-27-http-figure-review.md)。
