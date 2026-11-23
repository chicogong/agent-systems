# Agent、工作流与多 Agent：安排任务的三种办法

> Synthesized concept page maintained by Aimake LLM Wiki.

## Key Evidence & Provenance

### Source Snapshot (2026-11-22)
- **Origin**: `/Users/haorangong/Github/chicogong/experiments/agent-systems/docs/concepts/agent-workflow-multiagent.md`
- **SHA-256**: `74557c49ca0ceaf1` · Raw: [[../raw/2026-11-22-agent-工作流与多-agent-安排任务的三种办法.md|2026-11-22-agent-工作流与多-agent-安排任务的三种办法.md]]
- 团队第一次把大模型搬进工程系统时，最容易掉进两个相反的深坑：要么把本来三步 `if/else` 就能稳定跑完的每日发票提取，硬塞给一群“自主协商的多 Agent”，结果延迟翻了十倍、每次跑出来的格式还不一样；要么把横跨十几个模块的线上故障排查全堆进同一个对话窗口，翻到第 20 个日志文件时，满屏中间输出早就把最初的排障目标冲没了。
- 之所以会选错架构，是因为很多人把“**下一步由谁决定**”和“**有几个独立执行窗口**”混成了一件事。只要把这两个正交维度拆开看，工作流（Workflow）、单 Agent 与多执行者（Multi-Agent）各自的甜点区一目了然。
- 图的上半部分回答**控制流归属**（代码写死轨道，还是模型动态选路），下半部分回答**执行上下文切分**（单兵推进，还是分头处理再汇总）。一条固定工作流里完全可以并行调用多个模型节点；反过来，一个自主 Agent 也完全能独自闭环复杂任务。各条路径的逐步对照见图的文字版。
- 借用 Anthropic《Building Effective Agents》对 Workflow 与 Agent 的经典界定：**Workflow** 是通过预定义代码路径编排大模型与工具的系统，而 **Agent** 则是由大模型动态决定推理过程与工具使用方式的系统；至于其中的协调者-工作者（Orchestrator-Workers）模式，则是在人数维度
- 我们把同一个真实研发任务——**上线前审查一次涉及多模块的变更请求**（提取配置改动、排查接口兼容性风险、给出发布建议）——放进三种架构里跑一遍，立刻就能看出取舍：
