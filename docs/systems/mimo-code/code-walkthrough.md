# 沿一次 checkpoint 与 rebuild 读代码

[返回章节](README.md) · [来源台账](../../../sources/mimo-code.md)

想读代码时，按“提前整理—记录位置—换窗口—准备下一轮输入”找四个入口即可。checkpoint 是交接笔记，rebuild 是用笔记重新组织输入。以下固定在 [`a273d345`](https://github.com/XiaomiMiMo/MiMo-Code/tree/a273d3450ee05ba5163320eae59d7716b778e480)，先跟主 Agent 的正常路径，再看几处失败处理。手工 `/rebuild` 复用核心决策，其界面另看源码。

1. `SessionPrompt` 的循环从已完成 assistant 消息取 token 用量，调用 `SessionPrune.fireCheckpoints`；随后 `overflowCheck` 独立决定是否重建。子 Agent 走自己的 compaction 路径，隐藏的有界计算 Agent 不参与这套上下文管理。[`prompt.ts` 4815–4879](https://github.com/XiaomiMiMo/MiMo-Code/blob/a273d3450ee05ba5163320eae59d7716b778e480/packages/opencode/src/session/prompt.ts#L4815-L4879)
2. `defaultThresholdsFor` 根据可用窗口给出阈值梯度，`resolveThresholds` 处理覆盖值、排序和上限。`fireCheckpoints` 排除不服务此机制的 actor、关闭开关和已有 writer 的情况；逐档判断并标记跨越。已在运行的 writer 会使本次检查直接返回，尚未消费的新阈值可留到下一次检查。[`prune.ts` 24–125](https://github.com/XiaomiMiMo/MiMo-Code/blob/a273d3450ee05ba5163320eae59d7716b778e480/packages/opencode/src/session/prune.ts#L24-L125) · [`prune.ts` 238–425](https://github.com/XiaomiMiMo/MiMo-Code/blob/a273d3450ee05ba5163320eae59d7716b778e480/packages/opencode/src/session/prune.ts#L238-L425)
3. `tryStartCheckpointWriter` 取得父会话消息，确定本次覆盖的结尾位置，建立缺失的模板文件，并按 `checkpoint.fork` 选择继承父上下文或给 writer 一段增量上下文。writer **总在新 child session** 运行，但写入路径按父 session ID 算；生成过程是后台 actor 调用，不阻塞主 Agent 的每一步。[`checkpoint.ts` 640–780](https://github.com/XiaomiMiMo/MiMo-Code/blob/a273d3450ee05ba5163320eae59d7716b778e480/packages/opencode/src/session/checkpoint.ts#L640-L780) · [`checkpoint.ts` 795–998](https://github.com/XiaomiMiMo/MiMo-Code/blob/a273d3450ee05ba5163320eae59d7716b778e480/packages/opencode/src/session/checkpoint.ts#L795-L998)
4. writer 按固定 11 节原地维护 `checkpoint.md`，必要时更新项目记忆。运行时再通过校验和重试检查 writer 产物，帮助它按模板完成整理。writer 成功后 settlement watcher 才写 `last_checkpoint_message_id`；失败保留旧位置，让以后 writer 重试未确认的消息范围。**失败前的文件改动可能已经留下**，旧 watermark 不保证磁盘文件仍是上次成功版本。[writer 指令](https://github.com/XiaomiMiMo/MiMo-Code/blob/a273d3450ee05ba5163320eae59d7716b778e480/packages/opencode/src/agent/prompt/checkpoint-writer.txt) · [校验入口](https://github.com/XiaomiMiMo/MiMo-Code/blob/a273d3450ee05ba5163320eae59d7716b778e480/packages/opencode/src/session/checkpoint-retry.ts#L38-L116) · [成功位置](https://github.com/XiaomiMiMo/MiMo-Code/blob/a273d3450ee05ba5163320eae59d7716b778e480/packages/opencode/src/session/checkpoint.ts#L1009-L1068)
5. 主 Agent 溢出时，`rebuildEnsuringCheckpoint` **先检查开关**：禁用 checkpoint 或 memory write 时立即返回，不使用已有 checkpoint。只有开关开启，才尝试已有文件**和**有效 watermark。已有 checkpoint 但插入边界失败返回 `insert-failed`；没有可用 checkpoint 则现场启动或等待 writer，自动路径最多等 180 秒，手工路径最多等 300 秒。等待超时不取消后台 writer。[`prompt.ts` 844–1055](https://github.com/XiaomiMiMo/MiMo-Code/blob/a273d3450ee05ba5163320eae59d7716b778e480/packages/opencode/src/session/prompt.ts#L844-L1055)
6. `renderRebuildContext` 给不同材料单独预算：任务、session checkpoint、最近用户原话、项目/全局记忆、notes、索引与最近活动。它把文件中的材料装成文本，并按容量取舍。历史细节是否完整、笔记是否准确，可以在实际任务中对照原始消息检查。[`checkpoint.ts` 1252–1595](https://github.com/XiaomiMiMo/MiMo-Code/blob/a273d3450ee05ba5163320eae59d7716b778e480/packages/opencode/src/session/checkpoint.ts#L1252-L1595)
7. `insertRebuildBoundary` 把上述文本写入带 `checkpoint` part 的合成 user 消息；只有实际生成活动摘要时才保存 `digestUpTo`，避免没有摘要却折叠尾部。下一轮 `filterCompacted` 以 checkpoint 或 compaction part 为投影边界，不删除会话表里的旧消息。[`checkpoint.ts` 1644–1740](https://github.com/XiaomiMiMo/MiMo-Code/blob/a273d3450ee05ba5163320eae59d7716b778e480/packages/opencode/src/session/checkpoint.ts#L1644-L1740) · [`message-v2.ts` 1270–1294](https://github.com/XiaomiMiMo/MiMo-Code/blob/a273d3450ee05ba5163320eae59d7716b778e480/packages/opencode/src/session/message-v2.ts#L1270-L1294)
8. 开关关闭，或开启后仍没有可用 checkpoint 且 writer 失败/超时，自动溢出路径插入 compaction 边界；已有 checkpoint 但插入失败时，不走这条退路。最后阈值的后台 writer 失败时，只有可重试错误且剩余窗口足够，才设下一次恢复门槛。[`prompt.ts` 4871–4941](https://github.com/XiaomiMiMo/MiMo-Code/blob/a273d3450ee05ba5163320eae59d7716b778e480/packages/opencode/src/session/prompt.ts#L4871-L4941) · [`prune.ts` 350–416](https://github.com/XiaomiMiMo/MiMo-Code/blob/a273d3450ee05ba5163320eae59d7716b778e480/packages/opencode/src/session/prune.ts#L350-L416)

```text
已完成回复的 token 用量 → 跨阈值？ → 异步 writer → 文件 + 成功 watermark
                                  主 Agent 继续
上下文溢出 → checkpoint / memory write 开关开启？
             ├─ 否 → compaction 边界（不使用已有 checkpoint）
             └─ 是 → 已有可用 checkpoint？
                       ├─ 是 → 插入重建边界 → 下一轮投影从边界开始
                       └─ 否 → 现场启动/等待 writer → 成功则重建；失败则退化到 compaction
```

上面的路径图展示主流程，已经画出禁用开关的出口；子 Agent、writer 排队、模型服务主动报溢出和手工 `/rebuild` 的细节请看链接代码。本文按源码讲解，尚未运行 writer 与数据库；要验证恢复，还需观察中途失败时文件与 watermark 是否对应，以及真实模型服务下的时序。
