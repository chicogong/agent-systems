# MiMo Code checkpoint 与重建图的文字版

[返回章节](../../docs/systems/mimo-code/README.md) · [可编辑图源](scene.excalidraw) · [SVG](diagram.svg) · [PNG](preview.png)

这张图回答“写 checkpoint 与换上下文窗口是否为同一时刻”。上半部是提前写入：主 Agent 继续执行任务，已完成回复的 token 用量跨过阈值时触发后台 writer。下半部是独立的 overflow 判断；只有需要换窗口时，运行时才检查能否用已写状态重建。

writer 在独立 child session 中读取截至固定消息位置的历史，原地编辑父会话 `checkpoint.md`，必要时维护项目 `MEMORY.md`。只有 writer 成功，父会话 watermark 才推进；它表示**成功确认的覆盖位置**，不保证文件与 DB 原子更新。writer 普通失败前可能已改写文件，但 watermark 仍旧。上半部的三个节点说明触发、后台提取和成功确认，不表示主 Agent 每一步都等待 writer。

下半部的分叉表示互斥条件：有可用 checkpoint 时，插入重建边界，让下一窗口读到结构化状态和边界后的活消息；没有时，系统尝试现场启动并有限等待 writer。仍失败、超时或写入被禁用，则退化为 compaction 边界，旧消息不再进入当前模型投影。writer 失败时旧 watermark 保持不变，下一阈值可重试未确认的消息范围；但文件可能已有部分改动。图省略了阈值配置、子 Agent 的独立 compaction、文件预算、最近用户原话及 provider 主动报溢出分支；详见[代码导读](../../docs/systems/mimo-code/code-walkthrough.md)。

所有箭头来自固定提交 [`a273d3450ee05ba5163320eae59d7716b778e480`](https://github.com/XiaomiMiMo/MiMo-Code/tree/a273d3450ee05ba5163320eae59d7716b778e480) 的静态源码阅读。主要定位是 [`prune.ts` 阈值](https://github.com/XiaomiMiMo/MiMo-Code/blob/a273d3450ee05ba5163320eae59d7716b778e480/packages/opencode/src/session/prune.ts#L238-L425)、[`checkpoint.ts` writer 与 watermark](https://github.com/XiaomiMiMo/MiMo-Code/blob/a273d3450ee05ba5163320eae59d7716b778e480/packages/opencode/src/session/checkpoint.ts#L943-L1068)、[`prompt.ts` 溢出分支](https://github.com/XiaomiMiMo/MiMo-Code/blob/a273d3450ee05ba5163320eae59d7716b778e480/packages/opencode/src/session/prompt.ts#L4815-L4941)。这不是运行轨迹。
