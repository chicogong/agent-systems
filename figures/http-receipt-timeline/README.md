# HTTP 回执时序：同一个 ID 找回记录

[SVG](diagram.svg) · [4× PNG](preview.png) · [可编辑图源](scene.excalidraw)

服务已经登记了一条记录，客户端却没等到回执。这张图跟着本书的[本地 HTTP 演示程序](../../examples/http-receipt/demo.py)，展示怎样用原编号把记录找回来；详细操作见[练习正文](../../docs/labs/http-receipt.md)。

## 不看图的说明

三列从左到右是客户端、HTTP 传输、服务，时间从上往下。先看“发送 → 登记 → 等待超时 → 查询 → 找回”这条主线。

1. **发送登记请求。** 客户端用 `POST /operations` 发送 JSON，里面有操作编号 `operation_id` 和待登记内容 `payload`。
2. **服务保存记录。** `Ledger.register()` 按这个编号登记原内容。
3. **让回执晚一点返回。** 演示程序让原 POST 等待 `release` 事件。橙色等待条画的就是这段等待；与此同时，服务的另一线程仍能处理查询 GET。
4. **客户端等到超时。** `http.client` 的读取超时设置为 0.15 秒。等待响应时发生读取超时（read timeout），随后在 `finally` 里关闭原连接。这时登记已完成，关闭连接也没有撤销它。
5. **用原编号查询。** 宿主另开连接，访问 `GET /operations/<原ID经URL编码>`；代码中的 `quote(operation_id, safe="")` 负责把编号放进 URL。
6. **取得记录。** 这条路径返回 HTTP 200，JSON 包含 `status="accepted"`、原编号和原内容。accepted 是本程序约定的字段，表示已登记；接口实际没有返回 found 这个字面值。
7. **核对后结束。** `accepted()` 检查 HTTP 状态、JSON 状态、编号和内容，都匹配时，`run()` 才写入 `host.status="confirmed_lookup"`。找到的是原记录，无需再发一次登记请求。

## 查询仍不清楚时

另一条路径可能返回 `404 not_found`：记录暂时查不到。它可能尚未登记，也可能已经保存但查询还看不到，还可能有旧请求正在路上。因此，这时保留原编号，进入 `unknown_stop`，也就是暂停并说明结果未知。登记前等待、延迟可见等情况，在程序和练习中分别演示。

本图确认的是这条记录是否已登记。真实业务还需按自己的要求检查，例如记录登记之后是否完成后续处理。

## 代码怎样安排时间（选读）

为了稳定演示超时，`request()` 在发送后、调用 `getresponse()` 前，先运行测试用的 `fixture_before_read`。主路径等待服务发出 `received` 和 `committed` 事件，保证已经收到并登记，再开始等待回执；因此即使登记本身慢于 0.15 秒，仍能得到图中的先后次序。`late_commit` 模式只等 received，随后再展示登记延后的情况。

这些事件只用于本地演示安排时间。宿主判断记录是否存在，仍依据查询返回的 HTTP 状态和内容。真实客户端通常拿不到服务内部事件，要按实际接口检查。

最后清理时，程序释放 `release`，服务才尝试返回旧 POST 的回执。原连接已经关闭，是否送达无法确认，所以图上只画了等待，没有画保证送达的迟到回执。

## 构建与校准

`build.py` 生成原生 Excalidraw 图源。运行实验使用的是演示程序，构建图源只负责画图。文字使用 Normal 6，标识与返回字段使用 Code 8；框线和箭头保留轻手绘风格。

从 `scene.excalidraw` 用仓库 `scripts/render_native_figures.py` 导出 SVG 和 4× PNG。脚本使用固定原生渲染器，并缓存它所需的 jsDelivr 静态资源。导出后检查三列、箭头、汉字和裁切；MCP 画布可能切换字体，显示效果另行检查。

本图按照本地演示的路由、字段与事件顺序校准。`ThreadingHTTPServer` 支持原 POST 等待时另一个连接处理 GET；其他服务的并发和状态规则需分别核对。导出与源码校准记录见 [HTTP 图稿复核](../../docs/reviews/2026-09-27-http-figure-review.md)，实际实验结果另看运行记录。
