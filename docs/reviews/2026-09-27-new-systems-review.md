# DSH 与 Hermes：独立静态二审

## 最新收口：四项 P2 已落实

2026-09-27 最终落地核对：下表四项 P2 均已按建议修订，可在本轮关闭；首轮问题与证据保留在下文。本段由 Hermes 初稿代理回查当前文件补记，是修订落地核对，不是新增独立审稿或外部真人试读。

- DSH 默认值：[`code-walkthrough.md` 第 5 节“从 pre-execute 跟到审批”](../systems/dsh/code-walkthrough.md)已明写 pre-execute 的终端默认值为 `allow`，只有 `ask` 才进入询问，缺通道拒绝与 guard／取消的边界仍保留。
- Hermes Skill 证据范围：[`README.md` 的“读取 Skill”段](../systems/hermes/README.md)已将“预处理与依赖分支”改为固定源码 `skills_tool.py#L573-L664`；代码导读仍给出覆盖该局部的 `#L573-L693` 并说明预处理与依赖激活。
- Hermes 压缩重建：当前 [介绍](../systems/hermes/README.md)、[导读第 8 步](../systems/hermes/code-walkthrough.md)、[图的文字说明](../../figures/hermes-session-memory/README.md)均使用 `conversation_compression.py#L3144-L3188`，且保留 detached seeded prompt 提前返回的例外。
- Hermes 图中主体：当前 [图的文字说明](../../figures/hermes-session-memory/README.md)、`figures/hermes-session-memory/build.py` 与 `scene.excalidraw` 已将蓝色节点改为“本轮模型回合”，保留“输入：快照 + 当前消息／输出：知识修改提案”，不再由“当前模型输入”充当修改主体。

本次仅核对上述当前正文、导读、图文字与图源的修订落地，没有联网重取源码、运行上游或重验 SVG／PNG、MCP、PDF、网页和纸样；这些范围及原有未验证声明不变。其他首轮结论和后续验收建议也未更改。

核对日期：2026-09-27。审稿者未参与这两篇的初稿撰写；只新增本记录，没有直接修改主稿、图或公共索引，也没有提交、推送或运行上游。这里是 Agent 交叉审稿，不是外部真人试读。

## 结论与范围

审查时的核心主张与固定官方源码相符，未发现需阻断合稿的 P0／P1 事实错误。仍有三处 P2 的表达／锚点修订及一处图中职责歧义，建议合稿者收口后纳入预览清单。检查范围为 DSH 工具批次、授权接缝与 bash sandbox；Hermes 内置记忆快照、Skill 加载／维护、后台 review 与压缩重建。不是两个项目的全仓审计、插件审计、安全认证或行为实测。

读了两篇系统介绍、两篇代码导读及各自 field-notes；另外阅读 DSH 图的文字说明、Hermes 图的文字说明并实际查看其 PNG。DSH 图在审查时尚未完成 SVG／PNG 导出，本文不将文字说明核对当作图的视觉验收。

## 合稿前建议修订

