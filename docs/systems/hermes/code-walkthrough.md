# Hermes 代码导读：知识在哪一刻被读取、批准和刷新

[返回 Hermes 剖面](README.md) · [上下文预算练习](../../labs/context-budget.md)

跟读目标不是背下模块名，而是回答：一条跨任务约束和一套可复用流程，怎样从磁盘进入输入，又怎样被修改？所有上游链接固定在 `a9109b07f42685f88397008d0d5a6c3d481b3b28`，下面只解释已读出的局部路径。没有执行上游安装或测试。

## 用一个任务贯穿代码

沿用虚构例子：用户要求排查测试失败，并强调不操作生产数据。可以把这条短约束与排查方法分开保存；但这不代表任何保存调用都有授权，也不代表保存的排查方法正确。分别观察四个证据：提交给工具的内容、工具返回、持久载体、后续请求中的可见内容。

### 1. 从前台 turn 入口开始，不从旧文档的“大文件”描述开始

[`TurnFacadeMixin.run_conversation()`](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/agent/turn_facade.py#L22-L44)先处理当前后台审视的取消，再进入会话运行入口；实际 forwarding 位于[同文件 142–154 行](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/agent/turn_facade.py#L142-L154)。[`agent/conversation_loop.py`](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/agent/conversation_loop.py#L1643-L1689)维护回合结果与结束后的 finalizer。

官方滚动开发文档仍可作为导航，但当前版本已拆出多个职责模块。`run_agent.py` 持有 `AIAgent` 的组合与转发，不能靠旧版文件体积推断当前逻辑都在那里。

### 2. 建立内置记忆：加载时快照与可变条目是两份状态

[`_init_memory()`](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/agent/agent_init.py#L1286-L1323)按配置与工具可用性建立 `MemoryStore`，然后 `load_from_disk()`。注意 `skip_memory` 和请求内置 memory 工具的例外，不能把一个参数概括成关闭所有内外部记忆。

接着看 [`MemoryStore`](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/tools/memory_tool_store.py#L88-L164)：live entries 与 `_system_prompt_snapshot` 分开；加载时去重并生成提示块。已在磁盘但不符合容量的外部写入不会被静默截断；可疑内容的检测替代也只影响快照，不自动删除磁盘原文。模式检测不是完整防注入证明。

### 3. 组装提示：短记忆与 Skill 索引走不同路径

[`_memory_parts()`](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/agent/system_prompt.py#L515-L539)调用 `format_for_system_prompt()` 加入内置快照，并可能追加外部 provider 提示块。本篇不沿外部 provider 展开。

[`_render_skills_index()`](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/agent/prompt_builder.py#L1359-L1415)把名称和描述组织成索引，部分类别可以只列名称；这里不是复制所有 `SKILL.md`。提示中的加载要求是给模型的指导，不是“所有相关 Skill 已经被正确读过”的运行证据。

### 4. 按需读取：检查 Skill 内容如何成为工具结果

[`skill_view()`](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/tools/skills_tool.py#L573-L693)先解析名称、定位文件，处理不支持的平台、被禁用的 Skill 和支持文件请求；普通读取返回内容、元数据和关联文件索引。需要引用文件时，再用 `file_path` 读取。

读这个函数还要看 `preprocess` 和依赖分支，而不是只看 `read_text`：默认路径可预处理正文并尝试激活声明的工具依赖。因此“Skill 是知识文档”不等于其宿主加载函数没有其他作用。此处没有执行任何激活。

### 5. 修改记忆：先看操作门禁，再看磁盘变更

[`memory_tool()`](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/tools/memory_tool.py#L208-L250)校验参数、检查后台删除与通用写审批门禁，随后调用存储方法。操作列表是另一条批量分支，不应漏读。

[`_mutate()`](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/tools/memory_tool_store.py#L245-L295)加锁、重读磁盘、运行变更并保存；[`replace()` / `_edit()`](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/tools/memory_tool_store.py#L298-L362)定位并替换整条记录，不是只修改匹配片段。保存采用[临时文件加原子替换](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/tools/memory_tool_store.py#L520-L528)。这些机制降低特定文件竞争风险，不表示多 Agent 共用一个记忆空间在语义上安全。

成功结果给出完成、容量与条目数量等信息，但当前版本不统一回显全部 live entries；这与滚动文档“工具响应总是展示 live state”的笼统说法不同。[成功回包](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/tools/memory_tool_store.py#L463-L481)

### 6. 修改 Skill：区分提议被接受与文件已更新

[`skill_manage()`](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/tools/skill_manager_tool.py#L767-L818)先处理批量分支、后台前置守卫和审批，再进入参数检查、锁与动作 handler。前台与 review 都经由知识维护工具，而不是直接把生成的文字当成已安装 Skill。

开启审批时，[Skill 门禁](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/tools/skill_manager_tool.py#L618-L648)返回带 `staged` 的结果；批准重放有独立入口。一般[审批决策](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/tools/write_approval.py#L169-L193)区分允许、暂存和主动拒绝。关卡模块导入失败时，这个 Skill 门禁存在 fail-open 分支；因此不能把配置开关写成绝对强隔离保证。

### 7. 一轮结束后的审视：有条件启动，并限制可调用工具

[`finalize_turn()` 的触发段](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/agent/turn_finalizer.py#L734-L763)根据计数、可用工具、最终答复、中断和禁用标记决定是否发起后台审视。它不是“用户说一句话，立刻训练一次”。

review fork 以[派发白名单](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/agent/background_review.py#L1083-L1124)限制默认工具，并在[执行段](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/agent/background_review.py#L1142-L1188)使用会话快照或有路由时的缩减历史。后台无人值守替换/删除旧记忆另有[暂存门禁](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/tools/memory_tool.py#L167-L204)。配置可增加额外工具；显式人工 review 与无人值守来源也不同，不应画成无条件保存箭头。

### 8. 知识何时进入后续输入：追到重建边界

[`format_for_system_prompt()`](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/tools/memory_tool_store.py#L463-L466)读取冻结快照，普通写入不改变它。live agent 的[压缩提交边界](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/agent/conversation_compression.py#L3144-L3188)调用 invalidate，再由[提示失效逻辑](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/agent/system_prompt.py#L790-L820)重读内存。保留 seeded prompt 的 detached 分支提前返回，是本结论的明确例外。

因此验收“记住了”时，至少应分别核对：保存结果是不是仅暂存；正式文件是否改变；后续模型输入是否包含更新；任务是否正确使用它。我们在这里定位了这些观察点，还没有运行它们。

## 图的文字说明

主线从“已有知识”进入“本轮输入与工作”，最后分出“经验候选”。经验候选经过写入门禁后，只有正式保存分支进入内置记忆 / Skill 文件；待批准分支停在 pending。记忆文件到当前提示快照的箭头必须标注“加载 / 受控重建”，不能标成即时同步。Skill 文件到本轮工具结果的箭头标注 `skill_view`。任务结束到 review fork 的箭头标注“触发条件满足”，fork 到写入门禁的箭头说明受限工具与无人值守删除限制。

这张图不表达安装器、所有插件、模型训练、沙箱强度、浏览器操作或外部 provider 的数据生命周期。

## 未验证项与下一步

本次仅获取固定 Git blob 并按原始文件行号核对，没有执行上游测试或实际模型回合。独立审稿应优先重开三条路径：压缩重建例外、无人值守删除门禁、Skill 暂存与 fail-open 分支。随后用隔离配置和合成数据验证“写后文件、写后普通回合、重建后输入”三种观察；不能使用个人记忆或真实生产任务作为测试数据。
