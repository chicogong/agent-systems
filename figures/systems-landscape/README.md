# 16 个开源系统选读地图：按工程问题对号入座

[返回系统索引](../../docs/systems/README.md) · [图源](scene.excalidraw) · [原尺寸 SVG（手机可放大）](diagram.svg) · [PNG](preview.png)

这张四象限地图把书中的 16 个开源项目按“各自最值得学的架构取舍”归为四组，帮助读者带着手头问题直接挑一个项目深读，而不必从头连读 16 套代码：

- **左上（01 循环内核与忙时控制）**：看一轮循环怎样组织、运行途中用户插话怎样安全接入——包含 `Pi`、`mini-SWE-agent`、`OpenCode`、`Kimi Code` 与 `DSH`。
- **右上（02 权限门禁、沙箱与交互界面）**：看高风险命令怎样审批隔离、网页界面怎样观测操作、工具太多怎样按需加载——包含 `Codex`、`OpenHands`、`Browser Use` 与 `Qwen Code`。
- **左下（03 长期记忆、压缩与知识沉淀）**：看长会话如何避免注意力稀释、跨任务经验如何写入和刷新——包含 `Letta Code`、`Hermes`、`Mem0` 与 `MiMo Code`。
- **右下（04 状态快照、常驻会话与多源编排）**：看状态图如何断点续跑、常驻服务如何管会话并发、多来源资料如何汇总——包含 `LangGraph`、`OpenClaw` 与 `GPT Researcher`。

## 生成与核验

`build.py` 生成原生 `scene.excalidraw`，再由 `excalidraw-agent` 原生导出 `diagram.svg` 与 4× `preview.png`。各项目的固定提交号与核对边界见对应章节及 `sources/systems.json`。
