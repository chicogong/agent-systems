# browser-use 一轮 step：文字版

[返回剖面](../../docs/systems/browser-use/README.md) · [图源](scene.excalidraw) · [SVG](diagram.svg) · [PNG](preview.png)

图从上往下读，四条泳道依次是 Agent、BrowserSession + Tools、模型、AgentHistory。Agent 请求浏览器状态；浏览器返回包含 DOM/URL/可用截图的 `BrowserStateSummary`；Agent 的消息管理器构造输入交给模型；模型返回动作列表；Agent 经 `multi_act`、`Tools.act` 在浏览器侧执行；`ActionResult` 回到 Agent；仅在有 `last_result` **且**状态摘要可用时，`_finalize` 才追加 `AgentHistory`。箭头是教学整理的主路径，不表示所有步骤都一定发生或异步组件只有一种实际调度顺序。

图旁明确区分三件事：采集状态时请求截图、根据 `use_vision` 决定是否送进模型、若状态中有截图则历史记录可单独保存。图片没有把“采集截图”误画成“模型一定看图”。源码定位、失败守卫和未验证边界见[章节](../../docs/systems/browser-use/README.md)及[代码导读](../../docs/systems/browser-use/code-walkthrough.md)。

固定官方源码：`browser-use/browser-use@d8110c5ff87ccba887aaa726cdb780f2f84bef8d`。本图为静态源码图，不是浏览器实测录屏。
