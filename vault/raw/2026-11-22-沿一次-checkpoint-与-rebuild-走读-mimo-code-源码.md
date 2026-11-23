---
title: "沿一次 checkpoint 与 rebuild 走读 MiMo Code 源码"
origin: "/Users/haorangong/Github/chicogong/experiments/agent-systems/docs/systems/mimo-code/code-walkthrough.md"
sha256: "e5066e34e3427b0c7fb0278d1b7e3d8118406742b8ba936ef36fa9cd04935a5e"
ingested_at: "2026-11-22T13:54:22.928Z"
tags: []
---

# 沿一次 checkpoint 与 rebuild 走读 MiMo Code 源码

# 沿一次 checkpoint 与 rebuild 走读 MiMo Code 源码

[返回章节](README.md) · [来源台账](../../../sources/mimo-code.md)

主 Agent 已经连续改完好几个模块，正埋头排查单测报错，上下文窗口眼看就要见底。MiMo Code 是怎样做到平时在后台悄悄攒好交接笔记、到溢出那一刻安全换窗，又在开关关闭或后台报错时守住退路的？

沿着主 Agent 的 8 个代码节点顺流而下，就能把「梯度触发 → 子会话写盘 → 水位线落锁 → 溢出门禁与窗口投影」的每一个分支看个通透。

```text
每轮 assistant 回复完成 → 读取 token 用量
  ├─ 1. SessionPrune.fireCheckpoints：跨过梯度阈值且无活跃 writer？
  │      └─ 拉起独立 child session 后台运行 writer → 写父会话 checkpoint.md
  │           ├─ 校验通过 → settlement watcher 推进 last_checkpoint_message_id（成功水位线）
  │           └─ 失败退出 → 保留旧水位线（磁盘文件可能残留半截修改）
  └─ 2. overflowCheck：上下文容量触及溢出线？ → 调用 rebuildEnsuringCheckpoint
         ├─ checkpoint 或 memory write 任一开关关闭 → 直接返回，走 compaction 压缩边界（忽略已有文件）
         └─ 双开关均开启 → 同时核对「有效文件 + 有效 watermark」
              ├─ 已就绪 → renderRebuildContext 分项预算装配 → insertRebuildBoundary 写入新起点
              │             └─ 若插入本身报错返回 insert-failed，不再退化到 compaction
              └─ 未就绪 → 现场拉起或限时等待 writer（自动 180s / 手动 300s）
                            ├─ 等待期内成功 → 插入重建边界，下一轮 filterCompacted 从新边界投影
                            └─ 超时或失败   → 自动溢出分支退化插入 compaction 边界
```

## 1. 后台提前提炼：子会话隔离运行，成功后才推进水位线

