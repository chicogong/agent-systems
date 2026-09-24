# 图的文字版：中断后先对账

[返回章节](../../docs/concepts/interruption-recovery.md) · [可编辑图源](scene.excalidraw) · [SVG](diagram.svg) · [PNG](preview.png)

这是一张**教学决策图**，不是某一产品的内部架构或保证。它用创建工单说明：Agent 先记录动作意图和业务键 K，再经工具发送创建请求。请求一旦越过本地进程边界，即使本地随后超时、取消或断线，外部系统也可能已经创建工单。

蓝色“发送创建请求”经紫色箭头跨过竖向虚线标出的**副作用边界**，进入外部系统的紫色节点。外部动作可能已生效，但响应未抵达；橙色“结果未知”因此进入“按 K / 请求 ID 对账”。查询后分三路：确认已创建，复用已有工单 ID；确认未创建且接口合同允许，进入有次数上限的重试；仍未知，暂停交给人对账。安全重试的蓝色回路从重试节点**返回原创建请求**，只在 `n < N` 时沿用同一 K；达到上限的橙色箭头转向人工对账。左侧无边框的 checkpoint 文字是没有流程箭头的旁注：它只恢复图状态，不撤销外部动作。

箭头表示推荐的判断顺序，**不表示**查询一定可用、人工能立即判明真相，或业务键自动使接口幂等。蓝色是 Agent 侧的动作与有条件回路，紫色是外部副作用边界，橙色是未知/人工确认，绿色是已确认的既有结果；文字标签给出同样的信息。`N` 是预设的有限重试上限，并非某框架固定参数。

图的依据分两层：Pi 的固定提交 [`898ab804050730e9dcefb4443875d5a932aa6a32`](https://github.com/earendil-works/pi/tree/898ab804050730e9dcefb4443875d5a932aa6a32) 展示取消信号及 coding-agent 的模型错误重试；LangGraph 的固定提交 [`bdb85b5aa87a21de68371d2e534b81aeed398f57`](https://github.com/langchain-ai/langgraph/tree/bdb85b5aa87a21de68371d2e534b81aeed398f57) 展示 checkpoint 选择/分叉。查询工单、K 的设计和人工对账是章节中的**工程建议**，不是对任一项目现成功能的声明。源码定位、适用范围和未验证项见[章节](../../docs/concepts/interruption-recovery.md)。

运行 `python3 figures/interruption-recovery/build.py` 可重新生成原生 `.excalidraw`。用 `excalidraw-agent` 的固定渲染器从该图源导出 SVG 和 PNG；重新生成时须重查文本布局与裁切。
