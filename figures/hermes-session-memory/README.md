# Hermes：保存知识与当前输入

[章节](../../docs/systems/hermes/README.md) · [代码导读](../../docs/systems/hermes/code-walkthrough.md) · [SVG](diagram.svg) · [PNG](preview.png) · [图源](scene.excalidraw)

本图只回答：短记忆和流程知识经过怎样的读写边界，才可能进入模型输入？浅绿表示正式持久知识，紫色是加载时提示快照，蓝色是本轮模型回合及其输入、知识提案，橙色表示修改门禁与待批准提议。颜色之外，节点名和箭头也分别说明这些状态。

## 不看图的说明

1. 内置 `MEMORY.md` / `USER.md` 在加载时进入系统提示快照；普通中途写入不即时替换快照。live agent 的压缩提交边界可以重载并重建，所以图中不是“会话内永远冻结”。保留 seeded prompt 的 detached 压缩路径有例外，见下方来源。
2. 模型回合的输入组合系统提示与当前用户、助手和工具消息；模型据此提出工具调用，输入本身不会执行写入。更新也可能出现在当前消息里，所以“不换系统快照”不等于“本轮完全看不到新信息”。这里的消息容器是教学抽象，不表示磁盘中完整会话日志会无条件送入 API。
3. 前台调用与有条件的后台 review 可提出知识修改。修改通过内置 memory / skill_manage 的检查、审批与保存路径；图没有表示所有 Skill 批量和插件分支。
4. 允许或批准后的短事实可以写回内置记忆，流程知识可以写回 Skill 文件。需要批准的提议先进入 pending，批准后再提交并检查结果。审批门禁在处理动作前拒绝时，目标知识不会提交；执行过程中报错则须读回核对。记忆工具会先修改内存再写文件，Skill 的安全扫描也可能发生在落盘之后，所以一次报错或写后扫描拒绝可能留下变化，需要检查保存与回滚的实际结果。
5. Skill 内容经 `skill_view` 按需读取进入工具结果，而不是所有长文常驻系统提示。默认加载还可能发生预处理与依赖激活；本图只表达内容可见性，不保证读取无副作用。
6. review 不是每轮必然执行。无人值守后台替换或删除旧记忆有额外暂存门禁；其工具白名单也可以被显式 extra_tools 配置扩充。

## 箭头证据

固定源码版本：[`NousResearch/hermes-agent@a9109b07f42685f88397008d0d5a6c3d481b3b28`](https://github.com/NousResearch/hermes-agent/tree/a9109b07f42685f88397008d0d5a6c3d481b3b28)，核对日期 2026-09-27；[MIT](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/LICENSE)。本图属于源码路径的教学简化，不是运行轨迹或完整架构。

- 记忆 → 快照：[提示块读取](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/agent/system_prompt.py#L515-L539)、[失效重载](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/agent/system_prompt.py#L804-L820)、[live / seeded 重建分支](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/agent/conversation_compression.py#L3144-L3188)。
- 提出修改 → 保存 / 暂存：[memory 入口](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/tools/memory_tool.py#L208-L250)、[Skill 写门禁](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/tools/skill_manager_tool.py#L618-L648)、[审批决策](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/tools/write_approval.py#L169-L193)。
- 报错后读回核对：[内存先更新再落盘](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/tools/memory_tool_store.py#L245-L274)、[Skill 写后扫描与恢复](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/tools/skill_manager_tool.py#L350-L369)。
- Skill → 当前输入的工具结果：[skill_view](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/tools/skills_tool.py#L573-L693)。
- review 条件与额外门禁：[触发段](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/agent/turn_finalizer.py#L734-L763)、[无人值守删除暂存](https://github.com/NousResearch/hermes-agent/blob/a9109b07f42685f88397008d0d5a6c3d481b3b28/tools/memory_tool.py#L167-L204)。

图不覆盖全部会话恢复、外部 memory provider、审批界面、sandbox 或模型参数训练；源码示意不等于运行验证。

## 生成与核验

`build.py` 通过仓库共用 Scene builder 生成原生 `.excalidraw`。SVG / 4× PNG 使用 excalidraw-agent 的固定原生 renderer 导出，不能用手写 SVG 替代导出。

正文已完成本轮独立源码抽样二审，图稿已导出并检查 PNG 与 PDF 实页，记录见[新增系统审查](../../docs/reviews/2026-09-27-new-systems-review.md)与[PDF 专项审查](../../docs/reviews/2026-09-27-expansion-pdf-review.md)。这些检查不代替实际运行验证。MCP 若展示，字体可能与仓库导出不同，交互画布必须单独验收，不以 checkpoint 成功替代。
