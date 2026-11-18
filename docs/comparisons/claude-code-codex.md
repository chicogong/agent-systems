# Claude Code 与 Codex：同一修复任务如何执行与受控？

[返回横向对照](README.md) · [先读五层职责](../concepts/model-harness-cli-mcp-skill.md) · [Codex 命令路径](../systems/codex/README.md)

很多开发者的终端里同时装着 `claude` 和 `codex`。日常修 Bug 时，你很容易遇到两桩让人困惑的事：

1. 明明在仓库根目录的 `CLAUDE.md` 或 `AGENTS.md` 里白纸黑字写着“可以随便跑单测，严禁运行 `git push`”，为什么跑 `npm test` 时有时还会弹窗求批准，而一旦放开自动批准，单靠那行 Markdown 又拦不住高危命令？
2. 明明开启了本地命令沙箱（Sandbox），以为一切写入都被关进了笼子，结果 Agent 调起工单系统的 MCP 工具时，一个请求就直接改掉了远端线上工单的状态。

问题出在我们把**提示词约定**、**工具审批**、**OS 进程沙箱**和**外部服务权限**混成了一道墙。实际上，无论是 Claude Code 还是 Codex，一次代码修复动作从“模型动念头”到“真正落到机器上”，都要穿过四道职责截然不同的控制关口。

![同一修复任务在 Claude Code 与 Codex 的行动关口对照](../../figures/claude-code-codex/diagram.svg)

[可编辑图源](../../figures/claude-code-codex/scene.excalidraw) · [PNG 预览](../../figures/claude-code-codex/preview.png) · [图的文字版](../../figures/claude-code-codex/README.md)

## 用同一个真实修复场景对齐两边的工作流

拿一个典型的后端缺陷来做切片：订单服务在高并发网络抖动下，客户端重发了带相同幂等键（Idempotency Key）的下单请求，服务没有返回原订单，而是重复创建了两笔订单。

你在终端给助手下达同一条任务指令：

```text
先读项目规范和工单 #731，补一个能稳定失败的幂等回归测试，再修复实现并只跑 orders 模块测试；
不要 git commit 或 git push，最后给我改动摘要和测试输出。
```

假设本地已经配好了读取工单系统的 MCP 服务，以及一份约束“测试驱动修复（先红后绿）”步骤的 Skill。顺着这条工作流走一遍，就能看清两套工具在五个关键节点上的异同：

