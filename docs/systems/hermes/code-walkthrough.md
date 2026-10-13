# Hermes 代码导读：知识在哪一刻被读取、批准和刷新

[返回 Hermes 剖面](README.md) · [上下文预算练习](../../labs/context-budget.md)

助手开始排查测试失败时，要先读到项目要求；需要排查方法时，再打开对应 Skill。过程中保存的新知识，要在后续读取或提示重建时用上。下面跟着这条路径找代码：加载、取用、写入，最后刷新提示。

## 用一个任务贯穿代码

沿用虚构例子：用户要求排查测试失败，并强调只在测试环境工作。短要求写进记忆，较长方法写成 Skill；写入与命令执行仍须经过各自权限检查。沿四个位置观察它们：工具收到的内容、返回结果、保存的文件、后续模型输入。

### 1. 找到处理用户输入的入口

[`TurnFacadeMixin.run_conversation()`](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/agent/turn_facade.py#L22-L44)先处理当前后台复查的取消，再把调用转交给会话运行入口，转交代码位于[同文件 142–154 行](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/agent/turn_facade.py#L142-L154)。[`agent/conversation_loop.py`](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/agent/conversation_loop.py#L1643-L1689)处理回合结果，并在结束后调用收尾处理（finalizer）。

找具体功能时，可以从 `run_agent.py` 中的 `AIAgent` 顺着转发调用往下读。这个版本已把功能拆到多个模块，下面逐个找到记忆、Skill、后台复查和提示重建的位置。

### 2. 读入短记忆，为提示准备一份副本

[`_init_memory()`](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/agent/agent_init.py#L1286-L1323)按配置与工具可用性建立 `MemoryStore`，然后 `load_from_disk()`。这里还要查看 `skip_memory` 和显式请求内置 memory 工具的分支，按具体配置判断启用范围。

接着看 [`MemoryStore`](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/tools/memory_tool_store.py#L88-L164)。它分别保管 live entries（当前条目）和 `_system_prompt_snapshot`（给系统提示的副本），加载时去重，再生成提示块。外部写入的超容量内容会留在磁盘，加载时给出提醒；对特定可疑内容的检测和替代只作用于提示快照，磁盘原文仍保留。

### 3. 组装提示：短记忆与 Skill 索引走不同路径

[`_memory_parts()`](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/agent/system_prompt.py#L515-L539)调用 `format_for_system_prompt()`，把内置记忆快照加入系统提示。配置外部 provider（记忆服务提供方）时，还可能追加它提供的提示块。

[`_render_skills_index()`](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/agent/prompt_builder.py#L1359-L1415)把名称和描述组织成索引，部分类别可以只列名称；先给模型一份目录，需要时再读取具体 `SKILL.md`。实际读了哪些文件，可以到工具结果里查看。

### 4. 按需读取：检查 Skill 内容如何成为工具结果

[`skill_view()`](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/tools/skills_tool.py#L573-L693)先解析名称、定位文件，处理不支持的平台、被禁用的 Skill 和支持文件请求；普通读取返回内容、元数据和关联文件索引。需要引用文件时，再用 `file_path` 读取。

加载时，除了读文件，还要看 `preprocess`（预处理）和依赖激活。默认路径可以处理正文并尝试启用声明的工具依赖；使用前应审查这些准备动作。本文没有执行激活。

### 5. 修改记忆：先看操作门禁，再看磁盘变更

模型提出记忆写入后，[`memory_tool()`](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/tools/memory_tool.py#L208-L250)先校验参数，检查无人值守的删除限制和通用写入审批，通过后再调用存储方法。输入是一组操作时，程序另走批量分支。

[`_mutate()`](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/tools/memory_tool_store.py#L245-L295)加锁、重读磁盘、运行变更并保存；[`replace()` / `_edit()`](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/tools/memory_tool_store.py#L298-L362)用匹配文本找到整条记录，再将整条记录替换为新内容。保存采用[临时文件加原子替换](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/tools/memory_tool_store.py#L520-L528)。锁和原子替换处理文件竞争；多执行者写入相互矛盾的事实，还需要应用层检查。

成功结果会告诉调用者操作已完成，并给出容量与条目数量等信息。要查看全部当前条目，还需读取存储；这个版本的成功响应未统一回显全部 live entries，滚动文档中“工具响应总是展示 live state”的描述需要按具体分支核对。[成功回包](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/tools/memory_tool_store.py#L463-L481)

### 6. 修改 Skill：区分提议被接受与文件已更新

要保存或修改排查方法时，模型调用 [`skill_manage()`](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/tools/skill_manager_tool.py#L767-L818)。程序先处理批量输入、后台操作限制和审批，再检查参数、取得锁，交给对应操作的处理函数（handler）。前台任务和后台 review 都通过这套知识维护工具更新 Skill。

开启审批时，[Skill 门禁](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/tools/skill_manager_tool.py#L618-L648)返回带 `staged` 的结果；批准重放有独立入口。一般[审批决策](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/tools/write_approval.py#L169-L193)区分允许、暂存和主动拒绝。审批模块导入失败时，Skill 门禁采用 fail-open（允许继续）分支。依赖缺失时的行为也应纳入安全检查。

### 7. 一轮结束后的审视：有条件启动，并限制可调用工具

一轮任务结束后，[`finalize_turn()` 的触发段](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/agent/turn_finalizer.py#L734-L763)检查计数、可用工具、最终答复、中断和禁用标记。满足条件时，它启动后台知识复查，挑选值得写进文件或整理成方法的经验。

review fork 以[派发白名单](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/agent/background_review.py#L1083-L1124)限制默认工具，并在[执行段](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/agent/background_review.py#L1142-L1188)使用会话快照或有路由时的缩减历史。后台无人值守替换/删除旧记忆另有[暂存门禁](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/tools/memory_tool.py#L167-L204)。配置可增加额外工具；显式人工复查和无人值守来源各按自己的门禁处理。

### 8. 知识何时进入后续输入：追到重建边界

记忆保存之后，[`format_for_system_prompt()`](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/tools/memory_tool_store.py#L463-L466)仍读取准备提示时的快照。正常会话在[压缩提交边界](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/agent/conversation_compression.py#L3144-L3188)调用 invalidate，使旧提示失效，再由[提示失效逻辑](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/agent/system_prompt.py#L790-L820)重读存储并重建提示。detached（分离回合）分支若保留 seeded prompt（预置提示），则提前返回，继续使用这份预置内容。

最后按“待批准列表—正式文件—后续输入—任务结果”检查：先看提议有没有批准和保存，再看模型何时读到，最后看任务是否用对。本文找到了这些观察点，实际效果留待运行验证。

## 图的文字说明

开始工作时，已有短记忆通过加载或受控重建进入提示快照；需要 Skill 时，`skill_view` 把文件内容作为工具结果交给模型。工作中产生的“经验候选”经过写入检查后，可以正式保存到内置记忆 / Skill 文件，也可以进入 pending 等待批准。任务结束后，触发条件满足才启动 review fork；这项复查使用受限工具，无人值守的删除操作还要经过额外检查。图中的箭头分别标出了这些条件。

这张图不表达安装器、所有插件、模型训练、沙箱强度、浏览器操作或外部 provider 的数据生命周期。

## 未验证项与下一步

本文按固定版本 `a9109b07f42685f88397008d0d5a6c3d481b3b28` 的原始 Git 文件和行号讲解，没有安装运行 Hermes、调用模型或执行上游测试。外部 provider 未展开，可疑内容检测的整体安全效果也未测试。压缩重建例外、无人值守删除限制、Skill 暂存与 fail-open 分支仍需运行检查。

要补实验，先准备隔离配置和合成数据，避免使用个人记忆或真实生产任务。然后依次观察写入后的文件、普通回合的模型输入和重建后的输入，看新知识在哪一步进入提示。
