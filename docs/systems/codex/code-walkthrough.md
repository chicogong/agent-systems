# 跟着 Codex 代码走一次 `exec_command`

[返回 Codex 首篇](README.md) · [固定源码](https://github.com/openai/codex/tree/c44deff7b1083e9660ac55d02122481f1cdf139b)

模型要求运行一条测试命令时，Codex 要先回答三件事：请求写得是否正确、是否允许执行、在哪种环境里执行。下面按固定版本中的普通 `exec_command` 路径找到对应代码。

## 1. 收到请求，核对环境和参数

`ExecCommandHandler::handle_call` 是接收工具请求的处理函数。它接受函数调用形式的输入，解析命令参数、执行环境和工作目录 `workdir`。环境不受支持、终端（TTY）配置不合要求或路径无效时，会在创建进程前把错误交回模型。[接收并检查请求](https://github.com/openai/codex/blob/c44deff7b1083e9660ac55d02122481f1cdf139b/codex-rs/core/src/tools/handlers/unified_exec/exec_command.rs#L170-L245)

接着，它合并这次请求的权限和当前回合已经授予的权限，再检查 `sandbox_permissions` 等设置。如果当前策略禁止申请更大权限，请求会在这里被拒绝。[执行前检查权限](https://github.com/openai/codex/blob/c44deff7b1083e9660ac55d02122481f1cdf139b/codex-rs/core/src/tools/handlers/unified_exec/exec_command.rs#L322-L376)

`apply_patch` 是一个特殊情况：识别到这类改文件请求时，处理器可以交给专用的补丁处理流程，并提前返回。下文继续看普通命令。[专用补丁路径](https://github.com/openai/codex/blob/c44deff7b1083e9660ac55d02122481f1cdf139b/codex-rs/core/src/tools/handlers/unified_exec/exec_command.rs#L378-L405)

## 2. 决定直接继续、先批准，还是拒绝

`UnifiedExecProcessManager::open_session_with_sandbox` 把命令交给执行策略，得到 `ExecApprovalRequirement`，也就是“这次是否需要审批”的决定，再调用 `ToolOrchestrator::run` 安排后续流程。[交给策略和编排器](https://github.com/openai/codex/blob/c44deff7b1083e9660ac55d02122481f1cdf139b/codex-rs/core/src/unified_exec/process_manager.rs#L1477-L1535)

三个决定分别是：

- `Forbidden`：拒绝执行。需要询问、但当前策略禁用询问时，也会得到这个决定。
- `NeedsApproval`：先发起审批请求，通过后继续。
- `Skip`：跳过普通询问。严格自动审查模式还会加一层审查。

`Skip` 请求只有在每段命令都命中明确的 allow（允许）规则时，才会附带可跳过沙箱的标志。后面选择环境时，还要检查其他限制。[生成审批决定](https://github.com/openai/codex/blob/c44deff7b1083e9660ac55d02122481f1cdf139b/codex-rs/core/src/exec_policy.rs#L394-L460) · [执行审批决定](https://github.com/openai/codex/blob/c44deff7b1083e9660ac55d02122481f1cdf139b/codex-rs/core/src/tools/orchestrator.rs#L151-L220)

## 3. 选择环境，运行第一次

通过前面的检查后，编排器结合文件系统权限、网络设置和执行器（executor）的能力，选择第一次尝试的沙箱。禁止读取指定文件的 deny-read 限制会阻止直接绕过文件系统沙箱。[选择首次沙箱](https://github.com/openai/codex/blob/c44deff7b1083e9660ac55d02122481f1cdf139b/codex-rs/core/src/tools/orchestrator.rs#L222-L309) · [保留禁止读取的限制](https://github.com/openai/codex/blob/c44deff7b1083e9660ac55d02122481f1cdf139b/codex-rs/core/src/tools/sandboxing.rs#L239-L279)

第一次尝试成功，就返回结果。沙箱拒绝则进入专门的判断：根据当前审批策略、拒绝原因、网络审批和自动审查配置，决定停下、再次请求批准，还是进行第二次尝试。`Never`、`OnRequest`、`Granular`、`UnlessTrusted` 等策略的分支可以在源码中分别查看。[判断能否重试](https://github.com/openai/codex/blob/c44deff7b1083e9660ac55d02122481f1cdf139b/codex-rs/core/src/tools/orchestrator.rs#L310-L443) · [安排第二次尝试](https://github.com/openai/codex/blob/c44deff7b1083e9660ac55d02122481f1cdf139b/codex-rs/core/src/tools/orchestrator.rs#L445-L506)

仍被沙箱拒绝时，`exec_command` 会把拒绝信息整理成工具结果，不返回可供后续交互的进程编号。其他错误也会转换成模型能收到的失败信息。[返回错误结果](https://github.com/openai/codex/blob/c44deff7b1083e9660ac55d02122481f1cdf139b/codex-rs/core/src/tools/handlers/unified_exec/exec_command.rs#L446-L479)

可将主干概括成：

```text
exec_command(payload)
  → Handler：环境与权限预处理
  → ExecPolicy：Skip / NeedsApproval / Forbidden
  → Orchestrator：必要审批 → 选择沙箱 → 第一次尝试
  → 成功返回；若是沙箱拒绝，再按策略判断终止或有条件重试
```

## 阅读范围

以上是固定版本 Rust core 普通命令路径的静态源码摘要。实际分支还受平台、权限配置、远程执行器和网络代理影响。本篇尚未运行这个提交；桌面 App、命令行和远程环境的审批体验、实际隔离与长期进程恢复，需要分别做运行检查。
