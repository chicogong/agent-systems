# 图稿约定

每张正式图放在独立目录：`scene.excalidraw` 是可编辑源文件，`diagram.svg` 用于 Markdown，`preview.png` 用于预览，`README.md` 给出文字说明、主张、来源和核验状态。

使用 [excalidraw-agent](https://github.com/chicogong/excalidraw-agent) 绘制和导出。发布前目视检查文字、箭头、边界、留白与移动端可读性。MCP 画布的成功返回只证明已接收，不证明与本地导出视觉一致；需要交互展示时还要检查实际画布。

字体、图形语义和导出验收见[设计原则](STYLE.md)。Pi 图采用 Normal 标题和 Code 节点；其他章节应按问题选择最清楚的形式。MCP 交互画布可能强制替换字体，因此仓库 SVG/PNG 才是对外展示的视觉基准。

概念图可以表达通用模型，但须说明它不是某个项目的内部结构。实现图只标固定源码版本中能核对的组件和路径。

## 图集

- 机制：[五层职责](agent-stack/README.md) · [Agent loop](agent-loop/README.md) · [工作流与多执行者](agent-workflow-multiagent/README.md) · [委派交接](delegation-and-handoff/README.md) · [上下文与记忆](context-vs-memory/README.md) · [中断与恢复](interruption-recovery/README.md) · [观察与评测](observation-evaluation/README.md)
- 运行与执行：[Pi 分层](pi-architecture/README.md) · [Pi 扩展](pi-extensions/README.md) · [Codex 审批](codex-exec-approval/README.md) · [OpenCode 状态](opencode-tool-state/README.md) · [mini-SWE-agent 消息](mini-swe-loop/README.md) · [Qwen Code 延迟工具](qwen-code-deferred-tools/README.md) · [OpenHands 事件](openhands-action-events/README.md) · [Browser Use 泳道](browser-use-step/README.md) · [Kimi Code 忙时输入](kimi-code/README.md) · [MiMo Code 窗口接力](mimo-code/README.md)
- 状态与材料：[Letta Code 记忆](letta-memory/README.md) · [Mem0 检索](mem0-retrieval/README.md) · [LangGraph checkpoint](langgraph-checkpoints/README.md) · [OpenClaw 会话](openclaw-session-gates/README.md) · [GPT Researcher 证据](gpt-researcher-evidence/README.md)
- 横向对照：[四种循环与停止契约](loop-and-stop/README.md) · [Claude Code 与 Codex 的命令关口](claude-code-codex/README.md) · [权限、未知结果与恢复](permission-and-recovery/README.md)

## 视觉校稿进度

逐张验收应从当前 `scene.excalidraw` 重导 SVG/PNG，复核图片、文字版和正文箭头语义；有 `build.py` 的图还需检查生成脚本的确定性。不能把某次检查的图数与结论沿用到新图。MCP 画布、手机视图、A4 实页和外部读者试读各是独立验收项。

印刷清晰度不能只看独立 PNG 的像素数：原图缩进 A4 正文宽度后，小字号注释仍可能难读。每次改图还要检查成书 PDF 的实际含图页；关键节点文字以约 8 pt 作为人工复核提醒线，过长的技术说明移到图下正文。密集图不能靠持续加大 PNG 像素“修复”。

图稿的可读性分开记录：源图字号、A4 中的估算字高、实际 PDF 页、手机上的原尺寸放大入口。当前旧图已按 A4 几何预检返修；**几何数字合格不等于 PDF 实页、打印样张或读者理解通过**。每张图独立决定是否需要标题、分区或注释，不做全库机械换色。
