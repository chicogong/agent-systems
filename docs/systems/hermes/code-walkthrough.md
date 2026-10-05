# Hermes 代码导读：知识在哪一刻被读取、批准和刷新

[返回 Hermes 剖面](README.md) · [上下文预算练习](../../labs/context-budget.md)

这篇是可选的源码路线，跟着一条短事实和一份排查方法读下去：先看加载，再看取用和写入，最后找提示刷新位置。上游版本固定在 `a9109b07f42685f88397008d0d5a6c3d481b3b28`。本文按代码讲解，没有执行安装、模型或上游测试。

## 用一个任务贯穿代码

沿用虚构例子：用户要求排查测试失败，并强调只在测试环境工作。短要求写进记忆，较长方法写成 Skill；写入与命令执行仍须经过各自权限检查。沿四个位置观察它们：工具收到的内容、返回结果、保存的文件、后续模型输入。

### 1. 找到处理用户输入的入口

[`TurnFacadeMixin.run_conversation()`](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/agent/turn_facade.py#L22-L44)先处理当前后台审视的取消，再进入会话运行入口；实际 forwarding 位于[同文件 142–154 行](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/agent/turn_facade.py#L142-L154)。[`agent/conversation_loop.py`](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/agent/conversation_loop.py#L1643-L1689)维护回合结果与结束后的 finalizer。

官方滚动开发文档仍可作为导航，但当前版本已拆出多个职责模块。`run_agent.py` 负责 `AIAgent` 的组合与转发；具体职责分散在下面这些模块中。

### 2. 读入短记忆，为提示准备一份副本

[`_init_memory()`](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/agent/agent_init.py#L1286-L1323)按配置与工具可用性建立 `MemoryStore`，然后 `load_from_disk()`。这里还要查看 `skip_memory` 和显式请求内置 memory 工具的分支，按具体配置判断启用范围。

接着看 [`MemoryStore`](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/tools/memory_tool_store.py#L88-L164)：live entries 与 `_system_prompt_snapshot` 分开；加载时去重并生成提示块。已在磁盘但不符合容量的外部写入不会被静默截断；可疑内容的检测替代也只影响快照，不自动删除磁盘原文。模式检测用于筛查特定可疑内容；整体安全效果需另做测试。

### 3. 组装提示：短记忆与 Skill 索引走不同路径

[`_memory_parts()`](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/agent/system_prompt.py#L515-L539)调用 `format_for_system_prompt()` 加入内置快照，并可能追加外部 provider 提示块。本篇不沿外部 provider 展开。

[`_render_skills_index()`](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/agent/prompt_builder.py#L1359-L1415)把名称和描述组织成索引，部分类别可以只列名称；先给模型一份目录，需要时再读取具体 `SKILL.md`。实际读了哪些文件，可以到工具结果里查看。

### 4. 按需读取：检查 Skill 内容如何成为工具结果

[`skill_view()`](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/tools/skills_tool.py#L573-L693)先解析名称、定位文件，处理不支持的平台、被禁用的 Skill 和支持文件请求；普通读取返回内容、元数据和关联文件索引。需要引用文件时，再用 `file_path` 读取。

加载时，除了读文件，还要看 `preprocess`（预处理）和依赖激活。默认路径可以处理正文并尝试启用声明的工具依赖；使用前应审查这些准备动作。本文没有执行激活。

### 5. 修改记忆：先看操作门禁，再看磁盘变更

[`memory_tool()`](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/tools/memory_tool.py#L208-L250)校验参数、检查后台删除与通用写审批门禁，随后调用存储方法。操作列表是另一条批量分支，不应漏读。

[`_mutate()`](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/tools/memory_tool_store.py#L245-L295)加锁、重读磁盘、运行变更并保存；[`replace()` / `_edit()`](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/tools/memory_tool_store.py#L298-L362)用匹配文本找到整条记录，再将整条记录替换为新内容。保存采用[临时文件加原子替换](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/tools/memory_tool_store.py#L520-L528)。锁和原子替换处理文件竞争；多执行者写入相互矛盾的事实，还需要应用层检查。

成功结果给出完成、容量与条目数量等信息，但当前版本不统一回显全部 live entries；这与滚动文档“工具响应总是展示 live state”的笼统说法不同。[成功回包](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/tools/memory_tool_store.py#L463-L481)

### 6. 修改 Skill：区分提议被接受与文件已更新

[`skill_manage()`](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/tools/skill_manager_tool.py#L767-L818)先处理批量分支、后台前置守卫和审批，再进入参数检查、锁与动作 handler。前台与 review 都经由知识维护工具，而不是直接把生成的文字当成已安装 Skill。

开启审批时，[Skill 门禁](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/tools/skill_manager_tool.py#L618-L648)返回带 `staged` 的结果；批准重放有独立入口。一般[审批决策](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/tools/write_approval.py#L169-L193)区分允许、暂存和主动拒绝。审批模块导入失败时，Skill 门禁采用 fail-open（允许继续）分支。依赖缺失时的行为也应纳入安全检查。

### 7. 一轮结束后的审视：有条件启动，并限制可调用工具

[`finalize_turn()` 的触发段](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/agent/turn_finalizer.py#L734-L763)根据计数、可用工具、最终答复、中断和禁用标记决定是否发起后台审视。条件满足时启动知识复查，更新的是文件和方法。

review fork 以[派发白名单](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/agent/background_review.py#L1083-L1124)限制默认工具，并在[执行段](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/agent/background_review.py#L1142-L1188)使用会话快照或有路由时的缩减历史。后台无人值守替换/删除旧记忆另有[暂存门禁](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/tools/memory_tool.py#L167-L204)。配置可增加额外工具；显式人工复查和无人值守来源各按自己的门禁处理。

### 8. 知识何时进入后续输入：追到重建边界

[`format_for_system_prompt()`](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/tools/memory_tool_store.py#L463-L466)读取冻结快照，普通写入不改变它。live agent 的[压缩提交边界](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/agent/conversation_compression.py#L3144-L3188)调用 invalidate，再由[提示失效逻辑](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/agent/system_prompt.py#L790-L820)重读内存。保留 seeded prompt 的 detached 分支提前返回，是本结论的明确例外。

最后按“待批准列表—正式文件—后续输入—任务结果”检查：先看提议有没有批准和保存，再看模型何时读到，最后看任务是否用对。本文找到了这些观察点，实际效果留待运行验证。

## 图的文字说明

主线从“已有知识”进入“本轮输入与工作”，最后分出“经验候选”。经验候选经过写入门禁后，只有正式保存分支进入内置记忆 / Skill 文件；待批准分支停在 pending。记忆文件通过加载或受控重建进入提示快照。Skill 文件到本轮工具结果的箭头标注 `skill_view`。任务结束到 review fork 的箭头标注“触发条件满足”，fork 到写入门禁的箭头说明受限工具与无人值守删除限制。

这张图不表达安装器、所有插件、模型训练、沙箱强度、浏览器操作或外部 provider 的数据生命周期。

## 未验证项与下一步

本次仅获取固定 Git blob 并按原始文件行号核对，没有执行上游测试或实际模型回合。独立审稿应优先重开三条路径：压缩重建例外、无人值守删除门禁、Skill 暂存与 fail-open 分支。随后用隔离配置和合成数据验证“写后文件、写后普通回合、重建后输入”三种观察；不能使用个人记忆或真实生产任务作为测试数据。
