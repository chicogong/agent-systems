# Hermes：保存知识与当前输入

[章节](../../docs/systems/hermes/README.md) · [代码导读](../../docs/systems/hermes/code-walkthrough.md) · [SVG](diagram.svg) · [PNG](preview.png) · [图源](scene.excalidraw)

假设助手刚完成一次排查，希望以后记住项目要求，也能沿用排查方法。Hermes 把短事实存进记忆文件，把较长的方法存成 Skill（可复用的工作方法）。这张图说明它们怎样保存，又怎样被模型取用。

## 跟着一次取用和保存走

1. **开工前读短记忆。** 宿主从 `MEMORY.md` 和 `USER.md` 读取内容，准备一份供系统提示使用的副本。图中的“系统提示快照”，就是准备提示时留下的这份内容。
2. **把本轮材料交给模型。** 宿主将快照与当前用户、助手和工具消息组合成输入。模型据此回答或建议调用工具。图中的“本轮模型输入”表示这次请求实际收到的材料。
3. **需要长流程时再读取。** 模型可以调用 `skill_view`，由宿主返回 `SKILL.md` 或相关参考文件，作为工具结果交回模型。长流程因此可以按需使用。
4. **发现值得保存的经验，先提出修改。** 前台工具调用，或条件满足时启动的后台 `review`（复查），可以提出更新。宿主通过内置 `memory` / `skill_manage` 检查操作、处理审批，再保存短事实或流程文件。
5. **需要批准的提议先等一等。** 图中的“待批准 pending”指待批准列表。提议先暂存，获批后再提交，并检查实际保存结果。图中的“检查知识写入”对应这一段操作与审批检查。

浅绿是正式保存的知识，紫色是提示快照，蓝色是本轮输入及模型提出的修改，橙色是写入检查与待批准提议。节点名称也说明了各自用途，不需要只靠颜色辨认。

## 新知识怎样进入后面的回答

普通的中途写入先改变存储，提示中的那份快照仍保留原内容。图中的“加载 / live 压缩”表示加载提示，以及仍在运行的助手（`live agent`）提交上下文压缩结果时的读取分支。另有 `detached`（分离回合）的压缩路径，可能沿用提前准备好的 `seeded prompt`（预置提示）；这条分支可能继续使用已有内容，不能一律按图中的重读箭头理解。

当前消息和工具结果也能带来新信息。因此，检查模型看到了什么时，要一起看系统提示快照和本轮消息。图中的消息框用于说明这些组成部分，实际发送哪些消息由宿主安排。

## 几种需要单独处理的情况

- **执行前被审批拒绝，停止提交。** 图上的“写前审批拒绝：不提交”指处理动作之前就被审批拒绝。
- **执行报错，读回核对。** 记忆工具先修改内存条目，再写文件；Skill 的一条路径先落盘再扫描，扫描拒绝时尝试恢复原文，恢复也可能报错。此时要核对当前条目、正式文件和保存结果，再决定后续动作。
- **读取 Skill 可能带着准备步骤。** 默认加载可预处理内容或激活依赖，使用前应检查 Skill 内容、依赖和允许的操作。
- **后台复查按条件启动。** 无人值守时，替换或删除旧记忆还有额外暂存要求。默认工具白名单限制其操作范围，显式 `extra_tools` 配置则可以扩充这份名单。

## 来源与范围

固定源码版本：[`NousResearch/hermes-agent@a9109b07f42685f88397008d0d5a6c3d481b3b28`](https://github.com/NousResearch/hermes-agent/tree/a9109b07f42685f88397008d0d5a6c3d481b3b28)，核对日期 2026-09-27；[MIT](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/LICENSE)。图根据源码简化了知识读取、修改与保存过程，尚未追踪实际运行。

- 记忆 → 快照：[提示块读取](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/agent/system_prompt.py#L515-L539)、[失效重载](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/agent/system_prompt.py#L804-L820)、[live / seeded 重建分支](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/agent/conversation_compression.py#L3144-L3188)。
- 提出修改 → 保存 / 暂存：[memory 入口](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/tools/memory_tool.py#L208-L250)、[Skill 写入检查](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/tools/skill_manager_tool.py#L618-L648)、[审批决策](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/tools/write_approval.py#L169-L193)。
- 报错后读回核对：[内存先更新再落盘](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/tools/memory_tool_store.py#L245-L274)、[Skill 写后扫描与恢复](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/tools/skill_manager_tool.py#L350-L369)。
- Skill → 当前输入的工具结果：[skill_view](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/tools/skills_tool.py#L573-L693)。
- 后台复查条件与写入限制：[触发段](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/agent/turn_finalizer.py#L734-L763)、[无人值守删除暂存](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/tools/memory_tool.py#L167-L204)。

全部会话恢复、外部记忆服务、审批界面、沙箱、Skill 批量操作和插件分支需另看各自实现。这里保存和取用的是资料，图中没有模型权重训练过程。

## 生成与核验

`build.py` 通过仓库共用 Scene builder 生成原生 `.excalidraw`。SVG / 4× PNG 使用 excalidraw-agent 的固定原生 renderer 导出，不能用手写 SVG 替代导出。

已有源码与 PNG / PDF 图稿检查记录见[新增系统审查](../../docs/reviews/2026-09-27-new-systems-review.md)与[PDF 专项审查](../../docs/reviews/2026-09-27-expansion-pdf-review.md)，实际运行效果仍需单独验证。用 MCP 展示时，字体可能与仓库导出不同，还要打开实际交互画布检查。