| 等级 | 位置与触发 | 影响 | 最小修订与源码证据 |
| --- | --- | --- | --- |
| P2 | `docs/systems/dsh/code-walkthrough.md` 第 5 节只说“默认预执行决定”和“要求询问但无法询问”不同，没有直接给出默认值 | 读者可能仍误以为 DSH 默认对所有工具询问审批，或缺审批服务对全部调用拒绝 | 明写：pre-execute 瀑布的终端默认值为 `allow`；只有策略选择 `ask` 的调用进入审批接缝。缺通道拒绝限定于这条分支；guard 与取消仍可阻止 dispatch。[默认值与分支](https://github.com/deepseek-ai/deepseek-harness/blob/477b4f420553e8a52c2fbccc464d7561b239c443/packages/core/tools/src/index.ts#L1504-L1535)、[ask 降级拒绝](https://github.com/deepseek-ai/deepseek-harness/blob/477b4f420553e8a52c2fbccc464d7561b239c443/packages/core/tools/src/index.ts#L1727-L1767)。原文结论没有写反，问题是教学显式程度。 |
| P2 | `docs/systems/hermes/README.md` 的“预处理与依赖分支”只链接 `skills_tool.py#L628-L664` | 这个范围包含依赖激活，却漏了实际 `_preprocess_skill()` 调用，读者点链接不能完整核对同一句的两部分 | 扩为 `#L573-L664`，覆盖 `preprocess=True` 的默认参数及 L625–626 的条件预处理。[完整局部函数](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/tools/skills_tool.py#L573-L664)。代码导读已有更完整范围，不是机制事实错误。 |
| P2 | Hermes 介绍、导读与图文字版把压缩重建证据截止在 `conversation_compression.py#L3180` | 分支、invalidate 和重建注释可见，但真正 `_build_system_prompt()` 调用在 L3182，读者仍需手动找后文 | 将这组锚点延长至 L3188；保留 detached seeded 路径例外，不改结论。[完整重建调用](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/agent/conversation_compression.py#L3144-L3188)。 |
| P2 | Hermes 图从“当前模型输入”指向知识写门禁，箭头只写“提出知识修改” | 输入是数据，不是产生工具提案的主体；正文已正确拆开输入、模型与宿主，但单看图仍可能混淆 | 不必加一整层框，将箭头明确为“模型提出修改”，或将节点命名为“本轮模型回合”并保留输入构成说明。写门禁与 pending 的其他语义不用改变。此项是图的教学职责表达，不是新上游 API 断言。 |

另外，Hermes 代码导读还有“一张待画图的文字版”标题，初稿状态句写着“尚未独立二审”。图已经生成且本轮二审完成后，应由合稿者统一更新这些状态文字；这类状态不能被误当成运行验证已经完成。

## 已按原文件确认的主张

取得方法：固定 commit 的 GitHub Contents API → base64 解码原文件 → `nl -ba`。没有使用网页提取的虚拟行号替代 GitHub 源码锚点，也没有导入或执行下载的源码。

### DSH：`477b4f420553e8a52c2fbccc464d7561b239c443`

- `executeToolCalls()` 按 live execution mode 组织批次；后续调用重新分类，exclusive 可以构成屏障。`startCall()` 串行准备，dispatch 的 promise 可重叠，不是所有调用无条件并行。[批次与准备](https://github.com/deepseek-ai/deepseek-harness/blob/477b4f420553e8a52c2fbccc464d7561b239c443/packages/core/agent-loop/src/tool-calls.ts#L60-L213)
- `commitReady()` 只跨连续 ready slot 推进，finalize／finish 后按模型调用次序 append 结果和附加上下文。A 慢、B 快的虚构轨迹能解释头部阻塞，文章明确不将其当实测。[提交器](https://github.com/deepseek-ai/deepseek-harness/blob/477b4f420553e8a52c2fbccc464d7561b239c443/packages/core/agent-loop/src/tool-calls.ts#L146-L159)
- 有序提交不保证外部副作用顺序。源码允许 dispatch 重叠，正文与图文字版均保留远端写入可能先发生的边界，未声称事务或撤销保证。[重叠 dispatch](https://github.com/deepseek-ai/deepseek-harness/blob/477b4f420553e8a52c2fbccc464d7561b239c443/packages/core/agent-loop/src/tool-calls.ts#L165-L184)
- scheduler failure 等待已开始 promise 结算并传播错误；取消可以为未启动调用生成跳过结果。没有把缺结果补为成功，也没有把取消等同外部撤销。[失败与取消](https://github.com/deepseek-ai/deepseek-harness/blob/477b4f420553e8a52c2fbccc464d7561b239c443/packages/core/agent-loop/src/tool-calls.ts#L219-L259)
- `ask` 无审批服务／无 Agent，或用户拒绝／取消／通道 unavailable 时进入拒绝；allowed-once 才映射 allow。guard 在允许路径仍运行，不被一个前置 allow 跳过。[授权分支](https://github.com/deepseek-ai/deepseek-harness/blob/477b4f420553e8a52c2fbccc464d7561b239c443/packages/core/tools/src/index.ts#L1493-L1539)
- `danger-full-access` 使用基础执行器；其他策略经 `confine()`，识别到 runner failure 时抛 `SandboxUnavailableError`，没有在该分支静默普通执行。[执行器](https://github.com/deepseek-ai/deepseek-harness/blob/477b4f420553e8a52c2fbccc464d7561b239c443/packages/shell/bash-sandbox/src/index.ts#L85-L133)、[confine](https://github.com/deepseek-ai/deepseek-harness/blob/477b4f420553e8a52c2fbccc464d7561b239c443/packages/shell/bash-sandbox/src/index.ts#L178-L189)
- 服务组合与 shared execution world 的说明有固定架构文档支持；`SAFETY.md` 确实明确开发者预览未经安全审计、不可作为唯一不可信工作负载控制。文稿没有替它背书。[接缝](https://github.com/deepseek-ai/deepseek-harness/blob/477b4f420553e8a52c2fbccc464d7561b239c443/docs/architecture.md#L129-L135)、[安全说明](https://github.com/deepseek-ai/deepseek-harness/blob/477b4f420553e8a52c2fbccc464d7561b239c443/SAFETY.md#L5-L23)

### Hermes：`a9109b07f42685f88397008d0d5a6c3d481b3b28`

- 2,200／1,375 是 `MemoryStore` 与初始化缺配置时的字符容量默认，不是 Token；外部超过容量的文件会警告但继续加载，不静默截断。[构造与加载](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/tools/memory_tool_store.py#L88-L164)、[初始化默认](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/agent/agent_init.py#L1286-L1323)
- 加载时快照与 live entries 分开，普通 `_mutate()` 保存不更新快照，`format_for_system_prompt()` 返回快照。当前消息仍可能包含更新，所以文稿没有误说“模型完全不知道新值”。[保存](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/tools/memory_tool_store.py#L245-L296)、[快照读取](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/tools/memory_tool_store.py#L463-L481)
- live 压缩边界 invalidate，重读内置存储并 rebuild；`_retain_seeded_system_prompt` 提前返回是明确例外。文稿没有把快照概括成会话内永远冻结。[失效重载](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/agent/system_prompt.py#L802-L820)、[重建与例外](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/agent/conversation_compression.py#L3144-L3188)
- `replace()` 是整条记录替换，old_text 定位；多匹配拒绝，容量超限不写。成功回包不统一列出所有 entries，但可额外返回被替换／删除记录，原文“不是统一回显全部”是适当限定。[编辑与匹配](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/tools/memory_tool_store.py#L298-L362)
- 通用 write gate 关闭为 allow；开启后 Skills 及后台来源 stage，前台 memory 可 inline prompt，无交互通道 stage。`success: true, staged: true` 不等于正式知识写入。Skill gate 导入失败确有 fail-open，不能称绝对安全边界。[gate](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/tools/write_approval.py#L171-L186)、[Skill 暂存与 fail-open](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/tools/skill_manager_tool.py#L618-L648)
- 无人值守 review 的 memory replace／remove 走额外暂存门禁，失败为拒绝；门禁也检查批量动作。review 默认为派发侧白名单，可扩展已存在的 parent tools；不是广告 schema 上所有工具都真的可执行，也不是永远固定小工具集。[删除门禁](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/tools/memory_tool.py#L166-L241)、[白名单与执行](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/agent/background_review.py#L1083-L1188)
- `skill_view` 默认预处理，声明依赖时尝试 `pm.ensure()`；正文已提示不是纯读文件，无执行实测。索引按名称／描述或 names-only 提供，不等于全文常驻。[加载](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/tools/skills_tool.py#L573-L679)、[索引](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/agent/prompt_builder.py#L1358-L1415)

## 未验证与后续验收

上述判断来自固定原文件，未运行模型、CLI、sandbox、approval UI、写入 replay 或多进程竞争实验；未核对所有插件、provider、终端后端、许可证依赖或真实效果。二审不能替代这些运行证据。

建议分别建立小型合成实验：DSH 记录 A／B 的 prepare、dispatch、settle、append，注入 ask 无通道与取消；Hermes 记录 stage／正式文件／普通回合输入／live 压缩后输入四种状态，另测 seeded detached 例外。实验必须专用目录、无真实账号或生产权限。PDF、网页、Markdown 的入清单与阅读体验检查由合稿者完成。

## 补充：DSH PNG 的实际目视范围

2026-09-27 初次文字审查后，实际打开了 `figures/dsh-tool-batch/preview.png`（3,960 × 1,940），并重新对照图的 README。三段主路径分别表达模型调用顺序、允许重叠的执行、等待连续 ready slot 的结果提交；下方两条虚线分别保留 ask 缺通道拒绝与外部副作用可能先发生的边界。节点文字清晰，箭头未穿过文字，未见截断、重叠或连线归属不明。此例是假设 B 较快的教学投影，图和说明都没有将其写成实测轨迹。

该补充只确认这张 PNG 的目视可读性与上述静态机制一致，不覆盖 SVG（当时仍待合稿者导出）、MCP 画布、PDF 缩排后阅读、移动端或 A4 纸面字号；不等于运行调度器、审批通道或 sandbox 的验收。
