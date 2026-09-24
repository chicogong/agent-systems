# 沿一次 checkpoint 与 rebuild 读代码

[返回章节](README.md) · [来源台账](../../../sources/mimo-code.md)

以下是 [`a273d3450ee05ba5163320eae59d7716b778e480`](https://github.com/XiaomiMiMo/MiMo-Code/tree/a273d3450ee05ba5163320eae59d7716b778e480) 的**静态控制流摘要**，不是运行轨迹。跟读范围为主 Agent 的正常阈值触发、溢出与几个重要失败分支；手工 `/rebuild` 复用同一核心决策，但其用户交互和所有边界不在此展开。

1. `SessionPrompt` 的循环从已完成 assistant 消息取 token 用量，调用 `SessionPrune.fireCheckpoints`；随后 `overflowCheck` 独立决定是否重建。子 Agent 走自己的 compaction 路径，隐藏的有界计算 Agent 不参与这套上下文管理。[`prompt.ts` 4815–4879](https://github.com/XiaomiMiMo/MiMo-Code/blob/a273d3450ee05ba5163320eae59d7716b778e480/packages/opencode/src/session/prompt.ts#L4815-L4879)
2. `defaultThresholdsFor` 根据可用窗口给出阈值梯度，`resolveThresholds` 处理覆盖值、排序和上限。`fireCheckpoints` 排除不服务此机制的 actor、关闭开关和已有 writer 的情况；逐档判断并标记跨越。已在运行的 writer 会使本次检查直接返回，尚未消费的新阈值可留到下一次检查。[`prune.ts` 24–125](https://github.com/XiaomiMiMo/MiMo-Code/blob/a273d3450ee05ba5163320eae59d7716b778e480/packages/opencode/src/session/prune.ts#L24-L125) · [`prune.ts` 238–425](https://github.com/XiaomiMiMo/MiMo-Code/blob/a273d3450ee05ba5163320eae59d7716b778e480/packages/opencode/src/session/prune.ts#L238-L425)
3. `tryStartCheckpointWriter` 取得父会话消息，确定本次覆盖的结尾位置，建立缺失的模板文件，并按 `checkpoint.fork` 选择继承父上下文或给 writer 一段增量上下文。writer **总在新 child session** 运行，但写入路径按父 session ID 算；生成过程是后台 actor 调用，不阻塞主 Agent 的每一步。[`checkpoint.ts` 640–780](https://github.com/XiaomiMiMo/MiMo-Code/blob/a273d3450ee05ba5163320eae59d7716b778e480/packages/opencode/src/session/checkpoint.ts#L640-L780) · [`checkpoint.ts` 795–998](https://github.com/XiaomiMiMo/MiMo-Code/blob/a273d3450ee05ba5163320eae59d7716b778e480/packages/opencode/src/session/checkpoint.ts#L795-L998)
4. writer 按固定 11 节原地维护 `checkpoint.md`，必要时更新项目记忆。提示文本只是要求，不能证明模型每次都正确执行；运行时还以校验/重试路径检查产物。writer 成功后 settlement watcher 才写 `last_checkpoint_message_id`；失败保留旧位置，让以后 writer 重试未确认的消息范围。**失败前的文件改动可能已经留下**，旧 watermark 不保证磁盘文件仍是上次成功版本。[writer 指令](https://github.com/XiaomiMiMo/MiMo-Code/blob/a273d3450ee05ba5163320eae59d7716b778e480/packages/opencode/src/agent/prompt/checkpoint-writer.txt) · [校验入口](https://github.com/XiaomiMiMo/MiMo-Code/blob/a273d3450ee05ba5163320eae59d7716b778e480/packages/opencode/src/session/checkpoint-retry.ts#L38-L116) · [成功位置](https://github.com/XiaomiMiMo/MiMo-Code/blob/a273d3450ee05ba5163320eae59d7716b778e480/packages/opencode/src/session/checkpoint.ts#L1009-L1068)
5. 主 Agent 溢出时，`rebuildEnsuringCheckpoint` 先尝试已有文件**和**有效 watermark。已有 checkpoint 但插入边界失败返回 `insert-failed`；没有可用 checkpoint 则现场启动或等待 writer，自动路径最多等 180 秒，手工路径最多等 300 秒。等待超时不取消后台 writer。[`prompt.ts` 844–1055](https://github.com/XiaomiMiMo/MiMo-Code/blob/a273d3450ee05ba5163320eae59d7716b778e480/packages/opencode/src/session/prompt.ts#L844-L1055)
6. `renderRebuildContext` 给不同材料单独预算：任务、session checkpoint、最近用户原话、项目/全局记忆、notes、索引与最近活动。它读文件形成文本，既不是把整个 SQLite 历史重新塞进模型，也不保证文件内容完全准确。[`checkpoint.ts` 1252–1595](https://github.com/XiaomiMiMo/MiMo-Code/blob/a273d3450ee05ba5163320eae59d7716b778e480/packages/opencode/src/session/checkpoint.ts#L1252-L1595)
7. `insertRebuildBoundary` 把上述文本写入带 `checkpoint` part 的合成 user 消息；只有实际生成活动摘要时才保存 `digestUpTo`，避免没有摘要却折叠尾部。下一轮 `filterCompacted` 以 checkpoint 或 compaction part 为投影边界，不删除会话表里的旧消息。[`checkpoint.ts` 1644–1740](https://github.com/XiaomiMiMo/MiMo-Code/blob/a273d3450ee05ba5163320eae59d7716b778e480/packages/opencode/src/session/checkpoint.ts#L1644-L1740) · [`message-v2.ts` 1270–1294](https://github.com/XiaomiMiMo/MiMo-Code/blob/a273d3450ee05ba5163320eae59d7716b778e480/packages/opencode/src/session/message-v2.ts#L1270-L1294)
8. 若没有可用 checkpoint 且 writer 失败/超时/被关闭，自动溢出路径插入 compaction 边界；已有 checkpoint 但插入失败时，不走这条退路。最后阈值的后台 writer 失败时，只有可重试错误且剩余窗口足够，才设下一次恢复门槛。[`prompt.ts` 4871–4941](https://github.com/XiaomiMiMo/MiMo-Code/blob/a273d3450ee05ba5163320eae59d7716b778e480/packages/opencode/src/session/prompt.ts#L4871-L4941) · [`prune.ts` 350–416](https://github.com/XiaomiMiMo/MiMo-Code/blob/a273d3450ee05ba5163320eae59d7716b778e480/packages/opencode/src/session/prune.ts#L350-L416)

```text
已完成回复的 token 用量 → 跨阈值？ → 异步 writer → 文件 + 成功 watermark
                                  主 Agent 继续
上下文溢出 → 已有可用 checkpoint？
             ├─ 是 → 插入重建边界 → 下一轮投影从边界开始
             └─ 否 → 现场启动/等待 writer → 成功则重建；失败则退化到 compaction
```

这段伪代码省略了禁用开关、子 Agent 分支、同会话 writer 排队、provider 主动报溢出和手工 `/rebuild`；详见对应源码，不能据此推断系统总能恢复。特别是 writer 原地改写文件后普通失败或崩溃时与 DB watermark 的一致性、长时间后台 actor 与真实 provider 的时序，本稿没有运行核验。
