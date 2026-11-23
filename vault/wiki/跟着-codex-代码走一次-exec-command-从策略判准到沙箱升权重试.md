# 跟着 Codex 代码走一次 `exec_command`：从策略判准到沙箱升权重试

> Synthesized concept page maintained by Aimake LLM Wiki.

## Key Evidence & Provenance

### Source Snapshot (2026-11-22)
- **Origin**: `/Users/haorangong/Github/chicogong/experiments/agent-systems/docs/systems/codex/code-walkthrough.md`
- **SHA-256**: `39e90f4d7cade226` · Raw: [[../raw/2026-11-22-跟着-codex-代码走一次-exec-command-从策略判准到沙箱升权重试.md|2026-11-22-跟着-codex-代码走一次-exec-command-从策略判准到沙箱升权重试.md]]
- 大模型递过来一句 shell 命令时，最粗糙的实现只需五行 `Command::new("sh").arg("-c")`；而在生产级编码 Agent 里，这句命令在真正 fork 出操作系统子进程前，必须闯过参数体检、回合权限合并、复合命令拆解、首次沙箱选型和撞墙升权裁决五道关卡。
- 下面我们锁定 `codex-rs/core` 的固定提交，顺着一条普通 `exec_command` 工具调用的生命周期，逐段拆解这五道关卡为什么要这样写。
- 工具调用的第一站是 `ExecCommandHandler::handle_call`。在接触任何进程管理器之前，它先对请求载荷做严格的前置体检：解析命令参数、核对当前运行环境是否支持统一执行、检查伪终端（TTY）标志是否合法，并验证工作目录 `workdir` 是否有效；任何一项不合规都会在创建进程前直接折返为模型可读的工具错误（见接收并检查请求）。
- 紧接着是一步很容易被忽略的**权限天花板校验**：模型有时会在工具参数里主动通过 `sandbox_permissions` 伸手讨要更高权限。Handler 会把本次申请的权限与当前回合已获授的权限合并，对照当前会话策略做检查——如果宿主策略压根禁止模型主动讨要额外权限，请求当场就会被驳回，连后面的审批编排器都进不去（见执行前检查权限）。
- 这里还有一个专门的分流口：如果模型没有调专门的改文件工具，而是试图在 `exec_command` 的命令行里调用 `apply_patch` 打补丁，处理器会识别出这类请求并直接转交专用补丁路径做细粒度文件变更审查与落盘，提前返回，避免让结构化的代码修改混同于黑盒 shell 脚本。
