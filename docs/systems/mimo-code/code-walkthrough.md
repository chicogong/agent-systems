# 沿一次 checkpoint 与 rebuild 读代码

[返回章节](README.md) · [来源台账](../../../sources/mimo-code.md)

主 Agent 已经修改了几个文件，还要继续处理测试失败。MiMo Code 先在后台整理交接笔记，窗口快满时再用它准备下一轮输入。这里的 checkpoint 指交接笔记，rebuild 指用笔记重新组织输入；下面先看笔记怎样生成，再看换窗口和失败处理。

1. **每轮回复后，先查看 token 用量。** `SessionPrompt` 从已完成的 assistant 消息取 token 用量，调用 `SessionPrune.fireCheckpoints` 判断是否安排笔记整理；随后，`overflowCheck` 另作判断，决定是否换窗口。子 Agent 使用自己的 compaction（上下文压缩）路径，隐藏的有界计算 Agent 不参与这套上下文管理。[`prompt.ts` 4815–4879](https://github.com/XiaomiMiMo/MiMo-Code/blob/a273d3450ee05ba5163320eae59d7716b778e480/packages/opencode/src/session/prompt.ts#L4815-L4879)
2. **到达阈值时，安排 writer。** `defaultThresholdsFor` 按可用窗口大小给出几档阈值，`resolveThresholds` 再处理配置覆盖、排序和上限。`fireCheckpoints` 先检查执行者（actor）是否采用这套机制、开关是否开启，以及是否已有 writer；符合条件时，逐档判断并标记已跨越的阈值。已有 writer 正在工作时，本次检查直接返回，尚未处理的新阈值可以留到下次检查。[`prune.ts` 24–125](https://github.com/XiaomiMiMo/MiMo-Code/blob/a273d3450ee05ba5163320eae59d7716b778e480/packages/opencode/src/session/prune.ts#L24-L125) · [`prune.ts` 238–425](https://github.com/XiaomiMiMo/MiMo-Code/blob/a273d3450ee05ba5163320eae59d7716b778e480/packages/opencode/src/session/prune.ts#L238-L425)
3. **让 writer 在子会话里整理主会话。** `tryStartCheckpointWriter` 取得父会话消息，记下本次整理到哪条消息，补齐缺失的模板文件。`checkpoint.fork` 决定让 writer 继承父上下文，还是只给它一段增量上下文。writer **总在新的 child session（子会话）中运行**，写入路径却按父 session ID 计算，所以笔记仍属于主会话。整理工作由后台 actor 执行，主 Agent 可以继续下一步。[`checkpoint.ts` 640–780](https://github.com/XiaomiMiMo/MiMo-Code/blob/a273d3450ee05ba5163320eae59d7716b778e480/packages/opencode/src/session/checkpoint.ts#L640-L780) · [`checkpoint.ts` 795–998](https://github.com/XiaomiMiMo/MiMo-Code/blob/a273d3450ee05ba5163320eae59d7716b778e480/packages/opencode/src/session/checkpoint.ts#L795-L998)
4. **整理成功后，更新位置标记。** writer 按固定 11 节修改 `checkpoint.md`，必要时也更新项目记忆。程序检查产物，并通过重试帮助它按模板完成整理。writer 成功后，监看执行结果的 settlement watcher 才写入 `last_checkpoint_message_id`，确认这一段消息已整理；失败时保留旧位置，让以后再处理未确认的消息。**失败前的文件改动可能已经留下**，因此需要连同文件一起检查 watermark（成功位置标记）。[writer 指令](https://github.com/XiaomiMiMo/MiMo-Code/blob/a273d3450ee05ba5163320eae59d7716b778e480/packages/opencode/src/agent/prompt/checkpoint-writer.txt) · [校验入口](https://github.com/XiaomiMiMo/MiMo-Code/blob/a273d3450ee05ba5163320eae59d7716b778e480/packages/opencode/src/session/checkpoint-retry.ts#L38-L116) · [成功位置](https://github.com/XiaomiMiMo/MiMo-Code/blob/a273d3450ee05ba5163320eae59d7716b778e480/packages/opencode/src/session/checkpoint.ts#L1009-L1068)
5. **窗口溢出时，选一份可用笔记。** `rebuildEnsuringCheckpoint` **先检查 checkpoint 和 memory write 开关**；任一开关关闭就立即返回，已有笔记也不会被使用。开关开启后，它同时检查文件**和**有效 watermark。已有可用 checkpoint 时，尝试插入重建边界，插入失败返回 `insert-failed`；没有可用 checkpoint 时，现场启动或等待 writer。自动路径最多等 180 秒，手工路径最多等 300 秒；等待超时后，后台 writer 仍可继续工作。[`prompt.ts` 844–1055](https://github.com/XiaomiMiMo/MiMo-Code/blob/a273d3450ee05ba5163320eae59d7716b778e480/packages/opencode/src/session/prompt.ts#L844-L1055)
6. `renderRebuildContext` 给不同材料单独预算：任务、session checkpoint、最近用户原话、项目/全局记忆、notes、索引与最近活动。它把文件中的材料装成文本，并按容量取舍。历史细节是否完整、笔记是否准确，可以在实际任务中对照原始消息检查。[`checkpoint.ts` 1252–1595](https://github.com/XiaomiMiMo/MiMo-Code/blob/a273d3450ee05ba5163320eae59d7716b778e480/packages/opencode/src/session/checkpoint.ts#L1252-L1595)
7. **从新边界开始准备模型输入。** `insertRebuildBoundary` 把这些文本写成一条带 `checkpoint` part 的 user 消息。只有实际生成活动摘要时，才保存 `digestUpTo`，避免把尚未摘要的尾部消息折叠掉。下一轮 `filterCompacted` 从 checkpoint 或 compaction part 标记的位置整理输入；会话表里的旧消息仍保留。[`checkpoint.ts` 1644–1740](https://github.com/XiaomiMiMo/MiMo-Code/blob/a273d3450ee05ba5163320eae59d7716b778e480/packages/opencode/src/session/checkpoint.ts#L1644-L1740) · [`message-v2.ts` 1270–1294](https://github.com/XiaomiMiMo/MiMo-Code/blob/a273d3450ee05ba5163320eae59d7716b778e480/packages/opencode/src/session/message-v2.ts#L1270-L1294)
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

本文依据 [`a273d345`](https://github.com/XiaomiMiMo/MiMo-Code/tree/a273d3450ee05ba5163320eae59d7716b778e480) 的静态源码，尚未运行 writer 与数据库。上面的流程摘要跟着主 Agent；子 Agent、writer 排队和模型服务主动报告溢出的细节，需继续读对应分支。手工 `/rebuild` 复用核心决策，界面另有实现。实际恢复还需观察中途失败后的文件、watermark 和真实模型请求的时间顺序。
