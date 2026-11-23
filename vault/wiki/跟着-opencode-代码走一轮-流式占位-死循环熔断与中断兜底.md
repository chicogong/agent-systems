# 跟着 OpenCode 代码走一轮：流式占位、死循环熔断与中断兜底

> Synthesized concept page maintained by Aimake LLM Wiki.

## Key Evidence & Provenance

### Source Snapshot (2026-11-22)
- **Origin**: `/Users/haorangong/Github/chicogong/experiments/agent-systems/docs/systems/opencode/code-walkthrough.md`
- **SHA-256**: `552a71d6851dcfb8` · Raw: [[../raw/2026-11-22-跟着-opencode-代码走一轮-流式占位-死循环熔断与中断兜底.md|2026-11-22-跟着-opencode-代码走一轮-流式占位-死循环熔断与中断兜底.md]]
- 如果让你手写一个接收大模型流式工具事件的状态机，最容易漏掉三个边界：流式参数分十几个增量分片到达时怎么避免重复建单？模型鬼打墙连续五次用一模一样的参数调同一个工具时怎么刹住车？网络断流或用户强退的那一瞬间，卡在半空中的 `pending` 和 `running` 调用由谁来善后？
- 下面我们沿着 `packages/opencode/src/session` 里的真实事件流向，把这整条状态机链路从头拆到尾：
- SessionPrompt.prompt(input)
- └─► 落盘用户消息 → loop() / SessionRunState.ensureRunning → runLoop()
- └─► 选定 Agent 与模型 → SessionTools.resolve(挂载前后置插件钩子) → SessionProcessor.process()
