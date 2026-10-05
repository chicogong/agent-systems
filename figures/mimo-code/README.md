# MiMo Code checkpoint 与重建图的文字版

[返回章节](../../docs/systems/mimo-code/README.md) · [可编辑图源](scene.excalidraw) · [SVG](diagram.svg) · [PNG](preview.png)

长任务快用满模型能接收的材料时，MiMo Code 用交接笔记准备下一轮。图分上下两段：上面提前整理笔记，下面需要换窗口时再使用笔记。两段各有自己的触发条件。

**① 提前记笔记：主 Agent 继续工作，writer 在后台整理。** token 是模型计算材料长度的单位。已完成回复的 token 用量跨过设定阈值时，程序安排 writer（笔记整理助手），让它在独立的 child session（子会话）中读取截至指定消息位置的历史，更新主会话的 `checkpoint.md`，必要时再维护项目 `MEMORY.md`。

图中的“交接笔记”就是按固定栏目整理的文件。writer 成功后，程序才推进 watermark（已确认整理到哪条消息的位置标记），对应图中的“成功后更新位置”。主 Agent 的日常步骤可以继续，无须每步都等待整理助手。

**② 窗口装不下时：检查笔记，再准备下一轮输入。** 上下文窗口是模型一次能接收的材料容量；overflow（溢出）指材料装不下了。图中这段流程要求 checkpoint 与 memory write（记忆写入）均已启用：

- **已有可用笔记：** 程序插入“重建边界”，即下一轮读取消息的新起点。接着用交接笔记和这之后的新消息组成输入，主 Agent 继续任务。
- **暂时没有：** 现场启动或限时等待 writer。writer 成功后，沿绿色“成功”箭头回到重建流程。
- **writer 仍失败或等待超时：** 改走 compaction（整理当前输入）的备用分支，插入新的读取边界。边界之前的旧消息留在会话存储里，但从这次模型输入中省略。

图底部另有更早的分支：禁用 checkpoint 或记忆写入时，直接走备用整理流程，跳过 writer 等待，也跳过磁盘上已有的 checkpoint。

出错时还要分清两件事。writer 失败会保留旧 watermark，但文件可能已经留下部分修改；后续满足触发条件时，可以再整理未确认的消息范围。文件和数据库（DB）的位置标记分别更新，检查时要一起读回。另一种情况是已有可用 checkpoint、却插入重建边界失败：程序会报告插入失败，此时不会自动改走 compaction 备用分支。

具体阈值、文件预算、最近用户原话、子 Agent 自己的整理流程，以及模型服务商（provider）主动报告溢出的分支，见[可选代码导读](../../docs/systems/mimo-code/code-walkthrough.md)。

本图依据固定提交 [`a273d3450ee05ba5163320eae59d7716b778e480`](https://github.com/XiaomiMiMo/MiMo-Code/tree/a273d3450ee05ba5163320eae59d7716b778e480) 整理，尚未采集完整 writer 与窗口重建的运行记录。源码位置是[阈值处理 `prune.ts`](https://github.com/XiaomiMiMo/MiMo-Code/blob/a273d3450ee05ba5163320eae59d7716b778e480/packages/opencode/src/session/prune.ts#L238-L425)、[writer 与位置标记 `checkpoint.ts`](https://github.com/XiaomiMiMo/MiMo-Code/blob/a273d3450ee05ba5163320eae59d7716b778e480/packages/opencode/src/session/checkpoint.ts#L943-L1068)、[溢出处理 `prompt.ts`](https://github.com/XiaomiMiMo/MiMo-Code/blob/a273d3450ee05ba5163320eae59d7716b778e480/packages/opencode/src/session/prompt.ts#L4815-L4941)。
