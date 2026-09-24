# 横向对照

[返回首页](../../README.md)

这里按机制比较项目，不做“最佳 Agent”总榜。每篇对照先定义同一个问题和比较维度，再引用固定版本的系统剖面；证据不足的位置留空。

计划中的首批问题：

- **Agent loop**：工具调用、观察与停止条件由谁控制？
- **上下文与记忆**：会话记录、压缩摘要和长期记忆怎样进入模型输入？
- **权限与恢复**：危险动作在哪里拦截，未知结果怎样对账？
- **完成判断**：测试、轨迹、文件产物和用户接受分别证明什么？

[一轮工具调用后，谁决定下一步？](loop-and-stop.md)以同一个观察点对照 Pi、mini-swe-agent、OpenCode 和 Kimi Code 的循环与停止契约。它比较的是各自固定源码的一条路径，不是同任务实测。

[存下来了，下一轮就一定能看见吗？](persisted-vs-visible.md)对照 Pi 与 Letta Code 各一条固定源码路径。

状态专题另有[四种常被叫作“记忆”的状态](four-kinds-of-state.md)：Pi、Letta Code、Mem0 与 LangGraph 的存储对象和进入模型的方式并不一样。

[同一测试命令，谁让它执行？](claude-code-codex.md)对照 Claude Code 的官方公开行为和 Codex 的固定源码路径。双方证据粒度不同，因此只比较用户能作出的控制选择，不推断 Claude Code 未公开的内部实现。

[批准过了，超时后能重试吗？](permission-and-recovery.md)把动作前批准、本地状态恢复和外部结果对账分开，对照 Codex、OpenHands、OpenCode 与 LangGraph 的固定源码切面；图中的部署超时是教学情境，不是四者同环境实测。

[Agent 说“完成”时，哪些证据够用？](completion-and-evidence.md)用同一教学任务区分循环结束、工具结果、文件改动、测试断言、任务边界和用户验收，再对照 Pi、mini-swe-agent、OpenCode 与 Kimi Code 的固定源码记录。
