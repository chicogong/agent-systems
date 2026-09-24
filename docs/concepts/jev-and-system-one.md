# Jev：把一个判断交给模型，动作仍由代码决定

[返回机制目录](README.md) · [模型、Harness、CLI、Skill、MCP 的职责](model-harness-cli-mcp-skill.md) · [来源记录](../../sources/jev.md)

在一个已有 Agent 的工作流里，如何判断本轮该提示哪项 Skill？规则很容易因用户说法变化而漏判；让生成式模型自行加载，也会把判断和动作混在一起。TypeSafe 将 Jev 称为 *System One* 模型：输入 `state` 和预先定义类型的问题，返回限定形状的判断及概率，供程序继续处理。[发布文](https://typesafe.ai/blog/introducing-system-one-models-and-jev)和[架构文档](https://docs.typesafe.ai/concepts/how-to-build-with-system-one)均是厂商说明；本文没有调用 API 或独立复现其性能。

核心路径是：**状态 + 有类型的问题 → 概率／结构化判断 → 代码阈值或人工复核 → 动作**。状态可以是本轮请求和可用 Skill 的简短描述；问题可以是“本轮是否需要 Skill？”（`Noul`，返回“是”的概率）和“若需要，哪一项最合适？”（`Choice`，在给定选项中选择并返回概率分布）。[快速入门](https://docs.typesafe.ai/introduction/quickstart)展示了同一请求中的 `state`、`questions` 和 `answers`；[Noul](https://docs.typesafe.ai/primitives/noul)与[Choice](https://docs.typesafe.ai/primitives/choice)文档解释了两类输出。

| 部件 | 在这个例子里负责什么 |
| --- | --- |
| Jev 模型 | 对给定状态与问题作有界语义判断；不生成任意 Skill 名称或自己调用工具。 |
| Agent | 处理用户目标，可能在后续步骤参考建议；其后续行为不能由 Jev 的答案保证。 |
| Harness／运行器 | 收集状态、发起调用、实施阈值和权限策略，并决定是否把建议交给 Agent 或人。 |
| Skill | 被选择的工作方法与资源；即便被推荐，也不会自行执行或增加权限。 |

TypeSafe 的[官方 Skill 推荐案例](https://docs.typesafe.ai/cookbooks/skill_suggestion)用两次请求筛选候选，最后只给 Agent 一条**可忽略的建议**。它报告的错误率改进来自厂商自己的样本、模型和评测流程；不是本书的独立验证。下面只借用“是否需要 + 候选选择”的机制，改成更短的**示意代码**，不是该案例的复制、可直接部署的策略或实测结果：

```python
from typesafe_sdk import Choice, Noul, TypeSafeClient

def suggest_for_turn(user_request: str):
    state = {
        "request": user_request,
        "skills": {
            "slides-author": "从需求制作新的演示文稿",
            "slides-edit": "修改已有演示文稿",
        },
    }
    with TypeSafeClient(model="jev-1.13.0") as client:
        answers = client.system_one(
            state=state,
            questions={
                "needs_skill": Noul(
                    instructions="这轮请求是否需要使用给定的任一 Skill？"
                ),
                "which": Choice(
                    instructions="若需要 Skill，哪项最贴合这轮请求？",
                    criteria=state["skills"],
                ),
            },
        ).answers

    need = answers["needs_skill"].noul
    choice = answers["which"]
    if need <= 0.20:
        return None                         # 不提示 Skill
    if need < 0.90 or choice.confidence < 0.80:
        return human_review(user_request)   # 由宿主实现的复核入口
    return propose_to_agent(choice.choice) # 建议；宿主仍核对权限与适用性
```

`human_review` 和 `propose_to_agent` 是示意中的宿主函数。`0.20／0.90／0.80` **只是教学阈值**，不能从一次模型输出推导出来；实际需要用目标任务的标注样本、误判代价和版本固定的模型调校。`Choice.confidence`描述选项概率分布的集中程度，不等于“这次选择正确的概率”；`Noul.noul`是对所问“是”的概率，也不是动作许可。[置信度说明](https://docs.typesafe.ai/confidence)要求按应用数据设门槛。模型超时、返回异常、候选已失效时，宿主也要有明确的停下或人工处理路径。

**边界在哪里？** 输出符合预设类型，只约束“能返回什么形状”，不保证选中的 Skill 在语义上正确，更不保证之后的 Agent 正确执行。比如“修改现有 PPT”被误分到 `slides-author`，结构仍完全合法。TypeSafe 的[已知问题](https://docs.typesafe.ai/model-jaggedness/jev-1.13)还列出 `jev-1.13` 对计数、日期比较、多层间接推理、冗长无关状态及对抗内容的局限；确定性的计数与日期运算应由代码完成。它也指出，对同一意思换一种问题类型或取反提问，概率不必满足直觉中的算术关系。因此阈值不能跨问题类型直接搬用。

适合把**选项有限、问题可拆小、错误可复核**的判断嵌入已有软件，例如路由、筛选、Skill 提示或结果打标。不适合要求模型自行规划长任务、生成正文或代码、做精确算术，也不适合把一次高分当作高风险动作的唯一依据。官方[模型页](https://docs.typesafe.ai/models)说明 Jev 目前以英文表现最好，非英文内容需单独测试；示意中的中文输入因此尤其不能视为已验证效果。版本别名会移动，调过阈值的部署应固定模型版本并记录返回的版本号。

**自测**

1. `Choice` 返回了 `slides-edit` 且类型正确，是否证明本轮一定该加载它？为什么？
2. `needs_skill=0.63` 时，谁决定去人工复核，而不是直接加载？
3. 需求要比较两个日期的先后，应该把哪一步留给代码？
