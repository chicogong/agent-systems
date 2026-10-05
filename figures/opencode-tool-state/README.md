# OpenCode 工具调用状态机：文字版

[返回 OpenCode 讲解](../../docs/systems/opencode/README.md) · [图源](scene.excalidraw) · [SVG](diagram.svg) · [PNG](preview.png)

看一次读取文件的工具调用，从图上方的 `pending` 往下跟。`ToolPart` 是这次调用的进度记录，`callID` 是它的编号；输入和结果都靠这个编号找到同一条记录。

| 图中状态 | 程序正在记录什么 |
| --- | --- |
| `pending`：接收输入 | `tool-input-*` 表示输入开始、陆续到达或结束。`ensureToolCall` 创建或复用调用记录。 |
| `running`：等待结果 | 完整的 `tool-call` 到达，程序写入参数和开始时间。 |
| `completed`：成功结束 | 找到对应的运行中记录后，成功的 `tool-result` 写入输出和结束时间。 |
| `error`：报错或中断 | 找到对应的运行中记录后，错误结果或 `tool-error` 写入错误。 |

每次变更都通过会话服务更新这条记录。`completed` 和 `error` 是两种结束结果；箭头分别指向它们。

右侧虚线是结束清理：仍没完成的 `pending` 可以直接进入 `error`，尚未完成的 `running` 也能被标为错误，并记上 `interrupted: true`（已中断）。所以，看见 `error` 时，要读具体原因：工具报错和清理时中断是两条来路。结果事件也只有找到对应的 `running` 记录时，才会更新它。

**图底部说的是整个会话。** `SessionStatus` 发布的 `busy / retry / idle` 分别表示忙碌、重试和空闲；单次调用的成功或失败看上面的 `ToolPart`。外层模型流出错时，`SessionRetry.policy` 判断能否重试、是否超过次数上限；允许重试才发布 `retry`，带上次数和下次尝试时间。单个工具报错先写进自己的记录，这件事本身不会自动让会话进入 `retry`。

工具真正执行时，插件前置处理 `tool.execute.before`、工具 `item.execute`、插件后置处理 `tool.execute.after` 依次协作。这条调用流程与图里的进度状态分别阅读。[函数位置](../../docs/systems/opencode/code-walkthrough.md) · [重试策略源码](https://github.com/anomalyco/opencode/blob/18ef3cc7c5a25b82114c953a80ccc09f4988f74e/packages/opencode/src/session/retry.ts#L178-L209)

本图依据固定源码 `18ef3cc7c5a25b82114c953a80ccc09f4988f74e`，用状态变化说明一条记录怎样从输入走到结果。尚未运行真实请求；不同模型服务（provider）、中断恢复和文件保存故障需要另做检查。
