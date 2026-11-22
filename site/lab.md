# 交互式实验台 (Interactive Trace Labs)

本目录与组件维护《图解 Agent 系统》在线阅读器的 6 组交互式状态机回放预设（Trace Presets）。

## 6 组实验预设矩阵

| 序号 | 实验标识 (`id`) | 预设标题 | 对应机制章节 | 本地运行入口 |
| --- | --- | --- | --- | --- |
| 1 | `first-agent-loop` | 最小 Agent 循环：提案、批准与宿主验收门 | `/concepts/agent-loop` | `python3 examples/first-agent-loop/demo.py` |
| 2 | `context-budget` | 上下文预算与可见性：为什么「存了」不等于「看见了」 | `/concepts/context-vs-memory` | `python3 examples/context-budget/demo.py` |
| 3 | `evidence-contract` | 不可信观测与证据审计：为什么宿主不轻信输入正文 | `/concepts/observation-evaluation` | `python3 examples/evidence-contract/demo.py` |
| 4 | `remote-effect` | 远端副作用与丢失回执：重试还是先查账？ | `/comparisons/permission-and-recovery` | `python3 examples/remote-effect/demo.py` |
| 5 | `http-receipt` | HTTP 幂等回执与状态落盘：区分「操作已生效」与「收到成功响应」 | `/comparisons/completion-and-evidence` | `python3 examples/http-receipt/demo.py` |
| 6 | `prefix-cache` | KV 前缀缓存与缓存失效对比 (Prefix Cache Hit vs Bust) | `/concepts/cache-and-cost-economics` | `python3 examples/prefix-cache/demo.py` |

## 架构与数据流

1. **预设定义**：`site/scripts/trace-presets.mjs` 定义所有实验的模式、CLI 命令、裁定状态（tone/badge/summary）及单步输入输出快照。
2. **主题组件**：`site/.vitepress/theme/TracePlayer.vue` 在实验页与概念伴生页渲染单步状态机播放器，支持模式切换与快照查看。
3. **契约校验**：`site/scripts/test-trace-presets.mjs` 确保所有 6 个实验预设数据完整且路由解析确定。
