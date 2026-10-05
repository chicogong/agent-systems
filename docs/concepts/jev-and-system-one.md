# Jev：让模型做判断，让程序安排后续动作

[返回机制目录](README.md) · [模型、Harness、CLI、Skill、MCP 的分工](model-harness-cli-mcp-skill.md) · [来源记录](../../sources/jev.md)

用户说“把昨天那份幻灯片的结尾改短一点”，程序需要判断该推荐“修改已有幻灯片”，还是“制作新幻灯片”。这类任务的答案范围比较小，但用户的表达方式很多。

TypeSafe 将 Jev 称为 *System One* 模型。程序给它当前材料和限定类型的问题，它返回判断及概率，再由程序决定下一步。可以把它看作工作流中的一个判断环节。[发布介绍](https://typesafe.ai/blog/introducing-system-one-models-and-jev) · [架构说明](https://docs.typesafe.ai/concepts/how-to-build-with-system-one)

## 输入材料，得到有限选项里的判断

在这个例子里，输入分成两部分：

- `state`，当前材料：用户请求，以及两个 Skill 的简短介绍。
- `questions`，需要回答的问题：这次是否需要 Skill，以及哪个候选更合适。

**Noul** 用于是非判断，返回“是”的概率。比如判断这条请求是否需要候选 Skill。**Choice** 用于从给定选项中选择，返回选项、各选项的概率和 confidence。

[快速入门](https://docs.typesafe.ai/introduction/quickstart) · [Noul](https://docs.typesafe.ai/primitives/noul) · [Choice](https://docs.typesafe.ai/primitives/choice)

流程可以写成：材料与问题 → 模型判断 → 程序检查 → 推荐方法或请人处理。

| 部件 | 在这个任务里做什么 |
| --- | --- |
| Jev | 判断请求更接近哪种已有选项 |
| 运行程序，也叫 Harness | 调用模型，处理概率、错误和权限 |
| Skill | 提供制作或修改幻灯片的方法与资源 |
| Agent | 结合用户任务和推荐方法，继续工作 |

TypeSafe 的 [Skill 推荐案例](https://docs.typesafe.ai/cookbooks/skill_suggestion)分两次请求筛选候选，最后把推荐交给 Agent。推荐是一条可忽略的建议，真正使用时仍由运行程序和 Agent 处理。

推荐提供工作方法，实际写入和外部动作仍走原有的授权流程。

## 概率怎样影响下一步

程序可以把结果分成三个区域：明确无需推荐时继续原流程，足够确定时给出建议，中间区域交给人检查。

这里的数值需要结合自己的样例测试。Choice 的 confidence 描述概率分布的集中程度；它没有直接表示“这个选项正确的概率”。Noul 的数值则描述模型对“是”的判断。两类输出要按各自含义使用。[置信度说明](https://docs.typesafe.ai/confidence)

例如“修改现有 PPT”可能被误选为制作新 PPT。选项格式是合法的，推荐内容却仍需要核对。因此调试时，既检查返回格式，也收集误选的具体请求。

## 可选深入：一段推荐 Skill 的代码

下面是本书的示意代码，没有调用过 API。`human_review` 和 `propose_to_agent` 需要应用自己实现；示例阈值只用于展示分支。接入真实服务会发送外部请求，先查看费用和数据处理规则，不要直接传入私人材料或密钥。

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
    with TypeSafeClient() as client:
        answers = client.system_one(
            model="jev-1.13.0",
            state=state,
            questions={
                "needs_skill": Noul(
                    instructions="这轮请求是否需要给定的任一 Skill？"
                ),
                "which": Choice(
                    instructions="若需要，哪项最贴合这轮请求？",
                    criteria=state["skills"],
                ),
            },
        ).answers

    need = answers["needs_skill"].noul
    choice = answers["which"]
    if need <= 0.20:
        return None                         # 继续原流程
    if need < 0.90 or choice.confidence < 0.80:
        return human_review(user_request)   # 请人检查
    return propose_to_agent(choice.choice) # 给 Agent 建议
```

模型超时、返回异常或候选失效时，应用也要安排停下或人工处理的分支。上线前，用目标任务的标注样例选择阈值，记录模型版本和误判情况。

## 适合放在哪里

Jev 适合选项有限、问题较小、结果便于复核的环节，例如请求路由、候选筛选和 Skill 提示。正文生成、长任务规划、精确计数和日期运算，应安排给适合这些工作的模型或代码。

厂商的 [jev-1.13 已知问题](https://docs.typesafe.ai/model-jaggedness/jev-1.13)列出了计数、日期比较、多层推理、无关材料过长和对抗内容等限制，也提示不同问题类型的概率不能直接套用同一门槛。[模型文档](https://docs.typesafe.ai/models)说明其英文表现最好，中文任务需要单独测试。

部署时固定模型版本，尤其在已经调过阈值的情况下。使用会变化的版本别名时，新版本上线后需要重新检查样例。

本章介绍的是厂商文档中的机制，没有独立测量性能，也没有验证上述中文示例的效果。可以先拿一组非敏感请求做人工标注，再决定是否适合放入自己的工作流。
