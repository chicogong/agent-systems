# mini-SWE-agent：砍掉一切花哨框架后，Agent 最本质的骨架是什么

> Synthesized concept page maintained by Aimake LLM Wiki.

## Key Evidence & Provenance

### Source Snapshot (2026-11-22)
- **Origin**: `/Users/haorangong/Github/chicogong/experiments/agent-systems/docs/systems/mini-swe-agent/README.md`
- **SHA-256**: `bd36d35e40b214fe` · Raw: [[../raw/2026-11-22-mini-swe-agent-砍掉一切花哨框架后-agent-最本质的骨架是什么.md|2026-11-22-mini-swe-agent-砍掉一切花哨框架后-agent-最本质的骨架是什么.md]]
- 读多了动辄几万行代码的重型 Agent 框架——各种有向无环图（DAG）调度器、三十多种自定义改文件工具、层层嵌套的事件总线——开发者很容易产生一种错觉：好像不搭一套庞大的脚手架，大模型就连修个 Bug 都寸步难行。直到你在跑大规模基准测试时被自定义 `search_replace` 解析器折磨到崩溃，或者发现框架里的布尔状态位（`is_finished`、
- SWE-agent 团队开源的 **mini-SWE-agent** 做了一次酣畅淋漓的减法实验：核心类 `DefaultAgent` 只有**不到两百行 Python 代码**，不造任何专用文件编辑工具（全靠标准 bash），不设独立状态机，整个运行时从头到尾只围绕**一份线性的 `self.messages` 消息列表**旋转——任务是消息、命令输出是消
- 文字版 · 可编辑图源 · 关键代码导读
- 打开 `DefaultAgent.run()`，你会惊讶于它的直白：先把系统提示词和用户任务塞进 `self.messages`，然后跑一个 `while` 循环，每一轮 `step()` 只做两件事（见循环与请求模型与执行动作）：
- 1. **问模型**（`query`）：检查预算未超标后，把整份 `self.messages` 发给模型，把模型返回的 `assistant` 回复追加到列表末尾。
