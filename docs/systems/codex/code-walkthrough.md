# 跟着 Codex 代码走一次 `exec_command`

[返回 Codex 首篇](README.md) · [固定源码](https://github.com/openai/codex/tree/c44deff7b1083e9660ac55d02122481f1cdf139b)

以下是源码**逻辑摘要**，并非原项目源码复制。不同平台、权限配置、远程 executor、网络代理和严格自动审查会改变分支；不要把下列单一路径当作所有部署的运行保证。

1. `ExecCommandHandler::handle_call` 只接受函数型 payload，解析执行环境、`workdir` 与参数；不支持的环境、TTY 配置或不合法路径会在进程创建前返回面向模型的错误。[payload 与环境](https://github.com/openai/codex/blob/c44deff7b1083e9660ac55d02122481f1cdf139b/codex-rs/core/src/tools/handlers/unified_exec/exec_command.rs#L170-L245)
2. Handler 将请求权限与已经授予的 turn 权限合并，再验证 `sandbox_permissions` 与额外权限。若策略不允许提出提权审批，直接拒绝，而不是先尝试执行。[权限预处理](https://github.com/openai/codex/blob/c44deff7b1083e9660ac55d02122481f1cdf139b/codex-rs/core/src/tools/handlers/unified_exec/exec_command.rs#L322-L376)
3. 特殊情形：若命令被识别为 `apply_patch`，Handler 可转到专门的 patch 路径并提前返回；本篇图解的是未走这个拦截分支的普通命令。[patch 拦截](https://github.com/openai/codex/blob/c44deff7b1083e9660ac55d02122481f1cdf139b/codex-rs/core/src/tools/handlers/unified_exec/exec_command.rs#L378-L405)
4. `UnifiedExecProcessManager::open_session_with_sandbox` 调用 exec policy，构造 `ExecApprovalRequirement`，再交给 `ToolOrchestrator::run`。[策略接线](https://github.com/openai/codex/blob/c44deff7b1083e9660ac55d02122481f1cdf139b/codex-rs/core/src/unified_exec/process_manager.rs#L1477-L1535)
5. exec policy 将命令匹配结果映射为 `Forbidden`、`NeedsApproval` 或 `Skip`。需要询问但当前审批策略禁用询问时，也会变为 `Forbidden`。`Skip` 仅当每段命令都被显式 allow 规则命中时，才带有可绕过沙箱的标志。[策略映射](https://github.com/openai/codex/blob/c44deff7b1083e9660ac55d02122481f1cdf139b/codex-rs/core/src/exec_policy.rs#L394-L460)
6. `ToolOrchestrator` 对 `Forbidden` 返回拒绝；对 `NeedsApproval` 发起请求；对 `Skip` 跳过普通询问，但严格自动审查模式还有额外审查。随后结合文件系统、网络与 executor 能力选择第一次尝试的沙箱。deny-read 限制阻止简单地绕过文件系统沙箱。[审批](https://github.com/openai/codex/blob/c44deff7b1083e9660ac55d02122481f1cdf139b/codex-rs/core/src/tools/orchestrator.rs#L151-L220) · [首次沙箱](https://github.com/openai/codex/blob/c44deff7b1083e9660ac55d02122481f1cdf139b/codex-rs/core/src/tools/orchestrator.rs#L222-L309) · [deny-read 约束](https://github.com/openai/codex/blob/c44deff7b1083e9660ac55d02122481f1cdf139b/codex-rs/core/src/tools/sandboxing.rs#L239-L279)
7. 第一次尝试成功即返回；只有符合特定条件的沙箱拒绝才进入重试判断。代码对 `Never`、`OnRequest`、Granular、`UnlessTrusted`、网络审批与严格自动审查分别设限；可能终止、再次请求批准或进行第二次尝试。把“沙箱失败→总会提权重试”画成固定箭头是错的。[拒绝与重试条件](https://github.com/openai/codex/blob/c44deff7b1083e9660ac55d02122481f1cdf139b/codex-rs/core/src/tools/orchestrator.rs#L310-L443) · [第二次尝试](https://github.com/openai/codex/blob/c44deff7b1083e9660ac55d02122481f1cdf139b/codex-rs/core/src/tools/orchestrator.rs#L445-L506)
8. 若仍是 sandbox denial，`exec_command` 将拒绝输出转成工具结果，注明没有可继续写入的进程；其他错误会转换成面向模型的失败。[错误返回](https://github.com/openai/codex/blob/c44deff7b1083e9660ac55d02122481f1cdf139b/codex-rs/core/src/tools/handlers/unified_exec/exec_command.rs#L446-L479)

可将主干概括成：

```text
exec_command(payload)
  → Handler：环境与权限预处理
  → ExecPolicy：Skip / NeedsApproval / Forbidden
  → Orchestrator：必要审批 → 选择沙箱 → 第一次尝试
  → 成功返回；若是沙箱拒绝，再按策略判断终止或有条件重试
```

### 证据与未知

以上为官方仓库固定提交的静态源码事实和对控制流的简化。我们**没有**运行该提交、检查 Linux/macOS/Windows 实际沙箱后端，也没有验证桌面 App、CLI 和远程 executor 之间的行为等价性。命令分类的误报/漏报、用户审批体验、网络代理的实际隔离效果以及长期进程恢复，均留待独立实验。不能用本篇推断 Codex 的默认安全保证或性能。
