# Computer Use 与 Browser Use：在异步变化的屏幕上闭环操作

> Synthesized concept page maintained by Aimake LLM Wiki.

## Key Evidence & Provenance

### Source Snapshot (2026-11-22)
- **Origin**: `/Users/haorangong/Github/chicogong/experiments/agent-systems/docs/concepts/computer-and-browser-use.md`
- **SHA-256**: `0c9fd84c15610db2` · Raw: [[../raw/2026-11-22-computer-use-与-browser-use-在异步变化的屏幕上闭环操作.md|2026-11-22-computer-use-与-browser-use-在异步变化的屏幕上闭环操作.md]]
- 调用后端 API 就像按电灯开关：入参字段固定，成功失败一目了然。而让 Agent 直接操作电脑桌面或浏览器界面，则像在颠簸的车厢里穿针：模型刚看着上一秒的网页截图算出“保存草稿”按钮位于像素坐标 `(640, 420)`，鼠标还没落下去，页面异步弹出一张促销遮罩恰好盖在同一位置，或者表单校验重绘把下方按钮整体往下顶了 80 像素——原本安全的保存草稿，一脚
- 要在没有现成 API 的真实软件里稳妥干活，界面操作 Agent——包括横跨桌面应用与浏览器的 **Computer Use**，以及专注网页交互的 **Browser Use**（下文源码部分亦会剖析同名开源项目 `browser-use`）——必须打通四个核心工程环节：**用什么通道“看”清界面、怎样在异步跳变的页面上安全点按、为什么高危提交按钮前必须设
- 图的文字版 · 可编辑图源
- 如上图所示，无论底层走视觉截图还是结构化控件树，运行主干都遵循同一个感知—行动闭环：**采样当前界面 → 模型提议单步或小批动作 → 宿主校验权限与界面新鲜度 → 工具执行 → 重新采样验证结果**。Anthropic 的 Computer Use 文档同样以此循环作为标准控制模型。
- 让模型理解当前屏幕上有什么，业界演化出了四条技术路线，各自在通用性、Token 成本与定位精度上有着鲜明取舍：
