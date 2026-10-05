# 执行系统源码与讲解复核（2026-10-05）

本轮通读 Pi、DSH、Codex、OpenCode、mini-SWE-agent、OpenHands、Browser Use、Qwen Code 八个目录的 17 篇 Markdown，按[来源台账](../../sources/systems.json)重新取得固定提交源码，重点检查正常路径、停止/错误分支和宿主授权责任。先修正可定位的讲解歧义，再按用户追加要求实质改写全部 17 篇的中文讲法。不更换上游版本、不启动这些 Agent、不把源码核对标作运行或读者验收。

## 核对结果摘要

事实复核已修正七类问题，涉及八篇正文：观察消息格式化与模型请求的区别；完成哨兵的空白归一化；OpenCode 调用状态数量；Qwen 权限检查的措辞；Browser Use 的截图条件与任务结束标志；OpenHands 再运行的隐式确认；DSH 批次结束意图的汇总边界。Pi 与 Codex 所抽查的核心分支未发现需要改动的事实问题；两者仍参与了后续写作风格改稿。

这些结论只覆盖下面列出的源码切面，并不代表八个项目的全部功能、所有正文断言或部署安全已经审计。

## Pi：循环、工具批次与按需指令

- 已读正文：首页、代码导读、Extension／Skill／Package 说明。
- 正常路径：`prompt()` 拒绝正在运行时的第二次 prompt；loop 在模型请求前变换上下文，工具准备与执行/后置钩子分开。并行工具结果经 `Promise.all` 按原调用顺序交回。[入口](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/agent/src/agent.ts#L367-L442) · [工具批次](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/agent/src/agent-loop.ts#L505-L657)
- 停止边界：批次中已完成结果必须全部带 `terminate: true` 才汇总为终止；`finishTurn=end` 直接结束，自然结束点才检查 follow-up。[批次终止](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/agent/src/agent-loop.ts#L685-L687) · [结束优先级](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/agent/src/agent-loop.ts#L279-L320)
- 可见性：Skill 列表只含名称、描述与位置；`disable-model-invocation` 过滤模型提示，显式 `/skill:name` 仍读取正文。会话原始条目与模型投影不是一份视图。[Skill 提示](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/coding-agent/src/core/skills.ts#L347-L382) · [显式展开](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/coding-agent/src/core/agent-session.ts#L1792-L1821) · [上下文投影](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/coding-agent/src/core/session-manager.ts#L543-L582)
- 事实修正：无；表达改稿覆盖三篇，详见文末。未知：本轮未安装第三方 Extension、跨 provider 运行、故障注入或验证实际权限隔离。

## DSH：有界批次与审批接缝

- 已读正文：首页、代码导读。
- 正常路径：prepare 按序推进，dispatch 可以重叠；`commitReady()` 只推进连续 ready 槽，后完成/前提交的关系不约束远端副作用次序。[批次调度](https://github.com/deepseek-ai/deepseek-harness/blob/477b4f420553e8a52c2fbccc464d7561b239c443/packages/core/agent-loop/src/tool-calls.ts#L122-L242)
- 授权边界：pre-execute 默认 allow，但 ask 无审批服务、无 Agent 或不可用时拒绝；guard 在 allow 后仍可拒绝。`danger-full-access` 跳过 confine，其他路径的 runner failure 不降级为普通执行。[准备](https://github.com/deepseek-ai/deepseek-harness/blob/477b4f420553e8a52c2fbccc464d7561b239c443/packages/core/tools/src/index.ts#L1489-L1539) · [询问](https://github.com/deepseek-ai/deepseek-harness/blob/477b4f420553e8a52c2fbccc464d7561b239c443/packages/core/tools/src/index.ts#L1727-L1767) · [执行器](https://github.com/deepseek-ai/deepseek-harness/blob/477b4f420553e8a52c2fbccc464d7561b239c443/packages/shell/bash-sandbox/src/index.ts#L85-L133)
- 修改：说明 `concludesTurn` 是汇总后返回上层的结束意图，本身不立刻截断剩余批次。[汇总与返回](https://github.com/deepseek-ai/deepseek-harness/blob/477b4f420553e8a52c2fbccc464d7561b239c443/packages/core/agent-loop/src/tool-calls.ts#L83-L159)
- 未验证：实际插件组合、操作系统 confine backend、取消后远端对账及安全审计。

## Codex：审批与沙箱不是一个开关

- 已读正文：首页、`exec_command` 代码导读。
- 正常路径：命令判定映射为 `Forbidden / NeedsApproval / Skip`；`Skip.bypass_sandbox` 仅在全部命令段命中显式 allow 时成立，deny-read 又会阻止绕过文件系统沙箱。[策略映射](https://github.com/openai/codex/blob/c44deff7b1083e9660ac55d02122481f1cdf139b/codex-rs/core/src/exec_policy.rs#L394-L460) · [首次沙箱约束](https://github.com/openai/codex/blob/c44deff7b1083e9660ac55d02122481f1cdf139b/codex-rs/core/src/tools/sandboxing.rs#L239-L279)
- 错误边界：非 sandbox denial 直接传播；符合拒绝类型、策略、网络审批与提权条件才进入第二次尝试；严格自动审查不复用第一次审查来放行无沙箱重试。[编排与重试](https://github.com/openai/codex/blob/c44deff7b1083e9660ac55d02122481f1cdf139b/codex-rs/core/src/tools/orchestrator.rs#L310-L506)
- 当前官方文档也已搜索并打开[命令执行审批说明](https://learn.chatgpt.com/docs/app-server#command-execution-approvals)，只用于区分客户端审批协议与固定源码；不以当前文档证明旧提交的实现。
- 事实修正：无；表达改稿覆盖两篇，详见文末。未知：桌面、CLI、远程 executor 的等价性与各平台沙箱实际效果仍未运行验证。

## OpenCode：调用状态与执行钩子

- 已读正文：首页、代码导读。
- 正常路径：输入事件创建 pending；完整 tool-call 更新 running；结果只收束匹配且仍为 running 的 part。普通成功/错误分支与 cleanup 的中断错误分开。[创建与收束](https://github.com/anomalyco/opencode/blob/18ef3cc7c5a25b82114c953a80ccc09f4988f74e/packages/opencode/src/session/processor.ts#L160-L253) · [调用与结果](https://github.com/anomalyco/opencode/blob/18ef3cc7c5a25b82114c953a80ccc09f4988f74e/packages/opencode/src/session/processor.ts#L315-L420) · [清理](https://github.com/anomalyco/opencode/blob/18ef3cc7c5a25b82114c953a80ccc09f4988f74e/packages/opencode/src/session/processor.ts#L585-L610)
- 工具包装：前置插件钩子、实际 execute、后置钩子是正常执行路径，与 part 的生命周期状态不是同一层。[包装](https://github.com/anomalyco/opencode/blob/18ef3cc7c5a25b82114c953a80ccc09f4988f74e/packages/opencode/src/session/tools.ts#L92-L132)
- 修改：把误写的“ToolPart 三个状态”改为明确的四个状态名称。未知：provider 事件日志、MCP/插件权限与中断恢复未实测。

## mini-SWE-agent：停止消息与观察适配器

- 已读正文：首页、代码导读。
- 正常与停止：`query()` 请求模型，动作交给环境；每轮 finally 保存；`exit` 尾消息结束，普通异常记录后重新抛出。LocalEnvironment 归一化输出开头/首行空白后，才匹配完成哨兵及返回码 0。[循环](https://github.com/SWE-agent/mini-swe-agent/blob/04d809ceab9df28f9adaed044884180159172930/src/minisweagent/agents/default.py#L88-L157) · [提交条件](https://github.com/SWE-agent/mini-swe-agent/blob/04d809ceab9df28f9adaed044884180159172930/src/minisweagent/environments/local.py#L24-L56)
- 观察消息：`LitellmModel.format_observation_messages()` 调用格式化辅助函数，而不是 `litellm.completion`；新的模型请求发生在后续 query。[适配器](https://github.com/SWE-agent/mini-swe-agent/blob/04d809ceab9df28f9adaed044884180159172930/src/minisweagent/models/litellm_model.py#L140-L151)
- 修改：澄清格式化不是再次生成；补准哨兵的空白处理。未知：交互子类、成本/时间计数效果、本地进程隔离与故障恢复未实测。

## OpenHands：事件先记录、宿主再确认

- 已读正文：首页、代码导读。
- 正常路径：ActionEvent 先发出，随后检查确认；默认回调 append_event 后才通知外部订阅。待确认时 run 停止；再次 run 先从当前分支取未匹配动作，再执行而非先采样。[回调](https://github.com/OpenHands/software-agent-sdk/blob/6ebd820d10794f1b52bb06ef6c19512888a1401b/openhands-sdk/openhands/sdk/conversation/impl/local_conversation.py#L415-L468) · [确认顺序](https://github.com/OpenHands/software-agent-sdk/blob/6ebd820d10794f1b52bb06ef6c19512888a1401b/openhands-sdk/openhands/sdk/agent/response_dispatch.py#L163-L190) · [未匹配动作](https://github.com/OpenHands/software-agent-sdk/blob/6ebd820d10794f1b52bb06ef6c19512888a1401b/openhands-sdk/openhands/sdk/agent/agent.py#L645-L661)
- 停止边界：waiting、预算、迭代数等是会话运行状态；stop hook 也可把 FINISHED 改回 RUNNING。不能把状态或事件记录等同于外部动作已验收。[外围停止](https://github.com/OpenHands/software-agent-sdk/blob/6ebd820d10794f1b52bb06ef6c19512888a1401b/openhands-sdk/openhands/sdk/conversation/impl/local_conversation.py#L1933-L2059)
- 修改：明确再次 run 是该同步路径的隐式批准，宿主应先获得授权；SDK 在此处不另验一份新的批准凭据。[清除等待态](https://github.com/OpenHands/software-agent-sdk/blob/6ebd820d10794f1b52bb06ef6c19512888a1401b/openhands-sdk/openhands/sdk/conversation/impl/local_conversation.py#L1977-L1995)
- 未验证：实际用户确认界面、磁盘崩溃恢复、恰好一次副作用及 workspace 隔离。

## Browser Use：捕获、可见、留痕分开

- 已读正文：首页、代码导读。
- 正常路径：step 在上下文准备后清除上一轮输出/结果；请求状态时要求截图，但消息管理器仍按 True/False/auto 及截图是否存在决定发送。历史也有独立条件，保存的摘要不是动作后新抓取的完整页面。[step 与捕获](https://github.com/browser-use/browser-use/blob/d8110c5ff87ccba887aaa726cdb780f2f84bef8d/browser_use/agent/service.py#L1033-L1160) · [截图条件](https://github.com/browser-use/browser-use/blob/d8110c5ff87ccba887aaa726cdb780f2f84bef8d/browser_use/agent/message_manager/service.py#L449-L502) · [留痕条件](https://github.com/browser-use/browser-use/blob/d8110c5ff87ccba887aaa726cdb780f2f84bef8d/browser_use/agent/service.py#L1356-L1415)
- 错误/停止：状态超时清除旧 selector 路径；multi_act 在任务已结束、结果出错、终止序列标志或页面/焦点变化时停止余下动作。[超时](https://github.com/browser-use/browser-use/blob/d8110c5ff87ccba887aaa726cdb780f2f84bef8d/browser_use/browser/session.py#L1616-L1679) · [序列守卫](https://github.com/browser-use/browser-use/blob/d8110c5ff87ccba887aaa726cdb780f2f84bef8d/browser_use/agent/service.py#L2730-L2828)
- 修改：补充截图三种模式，区分普通动作完成与 `is_done` 的任务结束。未知：真实浏览器观测、模型截图输入、截图存储与页面变化检测时延未实测。

## Qwen Code：发现不等于声明刷新或获准执行

- 已读正文：首页、代码导读。
- 可见性：getFunctionDeclarations 过滤隐藏 deferred 工具；tool_search 返回 schema 文本，不因此 reveal 目标；显式可见、预加载、会话 reveal 等另走分支。[声明过滤](https://github.com/QwenLM/qwen-code/blob/b9840886b86c23f196482cc1ee55d59cbc74df87/packages/core/src/tools/tool-registry.ts#L835-L974) · [schema 返回](https://github.com/QwenLM/qwen-code/blob/b9840886b86c23f196482cc1ee55d59cbc74df87/packages/core/src/tools/tool-search.ts#L295-L411)
- 执行边界：桥校验目标、上下文、隐藏状态与完整桥；scheduler 改写真实目标前检查 allowlist/blocklist，wrapper execute 本身拒绝直接执行。[解析与拒绝](https://github.com/QwenLM/qwen-code/blob/b9840886b86c23f196482cc1ee55d59cbc74df87/packages/core/src/tools/tool-call.ts#L60-L230) · [目标改写](https://github.com/QwenLM/qwen-code/blob/b9840886b86c23f196482cc1ee55d59cbc74df87/packages/core/src/core/coreToolScheduler.ts#L2645-L2729)
- 修改：把“执行后的权限、审批”改成“后续执行路径中的权限、审批”，避免被读成先执行再授权。未知：模型搜索习惯、token 节省量、MCP 重连及实际审批/hook 顺序未实测。

## 本地校验与后续交接

- `python3 scripts/check_sources.py`：16 个系统文章的固定版本台账一致性通过；此脚本不证明上述源码断言。
- 本轮自有正文 `git diff --check` 通过；未修改脚本、图源、版本台账、书序或导出物。
- 白话改稿后重新运行 `check_sources.py` 与 `check_repo.py`，均通过。按文件对照改稿前后的 208 个去重外链目标，零删除、零新增；所有原固定来源仍在原文章中。这些检查只验证台账、链接和仓库结构，不替代运行与读者检查。
- 图意交接：全册 QA 应特别核对 Browser Use 的 `is_done`、OpenHands 的宿主确认，以及 mini-SWE-agent 的哨兵表达。增加正文解释不等于重新验收交互画布或 PDF。
- 发布合稿应重新构建网站、Markdown 包及 PDF，并在实际产物上检查增补段落的分页、字号和链接。真实读者试读、运行故障实验和印前权益仍是独立门槛。

## 白话写作改稿范围

用户要求“用大白话讲，而不是各种反文句”后，本轮对八个系统目录的全部 17 篇实质改稿：八篇首页、八篇源码导读，以及 Pi 的扩展说明。改稿保留原有图引用、固定版本和源码外链，不修改图源与导出脚本。

- 首页先讲具体任务或直接说明分工：读文件、执行测试、多个工具协作、网页观察、按需找工具说明。源码作为可选延伸，完整版本说明放入范围说明；Pi、DSH、Browser Use 已按独立 QA 建议移至篇末。
- 导读改用“谁接收、谁检查、谁执行、结果放回哪一轮”的动作表达；把长串函数和断言拆成可跟读的短段落。工具结果、事件、钩子、延迟工具、执行器等首次出现时加中文说明。
- 保留关键执行条件：OpenHands 宿主先取得批准再调用 run；DSH ask 无审批服务拒绝；Codex 必要审批通过后执行；Qwen 按真实目标检查权限。将一般范围提醒收至文末，减少每段“不能证明／不等于”的防御性句子。
- 保留已经核实的细节：Pi 并行结果按调用顺序写入；DSH concludesTurn 汇总后交上层；mini 的格式化不增加模型请求；Browser 的历史截图与模型图片输入分别检查。Browser 标题按实际跳转/错误条件收窄，避免泛称所有页面变化都能发现。
- DSH 的 Cordis、profile、bundle、sdk-minimal 补为插件框架、配置方案、组合包和精简 SDK。报告本身仍保留核对用的技术表达，属于维护记录，不作为入门正文。

这次改稿是 AI 编辑和源码交叉检查，不是非作者真人试读或学习效果验证。先前追加的独立教学交叉审查已按任务优先级暂停，未将其写成通过结论。合稿后仍需在网站、MD 包和 PDF 里核对新标题、换行、图文关系与分页。