1. **双表盘监控 token 用量**：每当一轮 assistant 消息生成完毕，`SessionPrompt` 先取出最新 token 消耗，调 `SessionPrune.fireCheckpoints` 判断是否需要提前安排后台写笔记；紧接着再由 `overflowCheck` 独立判断是否已经撞上窗口上限需要立刻换窗。注意这套长程接力只服务主 Agent——普通子 Agent 走各自的常规 `compaction` 压缩路径，而隐藏的有界计算 Agent 则完全不参与这套上下文管理。[`prompt.ts` 4815–4879](https://github.com/XiaomiMiMo/MiMo-Code/blob/a273d3450ee05ba5163320eae59d7716b778e480/packages/opencode/src/session/prompt.ts#L4815-L4879)
2. **梯度阈值与单飞互斥**：`defaultThresholdsFor` 根据可用窗口大小计算默认百分比档位，`resolveThresholds` 合并用户自定义配置并排序裁剪。进入 `fireCheckpoints` 后，程序先核验当前执行者（actor）类型、功能开关以及**是否已有后台 `writer` 正在运行**——如果上一个 `writer` 还没忙完，本次检查立刻退出，绝不并发拉起两个 `writer` 互踩文件；刚刚跨过的新档位留待后续轮次再补。[`prune.ts` 24–125](https://github.com/XiaomiMiMo/MiMo-Code/blob/a273d3450ee05ba5163320eae59d7716b778e480/packages/opencode/src/session/prune.ts#L24-L125) · [`prune.ts` 238–425](https://github.com/XiaomiMiMo/MiMo-Code/blob/a273d3450ee05ba5163320eae59d7716b778e480/packages/opencode/src/session/prune.ts#L238-L425)
3. **子会话执行、父路径落盘**：`tryStartCheckpointWriter` 读取父会话消息列表，拍下本次准备整理到的目标消息编号，并按需初始化缺失的模板文件（由 `checkpoint.fork` 控制是继承完整父上下文还是只喂增量片段）。精巧的设计在于：**后台整理者永远在新建的独立 `child session` 里跑推理循环，但它落盘的目标路径却按父会话 ID 计算**——既不污染主会话的消息流，又把交接产物精准写回主会话名下。[`checkpoint.ts` 640–780](https://github.com/XiaomiMiMo/MiMo-Code/blob/a273d3450ee05ba5163320eae59d7716b778e480/packages/opencode/src/session/checkpoint.ts#L640-L780) · [`checkpoint.ts` 795–998](https://github.com/XiaomiMiMo/MiMo-Code/blob/a273d3450ee05ba5163320eae59d7716b778e480/packages/opencode/src/session/checkpoint.ts#L795-L998)
4. **模板重试与水位线落锁**：`writer` 按固定 11 节结构更新 `checkpoint.md`（必要时同步维护项目记忆），程序会对产物做结构校验并通过重试引导它补齐格式。只有当后台结算监听器（settlement watcher）确认 `writer` 完整成功收官，才会更新 `last_checkpoint_message_id`；倘若中途失败，水位线原封不动停在上次成功的位置，留待日后重跑。由于**失败前写入磁盘的局部文件改动不会自动回滚**，后续任何读取方都必须把文件与水位线捆绑核验。[writer 指令](https://github.com/XiaomiMiMo/MiMo-Code/blob/a273d3450ee05ba5163320eae59d7716b778e480/packages/opencode/src/agent/prompt/checkpoint-writer.txt) · [校验入口](https://github.com/XiaomiMiMo/MiMo-Code/blob/a273d3450ee05ba5163320eae59d7716b778e480/packages/opencode/src/session/checkpoint-retry.ts#L38-L116) · [成功位置](https://github.com/XiaomiMiMo/MiMo-Code/blob/a273d3450ee05ba5163320eae59d7716b778e480/packages/opencode/src/session/checkpoint.ts#L1009-L1068)

## 2. 溢出换窗：前置开关绕过、分项预算与边界投影

5. **溢出入口的双开关前置条件与限时等待**：窗口告警进入 `rebuildEnsuringCheckpoint` 时，**第一道门槛就是同时检查 `checkpoint` 开关与 `memory write` 开关**——只要其中任意一个被关闭，函数立刻短路返回，哪怕磁盘上已有旧检查点文件也一概不用。双开关开启后，程序同时核查文件内容与有效 `watermark`：已就绪则直接尝试插入重建边界（若插入动作本身出错则返回 `insert-failed`）；尚未就绪则现场启动或等待已在跑的后台 `writer`（自动溢出最多等 180 秒，手动触发最多等 300 秒；超时返回后后台 `writer` 仍可继续跑完）。[`prompt.ts` 844–1055](https://github.com/XiaomiMiMo/MiMo-Code/blob/a273d3450ee05ba5163320eae59d7716b778e480/packages/opencode/src/session/prompt.ts#L844-L1055)
6. **分项预算防挤压**：`renderRebuildContext` 不会把所有文件一股脑塞进去，而是给任务状态、会话 `checkpoint.md`、最近用户原话、项目与全局记忆、`notes.md`、索引以及近期活动分别划定容量预算，按优先级裁剪拼装成重建文本。[`checkpoint.ts` 1252–1595](https://github.com/XiaomiMiMo/MiMo-Code/blob/a273d3450ee05ba5163320eae59d7716b778e480/packages/opencode/src/session/checkpoint.ts#L1252-L1595)
7. **写入边界消息与谨慎折叠尾部**：`insertRebuildBoundary` 把拼好的交接文本写成一条携带 `checkpoint` 片段（part）的特殊 `user` 消息。注意一处极细致的防丢数据保护：**只有当本次确实成功生成了水位线之后的尾部活动摘要时，才会记录 `digestUpTo` 标记**，从而绝不会把还没来得及摘要的尾部增量消息误折叠掉。到了下一轮请求模型时，`filterCompacted` 从最新的 `checkpoint` 或 `compaction` 标记位开始向后截取窗口，底层会话表里的历史记录依然完整保留。[`checkpoint.ts` 1644–1740](https://github.com/XiaomiMiMo/MiMo-Code/blob/a273d3450ee05ba5163320eae59d7716b778e480/packages/opencode/src/session/checkpoint.ts#L1644-L1740) · [`message-v2.ts` 1270–1294](https://github.com/XiaomiMiMo/MiMo-Code/blob/a273d3450ee05ba5163320eae59d7716b778e480/packages/opencode/src/session/message-v2.ts#L1270-L1294)
8. **兜底退化与末档重试门槛**：当任一开关关闭，或双开关开启但无可用检查点且等待 `writer` 失败/超时时，自动溢出逻辑会退化插入常规 `compaction` 压缩边界来保住会话不断裂；唯独「已有可用检查点、却在插入边界时失败（`insert-failed`）」不会盲目走这条退路。另外，如果最后一档阈值的后台 `writer` 执行失败，只有当错误属于可重试类型且剩余窗口空间还够用时，系统才会补设下一道恢复重试门槛。[`prompt.ts` 4871–4941](https://github.com/XiaomiMiMo/MiMo-Code/blob/a273d3450ee05ba5163320eae59d7716b778e480/packages/opencode/src/session/prompt.ts#L4871-L4941) · [`prune.ts` 350–416](https://github.com/XiaomiMiMo/MiMo-Code/blob/a273d3450ee05ba5163320eae59d7716b778e480/packages/opencode/src/session/prune.ts#L350-L416)

## 来源与边界

本篇导读依据 [`XiaomiMiMo/MiMo-Code@a273d3450ee05ba5163320eae59d7716b778e480`](https://github.com/XiaomiMiMo/MiMo-Code/tree/a273d3450ee05ba5163320eae59d7716b778e480) 静态梳理主 Agent 的检查点调度与窗口重建代码；子 Agent 独立压缩分支、模型服务端主动报错触发的溢出分支、手工 `/rebuild` 命令界面层以及真实故障中断后的磁盘残留恢复表现，需结合对应源码与运行实验进一步核查。
