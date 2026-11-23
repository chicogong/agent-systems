---
title: "跟着 Codex 代码走一次 `exec_command`：从策略判准到沙箱升权重试"
origin: "/Users/haorangong/Github/chicogong/experiments/agent-systems/docs/systems/codex/code-walkthrough.md"
sha256: "39e90f4d7cade22677dcd3a63c28bc87c74911fc76d640cfa8b43a970e8df47f"
ingested_at: "2026-11-22T13:54:22.824Z"
tags: []
---

# 跟着 Codex 代码走一次 `exec_command`：从策略判准到沙箱升权重试

# 跟着 Codex 代码走一次 `exec_command`：从策略判准到沙箱升权重试

[返回 Codex 首篇](README.md) · [固定源码](https://github.com/openai/codex/tree/c44deff7b1083e9660ac55d02122481f1cdf139b)

大模型递过来一句 shell 命令时，最粗糙的实现只需五行 `Command::new("sh").arg("-c")`；而在生产级编码 Agent 里，这句命令在真正 fork 出操作系统子进程前，必须闯过参数体检、回合权限合并、复合命令拆解、首次沙箱选型和撞墙升权裁决五道关卡。

下面我们锁定 `codex-rs/core` 的固定提交，顺着一条普通 `exec_command` 工具调用的生命周期，逐段拆解这五道关卡为什么要这样写。

## 1. 入口体检与补丁分流：`ExecCommandHandler::handle_call`

工具调用的第一站是 `ExecCommandHandler::handle_call`。在接触任何进程管理器之前，它先对请求载荷做严格的前置体检：解析命令参数、核对当前运行环境是否支持统一执行、检查伪终端（TTY）标志是否合法，并验证工作目录 `workdir` 是否有效；任何一项不合规都会在创建进程前直接折返为模型可读的工具错误（见[接收并检查请求](https://github.com/openai/codex/blob/c44deff7b1083e9660ac55d02122481f1cdf139b/codex-rs/core/src/tools/handlers/unified_exec/exec_command.rs#L170-L245)）。

紧接着是一步很容易被忽略的**权限天花板校验**：模型有时会在工具参数里主动通过 `sandbox_permissions` 伸手讨要更高权限。Handler 会把本次申请的权限与当前回合已获授的权限合并，对照当前会话策略做检查——如果宿主策略压根禁止模型主动讨要额外权限，请求当场就会被驳回，连后面的审批编排器都进不去（见[执行前检查权限](https://github.com/openai/codex/blob/c44deff7b1083e9660ac55d02122481f1cdf139b/codex-rs/core/src/tools/handlers/unified_exec/exec_command.rs#L322-L376)）。

这里还有一个专门的分流口：如果模型没有调专门的改文件工具，而是试图在 `exec_command` 的命令行里调用 `apply_patch` 打补丁，处理器会识别出这类请求并直接转交[专用补丁路径](https://github.com/openai/codex/blob/c44deff7b1083e9660ac55d02122481f1cdf139b/codex-rs/core/src/tools/handlers/unified_exec/exec_command.rs#L378-L405)做细粒度文件变更审查与落盘，提前返回，避免让结构化的代码修改混同于黑盒 shell 脚本。

## 2. 复合命令防夹带与三态审批：`ExecPolicy`

普通命令穿过入口体检后，进入 `UnifiedExecProcessManager::open_session_with_sandbox`。它先请 `exec_policy` 对命令定性，算出 `ExecApprovalRequirement`，再把接力棒交给 `ToolOrchestrator::run`（见[交给策略和编排器](https://github.com/openai/codex/blob/c44deff7b1083e9660ac55d02122481f1cdf139b/codex-rs/core/src/unified_exec/process_manager.rs#L1477-L1535)）。

为什么 `exec_policy` 不能只拿前缀匹配命令开头？设想模型拼出一条复合命令 `git status && rm -rf ../other-repo`——如果只看开头的 `git status` 就放行，白名单瞬间就会被绕穿。因此源码在[生成审批决定](https://github.com/openai/codex/blob/c44deff7b1083e9660ac55d02122481f1cdf139b/codex-rs/core/src/exec_policy.rs#L394-L460)与[执行审批决定](https://github.com/openai/codex/blob/c44deff7b1083e9660ac55d02122481f1cdf139b/codex-rs/core/src/tools/orchestrator.rs#L151-L220)时守住了两条硬规则：

- **三态精准落定**：命中禁令，或原本需要人工确认但当前策略关闭了交互询问通道时，一律判为 `Forbidden`；需要人工拍板时判为 `NeedsApproval`；常规安全命令判为 `Skip`（若开启严格自动审查模式，即便 `Skip` 了人工弹窗，仍会经过自动审查器复核）。
- **全段命中才给脱笼候选**：在 `Skip` 分支下，只有当复合命令拆开后的**每一段子命令**都明确命中了 `allow` 放行规则时，结果上才会附带「允许跳过首次沙箱」的候选标志；只要其中混有一段拿不准的命令，就乖乖留在沙箱里。

## 3. 首次沙箱选型与 `deny-read` 保底铁律

走完必要的人工或自动审批后，`ToolOrchestrator` 开始为**第一次执行尝试**（Attempt 1）挑选沙箱环境。它会综合评估文件系统权限、网络开关与底层执行器能力（见[选择首次沙箱](https://github.com/openai/codex/blob/c44deff7b1083e9660ac55d02122481f1cdf139b/codex-rs/core/src/tools/orchestrator.rs#L222-L309)）。

读到这里，一定要点开 `sandboxing.rs` 看一眼[保留禁止读取的限制](https://github.com/openai/codex/blob/c44deff7b1083e9660ac55d02122481f1cdf139b/codex-rs/core/src/tools/sandboxing.rs#L239-L279)：即便上一步 `ExecPolicy` 给某条白名单命令贴了「可跳过首次沙箱」的标签，只要当前生效的文件系统策略里包含禁止读取特定敏感目录的 `deny-read` 规则，**系统就会强行拦住这次绕过，继续启用文件系统沙箱**。原因很直白：白名单只能证明命令本身常见（比如 `cat` 或 `python`），却拦不住参数去读受保护的密钥目录，底线规则绝不能被白名单架空。

## 4. 沙箱拒绝后的二次重判与进程句柄回收

第一次尝试跑完后，编排器站在了整条路径最精妙的分岔口上：

1. **一次成功或普通命令报错**：如果命令顺利跑完，或者只是普通业务逻辑失败（例如测试断言没过、编译器报语法错），直接把输出整理后返回，不再折腾第二次。
2. **明确死于沙箱拦截**（Sandbox Denial）：只有确认是被沙箱挡下时，才进入[判断能否重试](https://github.com/openai/codex/blob/c44deff7b1083e9660ac55d02122481f1cdf139b/codex-rs/core/src/tools/orchestrator.rs#L310-L443)分支。代码会交叉比对当前的审批策略（`Never`、`OnRequest`、`Granular`、`UnlessTrusted` 等）、具体拒绝原因、网络审批状态以及自动审查配置，裁定是就此打住、向用户弹窗申请提权，还是直接进入[安排第二次尝试](https://github.com/openai/codex/blob/c44deff7b1083e9660ac55d02122481f1cdf139b/codex-rs/core/src/tools/orchestrator.rs#L445-L506)。

如果策略不允许重试，或者第二次尝试依然被拒，收尾处的[返回错误结果](https://github.com/openai/codex/blob/c44deff7b1083e9660ac55d02122481f1cdf139b/codex-rs/core/src/tools/handlers/unified_exec/exec_command.rs#L446-L479)还做了一个非常干净的清理细节：正常后台运行或未结束的交互命令可能会给模型返回一个用于后续读输出、写输入的进程会话编号（session / process ID），但**凡是死于沙箱拒绝的调用，只把拒绝说明打包成工具文本结果交回模型，绝不暴露任何可继续交互的进程编号**，彻底掐断模型对着半死会话反复轮询的可能。

把这四步串成一张端到端调用全图：

```text
exec_command(payload)
  │
  ├─► 1. ExecCommandHandler::handle_call
  │       ├─ 校验环境 / TTY / workdir，合并并核查回合权限上限
  │       └─ 若识别为 apply_patch 请求 ──► 分流至专用补丁管线提前返回
  │
  ├─► 2. ExecPolicy 静态与策略定性
  │       └─ 输出 Forbidden | NeedsApproval | Skip（全段命中 allow 才附带可绕过首次沙箱候选位）
  │
  ├─► 3. ToolOrchestrator::run 首次执行（Attempt 1）
  │       ├─ 完成必要的人工审批或自动审查
  │       └─ 选定首次沙箱（若存在 deny-read 限制，强制保留文件系统沙箱）并启动进程
  │
  └─► 4. 结果分流与条件升权（Attempt 2）
          ├─ 成功或普通非零退出码 ──► 原样返回输出给模型修代码
          └─ 沙箱拒绝 ──► 按 Never / OnRequest / Granular / UnlessTrusted 裁决终止或获批重试
                          （若最终仍被沙箱拒绝，返回错误文本且不分配交互进程句柄）
```

## 来源与边界

本文基于官方仓库固定提交 [`openai/codex@c44deff7b1083e9660ac55d02122481f1cdf139b`](https://github.com/openai/codex/tree/c44deff7b1083e9660ac55d02122481f1cdf139b) 中 `codex-rs/core` 的静态源码整理，核对日期 2026-09-23。实际运行时的具体分支走向还受操作系统平台（macOS Seatbelt / Linux Landlock / Windows）、宿主权限配置、远程执行器及网络代理设置共同决定。
