# Jev 机制旁栏来源记录

- **对象与核对日期：** TypeSafe 的 Jev／System One 托管模型与公开文档；2026-09-23 核对。正文是[机制旁栏](../docs/concepts/jev-and-system-one.md)，不是开源 Agent 的固定源码剖面。
- **取得方式：** 直接读取 TypeSafe 的发布文和官方文档 Markdown 页面；未调用 API、未取得输出样本、未审计服务端或模型权重。
- **厂商定位：** [发布文](https://typesafe.ai/blog/introducing-system-one-models-and-jev)称 Jev 在早期访问中提供结构化概率判断，并给出速度、成本、校准与无类型错误等主张。[架构文档](https://docs.typesafe.ai/concepts/how-to-build-with-system-one)明确将它与会自主选择下一步的 Agent 区分，主张控制流、确定性规则和副作用归代码所有。这些是**文档声明**，不是独立测量或内部实现事实。
- **接口证据：** [快速入门](https://docs.typesafe.ai/introduction/quickstart)展示 `POST /v1/systemone`、`state`、`model` 和 `questions`；[Noul](https://docs.typesafe.ai/primitives/noul)、[Choice](https://docs.typesafe.ai/primitives/choice)说明返回概率、选项和置信度；[置信度说明](https://docs.typesafe.ai/confidence)区分概率与信心。[模型页](https://docs.typesafe.ai/models)在核对时列出 `jev-1.13.0`，并说明别名可变及英文表现较强。以上页面均会更新，版本陈述限于核对日。
- **应用案例：** [Skill suggestion cookbook](https://docs.typesafe.ai/cookbooks/skill_suggestion)展示两次请求筛选并建议 Skill。其 488 个请求的错误率表和效果结论是**厂商报告**，没有本书的独立复现；旁栏不引用数字作普遍效果承诺。
- **失败边界：** [Jev 1.13 jaggedness](https://docs.typesafe.ai/model-jaggedness/jev-1.13)是厂商公开的版本特定已知问题，涉及字面理解、计数、日期、间接推理、无关长状态、对抗内容和跨问题形式不满足直觉不变量。类型受限不能推出语义正确。发布文中的“不能幻觉”按输出类型／选项约束理解，不扩展为零误判。
- **工程推断与未知：** 旁栏的阈值、人审和 Skill 提示代码是教学设计，不是 TypeSafe 的实测或官方推荐阈值。实际校准程度、中文场景准确率、生产延迟、服务端实现与模型权重均未核实；上游 SDK 开源也不说明模型权重或服务端开源。
