# browser-use 一轮 step：文字版

[返回讲解](../../docs/systems/browser-use/README.md) · [图源](scene.excalidraw) · [SVG](diagram.svg) · [PNG](preview.png)

网页助手找资料时，要先看页面，再决定点击、输入或滚动，最后记下结果。图从上往下讲一轮 `step`（工作步骤）；四列是 Agent、浏览器与工具 `BrowserSession + Tools`、模型，以及历史记录 `AgentHistory`。

沿箭头看一次正常过程：

1. Agent 请求网页状态。浏览器返回 `BrowserStateSummary`（状态摘要），包括网页结构 DOM、页面地址 URL 和可用截图。
2. 消息管理器用 `create_state_messages` 整理模型输入。模型收到后，返回 `AgentOutput.action`，也就是准备执行的动作列表。
3. `multi_act` 逐项安排动作，`Tools.act` 找到实际工具，在浏览器中执行；工具把 `ActionResult`（动作结果）交回 Agent。
4. `_finalize` 整理本轮记录。**同时有动作结果 `last_result` 和网页摘要时**，才追加 `AgentHistory`。它保存本轮执行前看到的页面和随后得到的结果；下一轮再看新页面。

图旁的截图提示说的是三个不同动作。请求状态时，`include_screenshot=True` 要求采集截图。摘要中确实有截图时，`use_vision=True` 会把图交给模型，`False` 会省略它，`"auto"` 只在动作结果要求截图时交给模型。历史记录另行保存可用截图的路径。想知道模型当时看到了什么，要同时查看截图是否取得和 `use_vision` 设置。

动作序列也有停止条件：出错、任务结束标记 `is_done`、动作要求停止，或页面地址／焦点目标变化时，程序会停下余下动作。超时或异常也可能影响状态获取与记录。具体函数和处理位置见[章节](../../docs/systems/browser-use/README.md)及[可选代码导读](../../docs/systems/browser-use/code-walkthrough.md)。

本图依据固定官方源码 `browser-use/browser-use@d8110c5ff87ccba887aaa726cdb780f2f84bef8d` 整理主流程，尚未用真实浏览器记录核对异步事件的实际时间顺序。
