# 快思考路由与 System-1 模型：小模型做有界判断，宿主握最终执行权

> Synthesized concept page maintained by Aimake LLM Wiki.

## Key Evidence & Provenance

### Source Snapshot (2026-11-22)
- **Origin**: `/Users/haorangong/Github/chicogong/experiments/agent-systems/docs/concepts/jev-and-system-one.md`
- **SHA-256**: `d12c7d28556c1aa0` · Raw: [[../raw/2026-11-22-快思考路由与-system-1-模型-小模型做有界判断-宿主握最终执行权.md|2026-11-22-快思考路由与-system-1-模型-小模型做有界判断-宿主握最终执行权.md]]
- 当工作区里的 Skill 攒到五六十个、工具列表越挂越长时，请求路由就会卡进两难死角：如果每轮对话都把几十份候选说明全量塞给重型推理大模型，首字延迟被拖慢，Token 账单成倍上涨；如果退回手写正则和关键词匹配，用户只要随口说一句“把昨天那份架构汇报最后两页砍掉”，没出现“修改幻灯片”这几个字，规则就当场漏判。
- 认知心理学把人的思维拆成直觉迅速的“快思考”（System 1）与审慎推演的“慢思考”（System 2）。TypeSafe 提出的 **Jev** 模型正是把这一分工搬进了 Agent 架构：在昂贵的主推理模型（System 2）启动前，先让一个轻快、输出严格受限的 **System-1 小模型**做有界分类或是非打分；而**走哪条分支、挂不挂 Skill
- 可编辑图源 · PNG 预览 · 图的文字版 · 背景参考：发布介绍 · 架构说明
- 在复杂的 Agent 流水线里，把“窄域意图分流”和“长程复杂推理”拆给不同角色，本质上是在延迟、成本与可控性之间做工程解耦：
- | 角色 | 核心职责 | 明确不做的事 |
