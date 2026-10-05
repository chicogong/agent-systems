# Codex：先检查权限，再运行命令

[返回系统目录](../README.md) · [关键代码路径](code-walkthrough.md) · [图的文字版](../../../figures/codex-exec-approval/README.md)

## 30 秒读懂

假设你让 Codex 运行项目测试。模型提出命令后，接入 Codex 的程序会先检查命令参数、执行环境和权限，再决定这次可以直接继续、需要批准，还是应当拒绝。通过这些检查后，命令才会在选定的执行环境里运行。

源码用三个名字表示审批决定：`Skip` 是跳过普通询问，`NeedsApproval` 是需要批准，`Forbidden` 是禁止执行。负责接收调用的处理器（Handler）先整理请求，执行策略（exec policy）给出决定，执行编排器（Orchestrator）安排审批与运行。[整理请求](https://github.com/openai/codex/blob/c44deff7b1083e9660ac55d02122481f1cdf139b/codex-rs/core/src/tools/handlers/unified_exec/exec_command.rs#L186-L245) · [作出审批决定](https://github.com/openai/codex/blob/c44deff7b1083e9660ac55d02122481f1cdf139b/codex-rs/core/src/exec_policy.rs#L337-L458) · [安排执行](https://github.com/openai/codex/blob/c44deff7b1083e9660ac55d02122481f1cdf139b/codex-rs/core/src/tools/orchestrator.rs#L116-L220)

![Codex exec_command 的审批与执行决策图](../../../figures/codex-exec-approval/diagram.svg)

[可编辑图源](../../../figures/codex-exec-approval/scene.excalidraw) · [PNG 预览](../../../figures/codex-exec-approval/preview.png) · [不看图的说明](../../../figures/codex-exec-approval/README.md)

## 批准执行与限制访问，是两件事

审批回答“这次允不允许做”；沙箱回答“执行时允许访问哪些文件、网络等资源”。因此，跳过普通询问的 `Skip` 请求仍可能在沙箱中执行。部分请求可以按规则跳过首次沙箱，但禁止读取某些文件的限制（deny-read）会阻止这种绕过。[首次沙箱的选择条件](https://github.com/openai/codex/blob/c44deff7b1083e9660ac55d02122481f1cdf139b/codex-rs/core/src/tools/sandboxing.rs#L239-L279)

第一次运行被沙箱拒绝时，程序会继续检查拒绝原因和当前策略。有的请求停在这里，有的需要再次批准，有的可以按规定重试。普通命令报错与沙箱拒绝分别处理。

具体使用哪条规则还与配置和平台有关。命令没有匹配已有规则时，代码会结合审批策略、沙箱配置和命令分类作后续判断。[未匹配命令的处理](https://github.com/openai/codex/blob/c44deff7b1083e9660ac55d02122481f1cdf139b/codex-rs/core/src/exec_policy.rs#L770-L858)

## 下一步

想读代码，就跟着[一次命令的处理过程](code-walkthrough.md)往下走；想作比较，可以看看 Pi 如何把工具交给循环核心。本文先讲清这条命令路径，Codex 的回合状态、上下文压缩和 Skill 加载需要分别阅读。

## 来源与阅读范围

本文依据官方仓库 [`openai/codex@c44deff7b1083e9660ac55d02122481f1cdf139b`](https://github.com/openai/codex/tree/c44deff7b1083e9660ac55d02122481f1cdf139b)，核对日期 2026-09-23，只介绍 Rust core 中 `exec_command` 的相关代码。不同宿主、工具和配置需要分别检查，本篇尚未运行该提交。
