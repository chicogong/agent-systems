# DSH：执行次序与结果提交

[返回正文](../../docs/systems/dsh/README.md) · [图源](scene.excalidraw) · [SVG](diagram.svg) · [PNG](preview.png)

固定版本与源码依据见正文，不将版本元数据写进图内。此图是 `executeToolCalls` / `runGroup` 的教学投影，不是运行轨迹。

假设调用顺序为 A、B、C，执行允许并行且 B 较快。有界池可以让它先完成，但提交器会等 A ready 后按 A、B、C 连续提交结果。准备/审批与实际 dispatch 分开：要求 ask 而通道不存在时拒绝，该调用不会进入执行。这个拒绝分支是条件支路，不意味着所有工具都要求审批。

另一条虚线说明外部状态不受事件提交顺序保证：B 即使还没提交事件结果，仍可能先改变远端。有序日志不提供事务回滚。图未涵盖整个循环、所有插件、模式切换或取消细节；不表示安全审计或 MCP 画布与导出一致。

可在此目录运行 `python3 build.py` 重建原生图源；SVG 与 4× PNG 由同一固定 Excalidraw 原生导出器另行生成和实际检查。
