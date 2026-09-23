# 审批、沙箱、工作目录：三个不同的边界

[返回机制目录](README.md) · [Codex 决策图](../systems/codex/README.md) · [OpenHands 事件图](../systems/openhands/README.md)

![Codex 一次命令的审批与执行决策](../../figures/codex-exec-approval/diagram.svg)

Agent 请求执行命令时，“问过用户”“在沙箱里跑”“只在项目目录运行”回答的是三个不同问题：

| 边界 | 回答的问题 | 它本身不保证 |
| --- | --- | --- |
| 审批 | 这次动作是否被允许启动？ | 执行过程不会访问别处或产生副作用 |
| 沙箱/隔离 | 动作运行时可访问哪些资源？ | 用户同意了动作，或结果已经正确 |
| 工作目录 | 命令从哪个路径开始解析相对文件？ | 路径外资源不可访问 |

固定源码中的两个例子说明这一区分。Codex Rust core 的 `exec_command` 先得出 `Skip / NeedsApproval / Forbidden`，再选择沙箱与执行；`Skip` 是无需普通审批，不等于必然无沙箱。[执行策略](https://github.com/openai/codex/blob/c44deff7b1083e9660ac55d02122481f1cdf139b/codex-rs/core/src/exec_policy.rs#L337-L458) · [沙箱选择](https://github.com/openai/codex/blob/c44deff7b1083e9660ac55d02122481f1cdf139b/codex-rs/core/src/tools/sandboxing.rs#L239-L279)

OpenHands SDK 的局部路径则先记 `ActionEvent`，需要确认时停在 `WAITING_FOR_CONFIRMATION`；获准后工具才可能执行。[确认闸门](https://github.com/OpenHands/software-agent-sdk/blob/6ebd820d10794f1b52bb06ef6c19512888a1401b/openhands-sdk/openhands/sdk/agent/response_dispatch.py#L163-L190) 其 `TerminalTool` 使用 workspace 的 `working_dir`，但这只是工作目录来源；真正的隔离要看所选 workspace 和部署方式。[TerminalTool](https://github.com/OpenHands/software-agent-sdk/blob/6ebd820d10794f1b52bb06ef6c19512888a1401b/openhands-tools/openhands/tools/terminal/definition.py#L294-L330)

这两个例子不是安全性能评测，也不表示两套产品的授权模型完全可比。本文只建立阅读源码时的提问顺序：**先看谁能发起动作，再看谁能批准，再看执行环境可触达什么，最后检查副作用与结果。**任何一层的“通过”都不能替代后一层的验证。