1. **启动入口与读取项目指令**：交互式终端直接用 `claude` 或 `codex` 启动；写进 CI 脚本或批处理流水线时，两边分别提供非交互入口 [`claude -p`](https://code.claude.com/docs/en/headless) 与 [`codex exec`](https://developers.openai.com/codex/noninteractive)。启动后，Claude Code 将工作目录、Git 状态与 `CLAUDE.md` 纳入上下文，Codex 则按目录层级读取 `AGENTS.md`。**关键体感差异不在文件名，而在边界认知**：这两份文件本质上都是喂给模型的“行事指南（软约束）”，它们能引导模型先写测试、少走弯路，但**绝不会自动赋予或剥夺底层工具的执行权限**。[Claude Code 工作方式](https://code.claude.com/docs/en/how-claude-code-works) · [Codex `AGENTS.md` 指南](https://developers.openai.com/codex/guides/agents-md)
2. **拉取外部工单与按需加载做法**（MCP 与 Skill）：模型通过 MCP 工具拉取 `#731` 工单详情，同时按需读取 TDD Skill 里的测试编写规范。为什么要把 Skill 与 `CLAUDE.md` / `AGENTS.md` 分开？因为项目主指令每轮常驻窗口，塞太多专项流程会白白烧掉上下文预算；Skill 则是“用到这类任务时才翻开的专项手册”。至于 MCP，它能读到哪张工单、能不能改工单状态，完全取决于你给该 MCP Server 配置的凭据与工具许可；如果连接失败，正确的处理是把“工单正文待核对”明确记入交付缺口，而不是靠猜需求硬写代码。[Claude Code MCP](https://code.claude.com/docs/en/mcp) · [Claude Code Skills](https://code.claude.com/docs/en/skills) · [Codex MCP](https://developers.openai.com/codex/mcp) · [Codex Skills](https://developers.openai.com/codex/skills)
3. **模型提出工具动作提案**：拿到复现条件后，模型依次提议搜索代码、修改测试文件、执行 `npm test -- orders`。在 Claude Code 官方文档中，这一闭环被归纳为“收集上下文 → 采取行动 → 验证结果”；而在 Codex 的开源 Rust 核心里，一条 Shell 命令提案会精确进入 `exec_command` 通道：先由 Handler 解析参数，再交给 Unified Exec 查询策略判定，最后由 `ToolOrchestrator`（执行编排器）串联审批与沙箱运行。[Claude Code 循环](https://code.claude.com/docs/en/how-claude-code-works) · [Codex 代码导读](../systems/codex/code-walkthrough.md)
4. **过审批闸口与进 OS 沙箱执行**：这是日常实操体感差异最明显的一步！
   - 在 **Claude Code** 中，当前权限模式、`allow / ask / deny` 规则、可选 Hook 与沙箱开关共同决定命令命运。为什么很多人开了沙箱后觉得弹窗变少了？因为启用沙箱且 `autoAllowBashIfSandboxed` 生效时，系统用“OS 级文件系统与网络隔离”兜住了爆炸半径，从而省掉一部分笼统的整工具 Bash 询问；但针对特定高危命令内容的 `ask` 规则和显式 `deny` 黑名单依然生效，绝不会被沙箱开关绕过。
   - 在 **Codex** 的固定源码路径中，策略层先对普通命令给出三选一裁决：`Skip`（免除常规人工询问）、`NeedsApproval`（挂起请求你拍板）或 `Forbidden`（直接拦截拒绝）。**注意 `Skip` 跳过的只是人工弹窗，不是沙箱隔离**——获准放行后，`ToolOrchestrator` 依然会为进程挑选首次执行沙箱；只有当首次运行因沙箱限制失败且满足严格重试条件时，才会进入受控的升级询问或二次尝试分支。[Claude Code 权限与沙箱交互](https://code.claude.com/docs/en/permissions#how-permissions-interact-with-sandboxing) · [Codex 策略映射](https://github.com/openai/codex/blob/c44deff7b1083e9660ac55d02122481f1cdf139b/codex-rs/core/src/exec_policy.rs#L394-L460) · [Codex 编排器执行](https://github.com/openai/codex/blob/c44deff7b1083e9660ac55d02122481f1cdf139b/codex-rs/core/src/tools/orchestrator.rs#L151-L309)
5. **依据测试回执迭代并收口交付**：第一次跑 `npm test -- orders` 应当如期失败（证明回归测试真能抓到重复建单 Bug），改完幂等校验逻辑后再跑一次应当变绿。最终交付物不是一句“修好了”，而是工作区真实 diff、测试命令原始输出，以及“未执行 `commit` / `push`、远端工单未改动”的边界确认。

## 一张表对齐两边的控制边界

| 核心控制问题 | Claude Code（基于官方文档公开行为） | Codex（基于固定 Rust 源码与官方文档） |
| --- | --- | --- |
| **项目级指令写在哪** | `CLAUDE.md`；随工作目录与会话加载为指令上下文 | `AGENTS.md`；按目录规则加载为指令上下文，同样不自动授予底层工具权限 |
| **命令什么时候弹窗或被拦** | 由权限模式、`allow / ask / deny` 规则、Hook 与沙箱配置联合裁决；沙箱模式下可减少常规 Bash 整工具询问，显式 `deny` 始终兜底 | 普通 `exec_command` 经 `exec_policy` 判出 `Forbidden`（拒止）、`NeedsApproval`（求批）或 `Skip`（免询），再交 `ToolOrchestrator` 执行 |
| **沙箱到底关住了谁** | Sandboxed Bash 对本地 Shell 命令及其子进程施加文件系统与网络访问限制，**不覆盖非 Bash 的外部工具通道** | 审批与沙箱分步决策：获准后先在选定沙箱内执行首次尝试，受限失败后按条件决定是否升级或重试 |
| **Skill 与 MCP 如何分工** | Skill 提供按需读取的任务做法说明；MCP 接入外部服务工具，受连接身份与工具权限控制 | 同样在产品层分别支持 Skills 与 MCP（独立于上述 `exec_command` 本地命令调用栈） |
| **长任务怎么防丢约束** | 会话支持保存续接，长上下文会自动压缩（compaction），早期口头细节可能被概括稀释 | 官方提供[长周期任务实践说明](https://developers.openai.com/blog/run-long-horizon-tasks-with-codex)；高危红线同样不能只靠早期对话口头叮嘱 |

## 开发者最容易踩的三个实战误区

### 误区一：把“开了本地沙箱”当成“所有工具都安全了”

审批和沙箱回答的是两个正交问题：**审批管这次调用准不准发出去，沙箱管拉起来的本地子进程能碰哪些目录和端口**。来看下面两条动作在宿主里的真实流向：

```text
动作 A: bash("npm test -- orders")
  ──► 经过审批规则 ──► 拉起本地子进程 ──► 受 OS 文件读写围栏与禁网沙箱约束

动作 B: mcp__tickets__close_issue(id=731)
  ──► 经过 MCP 工具权限检查 ──► 由宿主向远端 API 发起请求 ──► 绕开本地 Bash 沙箱直接改写线上数据！
```

无论是 Claude Code 文档对工具权限与 Bash 沙箱的区分，还是 Codex 在策略放行后单独为 `exec_command` 选择首次沙箱，都印证了同一条铁律：**本地 Shell 沙箱防不住拥有写权限的远端 MCP 连接**。外部写工具必须单独配置 ask 确认或只读 Token。[Claude Code 权限边界](https://code.claude.com/docs/en/permissions#how-permissions-interact-with-sandboxing) · [Codex 首次沙箱选择](https://github.com/openai/codex/blob/c44deff7b1083e9660ac55d02122481f1cdf139b/codex-rs/core/src/tools/orchestrator.rs#L222-L309)

### 误区二：命令跑失败了，分不清是“代码 Bug”还是“沙箱拦路”

测试命令返回非零退出码时，最忌讳不看原因盲目重试。如果是断言失败，说明业务逻辑没修对，应该把报错喂回模型接着改代码；如果是沙箱禁网或只读目录拦截（例如测试试图连接外部测试库或写临时锁文件），改业务代码毫无意义。在 Codex 源码里，编排器专门在首次执行后检查失败是否源于沙箱限制，并按策略决定是直接返回错误、弹窗请求无沙箱重试，还是终止尝试。[Codex 重试分支](https://github.com/openai/codex/blob/c44deff7b1083e9660ac55d02122481f1cdf139b/codex-rs/core/src/tools/orchestrator.rs#L310-L506)

### 误区三：长会话聊久了，把“禁止推送”只写在第一轮提问里

修一个复杂幂等 Bug 往往要来回跑十几轮搜索和单测。正如 [Claude Code 工作方式文档](https://code.claude.com/docs/en/how-claude-code-works)所说明的，长上下文触发自动压缩后，第一轮顺口提过的附加条件很可能在摘要里被弱化。真正稳妥的工程习惯是两手抓：**把长期规范写进 `CLAUDE.md` / `AGENTS.md`，同时把 `git push` 或生产写操作写进权限配置的 `ask` / `deny` 硬规则里**。

## 源码与文档深读入口

想顺着[五层职责模型](../concepts/model-harness-cli-mcp-skill.md)继续深挖源码与官方接口，可以沿两条主线对照阅读：

- **Codex Rust 核心主线**：从 [`ExecCommandHandler::handle_call`](https://github.com/openai/codex/blob/c44deff7b1083e9660ac55d02122481f1cdf139b/codex-rs/core/src/tools/handlers/unified_exec/exec_command.rs#L170-L245) 切入，依次追踪 [`UnifiedExecProcessManager::open_session_with_sandbox`](https://github.com/openai/codex/blob/c44deff7b1083e9660ac55d02122481f1cdf139b/codex-rs/core/src/unified_exec/process_manager.rs#L1435-L1535)、[`exec_policy` 策略求值](https://github.com/openai/codex/blob/c44deff7b1083e9660ac55d02122481f1cdf139b/codex-rs/core/src/exec_policy.rs#L394-L460)与 [`ToolOrchestrator::run`](https://github.com/openai/codex/blob/c44deff7b1083e9660ac55d02122481f1cdf139b/codex-rs/core/src/tools/orchestrator.rs#L116-L220)，完整串联可配读 [Codex 逐步代码导读](../systems/codex/code-walkthrough.md)。
- **Claude Code 官方文档主线**：依次对照[工作方式](https://code.claude.com/docs/en/how-claude-code-works)、[权限规则](https://code.claude.com/docs/en/permissions)、[沙箱机制](https://code.claude.com/docs/en/sandboxing)、[MCP 集成](https://code.claude.com/docs/en/mcp)与 [Skills 配置](https://code.claude.com/docs/en/skills)，重点核对当前配置下“哪类动作免询、哪类动作弹窗、哪类子进程受沙箱隔离”。

## 来源与边界

本文于 2026-09-23 核对，两边证据粒度不同，阅读时需注意各自边界：

- **Codex**：命令执行、审批与沙箱编排依据官方开源仓库固定提交 [`openai/codex@c44deff7b1083e9660ac55d02122481f1cdf139b`](https://github.com/openai/codex/tree/c44deff7b1083e9660ac55d02122481f1cdf139b) 的 Rust `core` 源码（`apply_patch` 专用补丁通道及各操作系统底层沙箱原语需另行查阅），CLI、Skills 与 MCP 用法结合官方文档。
- **Claude Code**：因其核心 Harness 未以同等粒度开源，本文严格依据官方公开产品文档描述外部可配置与可观察行为，不反推或猜测未公开的内部函数与提示词结构。两边未做同一缺陷仓库下的耗时或修复成功率跑分对比。
