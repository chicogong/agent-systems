# MiMo Code 固定来源记录

- **规范上游：** <https://github.com/XiaomiMiMo/MiMo-Code>。
- **固定提交：** `a273d3450ee05ba5163320eae59d7716b778e480`；2026-09-23 使用 `git ls-remote` 确认 HEAD，并以 `git clone --depth 1 --filter=blob:none` 获取，再由本地 `git rev-parse HEAD` 核对。
- **许可：** 固定版根目录 `LICENSE` 为 MIT；含 2026 MiMo Code/Xiaomi Corporation 与 2025 opencode 版权行。这里只记录上游许可事实，不代替本书发布前的第三方内容许可复核。
- **维护状态：** 核对时官方仓库可访问，HEAD 如上；不由此推断 release 二进制与该提交一致。
- **官方文档：** [设计文章](https://mimo.xiaomi.com/blog/mimo-code-long-horizon)（网页署名日期 2026-06-10；文档可变）、[Sessions & Context](https://mimo.xiaomi.com/mimocode/sessions)（可变）。文章的性能、阈值示例与产品承诺均按“文档声明”处理。
- **源码切面：** `packages/opencode/src/session/{prompt,prune,checkpoint,checkpoint-paths,checkpoint-templates,checkpoint-retry,message-v2,compaction}.ts`、`packages/opencode/src/agent/prompt/checkpoint-writer.txt`、`packages/opencode/src/session/llm.ts`。入口是 `SessionPrompt` 的循环；跟读 writer 触发、子会话生成、文件/watermark、重建材料与边界、溢出退化。
- **证据等级：** 正文函数与条件分支是固定版静态源码事实；“以额外计算换接力点”和“原话降低摘要漂移风险”是工程推断；文章的效果数字为厂商声明；本稿没有运行观察。
- **明确未知：** 发布二进制版本映射、真实 provider 长任务成功率、writer 产物语义质量、writer 普通失败或进程崩溃时原地编辑文件与 DB watermark 的一致性、跨平台行为、所有配置/子 Agent 分支。
- **本书复跑的有限测试（2026-09-24）：** 在固定提交的稀疏检出中，从仓库目录外执行 `bun test /absolute/path/to/packages/opencode/test/session/checkpoint-align.test.ts`，Bun 1.3.5 报告 7/7 通过。它只覆盖 [`alignToNonToolResultUser`](https://github.com/XiaomiMiMo/MiMo-Code/blob/a273d3450ee05ba5163320eae59d7716b778e480/packages/opencode/src/session/checkpoint-align.ts) 将增量消息起点对齐到非工具结果 user 消息的纯函数；没有启动 writer、数据库、模型或重建循环。完整恢复链仍需依赖安装、mock/fault-injection 和真实 provider 分层验证，不能把这 7 个用例称为长会话恢复实测。
