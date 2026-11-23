# browser-use：把杂乱动态网页压成可索引的单步闭环

> Synthesized concept page maintained by Aimake LLM Wiki.

## Key Evidence & Provenance

### Source Snapshot (2026-11-22)
- **Origin**: `/Users/haorangong/Github/chicogong/experiments/agent-systems/docs/systems/browser-use/README.md`
- **SHA-256**: `95c7066b56c47d52` · Raw: [[../raw/2026-11-22-browser-use-把杂乱动态网页压成可索引的单步闭环.md|2026-11-22-browser-use-把杂乱动态网页压成可索引的单步闭环.md]]
- 如果你试过直接把现代电商或后台系统的原始 HTML 塞给大模型，马上就会撞上两场灾难：一页动辄五万 token 的嵌套 `<div>` 和脚本瞬间灌满上下文窗口；更糟的是，就算模型好不容易猜出一个 CSS 选择器，半秒后弹窗动画或路由跳转一发生，后续点击就会结结实实点错按钮。
- `browser-use` 的核心价值，就是用 `Agent.step()` 把充满噪声、随时跳变的真实浏览器，驯服成一个「**提取可交互索引 → 模型输出结构化动作序列 → 浏览器带熔断执行 → 归档因果历史**」的紧凑单步闭环。
- 文字版 · 可编辑图源 · 关键代码导读
- 每一轮 `step()` 开始时，`BrowserSession` 不会把整棵原始 DOM 树倒给模型，而是提炼出一份带数字编号的可交互元素摘要（连同标签页、URL 与页面截图），再由消息管理器（`MessageManager`）拼上「上一步动作的执行反馈」，组装成定长可控的当前轮输入。这样历史轮次的庞大网页快照不会在上下文里无限堆积。一轮工作 · 保存这一
- 多模态截图是最昂贵的上下文消耗源之一，`browser-use` 把「采集截图」「送给模型」和「写入历史」拆成了三个独立开关：
