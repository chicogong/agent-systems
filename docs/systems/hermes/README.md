# Hermes：怎样把一次经验变成下次可用的知识

[返回系统目录](../README.md) · [关键代码导读](code-walkthrough.md) · [上下文与记忆](../../concepts/context-vs-memory.md)

你刚教会助手一套排查方法，下一次任务它能不能复用？这不是“把聊天记录全部存起来”就能回答的问题。本篇用 Hermes 解释三个不同动作：保存简短事实、按需读取较长流程、在任务结束后审视是否值得修改知识。它们改变的是宿主维护的文件和模型输入，不能直接理解为模型权重训练。

> 固定研究版本：[`NousResearch/hermes-agent@a9109b07f42685f88397008d0d5a6c3d481b3b28`](https://github.com/NousResearch/hermes-agent/tree/a9109b07f42685f88397008d0d5a6c3d481b3b28)，核对日期 2026-09-27；上游提交时间为 2026-09-27 03:21:39 UTC。[仓库 LICENSE 为 MIT](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/LICENSE)。本稿是静态源码剖面，不是运行评测。

## 先把两种知识分开

以一个虚构任务说明：你让助手分析测试失败，同时明确“本项目只在隔离的测试环境验证，不操作生产数据”。

- 这条跨任务约束适合短记忆：内置 `MEMORY.md` / `USER.md` 对应环境事实与用户资料，加载时生成系统提示块。默认字符容量分别为 2,200 与 1,375；这是源码中的字符限制，不是精确 Token 配额，也不是手工外部写入后会自动截断的保证。[内置存储与加载](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/tools/memory_tool_store.py#L88-L164)
- “如何定位测试依赖、复现最小失败、核对修复”适合 Skill：启动提示通常列出名称和描述，`skill_view` 再按需返回 `SKILL.md` 或支持文件。流程长文不必全部常驻系统提示。[索引生成](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/agent/prompt_builder.py#L1359-L1415)、[按需读取](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/tools/skills_tool.py#L573-L693)

两种知识都有持久载体，但进入本轮上下文的方式不同。短记忆并不自动授权执行；Skill 中写着一个命令，也不意味着读 Skill 就已经完成了任务。

## 正常路径：读、做、筛选，再保存

1. 内置记忆启用时，初始化建立 `MemoryStore` 并从磁盘读取，形成加载时快照。
2. 系统提示组合该快照与 Skill 索引；模型先知道有哪些流程，而不是已经读过所有流程正文。
3. 任务需要某个流程时，模型调用 `skill_view`，宿主解析名称、检查状态并返回内容；读取支持文件是另一次调用。
4. 前台工作发现稳定事实或流程缺陷时，可以提出 `memory` 或 `skill_manage` 调用。写入经过各自的操作检查与审批分支，不由一句“学到了”替代实际结果。
5. 一轮结束后，达到记忆或 Skill 审视触发条件、存在最终答复、未被中断且未禁止后台审视时，宿主可能启动 review fork。它使用会话快照和受限工具面，不是每轮必定保存一条知识。
6. 真正落盘的知识与暂存的提议要区分。下一次提示重建或显式 Skill 读取，才是观察这些变化是否进入模型输入的位置。

这条路径的具体入口、状态和分支见[代码导读](code-walkthrough.md)。下面只画“已保存、待批准、当前可见”的关系，不是完整系统架构。

![Hermes 中持久知识、系统提示快照、当前输入和待批准写入的区别](../../../figures/hermes-session-memory/diagram.svg)

[图源](../../../figures/hermes-session-memory/scene.excalidraw) · [PNG 预览](../../../figures/hermes-session-memory/preview.png) · [不看图的说明与箭头证据](../../../figures/hermes-session-memory/README.md)

## 最容易误解的边界：写入了，不等于系统提示立即改变

`MemoryStore` 的 live entries 可以写回磁盘，但 `format_for_system_prompt()` 返回加载时捕获的快照。普通中途写入不会直接修改这个快照。当前任务仍可从用户消息和工具结果得到新信息，所以不能反过来说“模型完全不知道更新”；只能说“缓存的系统提示记忆块没有被这次写入直接替换”。[写入与快照的分离](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/tools/memory_tool_store.py#L245-L295)、[快照读取](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/tools/memory_tool_store.py#L463-L481)

也不要把它概括成“整场会话永远冻结”。固定版本的 live agent 压缩提交边界会使提示失效、重载内存并重建提示；保留 seeded prompt 的 detached 路径有例外。更准确的心智模型是：在普通回合间保持稳定，在受控重建边界刷新，而不是每次文件变化都即时更新。[压缩边界](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/agent/conversation_compression.py#L3144-L3188)、[失效时重载](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/agent/system_prompt.py#L790-L820)

## 失败路径与反例

**内存满了。** `add` / `replace` 超过字符容量会返回失败，要求缩短、合并或移除，而不是悄悄丢弃旧条目。替换是整条 entry 替换，`old_text` 只用于定位；它不是在条目中局部替换一个短语。多条匹配也会拒绝猜测。重复整合失败后有终止提示，避免保存辅助知识拖住用户的答复。[容量与整条替换](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/tools/memory_tool_store.py#L276-L362)、[连续失败限制](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/tools/memory_tool_store.py#L93-L131)

**工具返回 `success: true`，但知识还没生效。** 开启 `write_approval` 时，Skill 写入会先暂存；记忆写入则按前台交互、后台等来源决定询问或暂存。暂存结果可以包含 `success: true` 与 `staged: true`，表示提议处理成功，而非正式存储已更新。审批还可能被拒绝。应检查 `staged`、待办记录和实际读回，不只检查一个布尔值。[审批决策](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/tools/write_approval.py#L169-L193)、[Skill 暂存结果](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/tools/skill_manager_tool.py#L618-L648)

**后台审视不能等同于前台自由操作。** 当前源码对无人值守 review 的记忆 `replace` / `remove` 有额外暂存门禁，即使通用审批开关关闭也不能直接执行这类删除旧知识的操作。默认 review 工具白名单也不允许普通 terminal / 写文件工具；但配置的 `extra_tools` 能扩充它，不能宣称它永远只有固定几个工具。[无人值守删除门禁](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/tools/memory_tool.py#L167-L204)、[review 白名单](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/agent/background_review.py#L1083-L1124)

**读取 Skill 不是纯文本的绝对无副作用操作。** `skill_view` 的默认预处理和依赖激活路径意味着，不能只看其名称就假定等价于静态读文件。本稿不执行它；安装、预处理、包激活与沙箱权限需要另行审查。[预处理与依赖分支](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/tools/skills_tool.py#L573-L664)

## 与 Pi 对照时，比较什么

[Pi 的既有剖面](../pi/README.md)区分核心循环与 coding 会话外壳，[Skill 篇](../pi/extensions-and-skills.md)解释按需指令与可执行 Extension。Hermes 这一篇多讲一步：宿主如何把短事实和长流程作为可写的跨任务资产，并为任务后的审视建立独立触发与工具门禁。

这不是“有记忆 / 没记忆”的全产品排名。Pi 可以通过扩展实现额外工作流；本篇也没有审计 Hermes 的所有插件。可学习的取舍是：更多知识维护逻辑放进宿主，能让复用路径显式，但也要承担缓存刷新、错误知识持久化、审批、并发写入与维护成本。这是基于本文路径的工程判断，不是效果或性能证明。

## 自测：你能区分哪种“成功”吗

1. `memory` 写入成功后，是否可以断言本轮缓存系统提示中的 MEMORY 块已经换成新值？不能；普通写入不改变快照，提示重建有单独边界。
2. `skill_manage` 返回 `success: true, staged: true`，可以报告“Skill 已更新，下次必定使用”吗？不能；先是待批准提议，批准、实际落盘、发现并读取各是一步。
3. 保存了一份排查 Skill，能否证明下一次排查更准确？不能；需要验证内容正确、确实进入输入、执行环境适用，以及最终结果通过验收。

## 本篇未覆盖

未运行 Hermes、未调用模型、未验证写入审批界面、未做多进程竞争实验；未评估记忆有效性或 Skill 生成质量。外部记忆 provider、压缩算法本体、Skill Hub 安全扫描、完整插件框架、terminal 后端及 Computer Use 留给单独专题。官方滚动文档用于发现线索，遇到与固定源码不一致时，以本文链接的版本限定结论。
