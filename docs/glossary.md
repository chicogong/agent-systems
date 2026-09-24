# 术语：同一个词别混用

本书把运行时的可见输入、应用存储、模型生成的指令和外部资源分开命名。以下是本书的**工作定义**，不是声称所有项目都采用同一术语或实现。

| 术语 | 在本书中的含义 | 继续阅读 |
| --- | --- | --- |
| Agent | 能围绕目标，在反馈中选择后续动作的运行系统；具体边界由宿主实现决定 | [与工作流的区别](concepts/agent-workflow-multiagent.md)、[Pi 分层](systems/pi/README.md) |
| 工作流 | 由预设步骤和分支组织的过程；其中可以包含 Agent 决策 | [与 Agent 的区别](concepts/agent-workflow-multiagent.md) |
| 多 Agent / 多执行者 | 任务拆给多个有独立职责的执行者，还需定义交接、合并与冲突处理；与下一步控制权是不同维度 | [控制权与数量](concepts/agent-workflow-multiagent.md) |
| Agent loop | 在模型请求、工具结果和继续/结束判断之间迭代的控制流程 | [Pi 代码导读](systems/pi/code-walkthrough.md) |
| Harness（宿主运行器） | 位于模型外的运行与控制层；组织模型调用、工具路由、上下文和权限等职责，不等于模型本身 | [五层职责](concepts/model-harness-cli-mcp-skill.md) |
| CLI | 命令行交互界面；不是 Agent 的全部运行机制，换产品的 CLI 也往往同时换了其他层 | [五层职责](concepts/model-harness-cli-mcp-skill.md) |
| Tool | 带输入、执行与结果的能力接口；模型提出调用不等于已经获准执行 | [Codex 审批](systems/codex/README.md) |
| Observation | 动作后提供给系统的结果或状态；它不必然准确，也不等于成功验收 | [OpenHands 事件](systems/openhands/README.md) |
| 当前上下文 | 一次模型请求实际提交的指令、消息和材料 | [上下文与记忆](concepts/context-vs-memory.md) |
| 会话记录 | 宿主保留的消息或事件历史，不保证全量进入下一次模型请求 | [状态对照](comparisons/four-kinds-of-state.md) |
| 压缩摘要 | 将选定历史转写为更短表示的产物；是否进入下一轮由宿主决定 | [上下文与记忆](concepts/context-vs-memory.md) |
| 长期记忆 | 跨轮次或跨任务保留、可能需检索和注入的状态或知识 | [Letta Code](systems/letta/README.md)、[Mem0](systems/mem0/README.md) |
| Checkpoint（执行状态） | 一个可定位的图执行状态版本，包含继续执行所需的状态与位置；不等同语义记忆 | [LangGraph](systems/langgraph/README.md) |
| `checkpoint.md`（上下文续接材料） | 从历史提炼给后续模型窗口使用的任务与线索，可能遗漏或保留旧状态；虽同名，不保证恢复原执行状态 | [MiMo Code](systems/mimo-code/README.md) |
| 审批 | 某个动作开始前的授权决定；不保证运行中隔离或结果正确 | [审批与沙箱](concepts/approval-vs-sandbox.md) |
| 沙箱/隔离 | 对执行期间可访问资源的边界；不替代用户意图确认 | [审批与沙箱](concepts/approval-vs-sandbox.md) |
| Skill | 按需读取的任务指导及配套文件，不等于可执行插件本身 | [扩展层次](concepts/extensibility-layers.md) |
| Extension | 由宿主加载的扩展代码或钩子；其权限取决于宿主和安装环境 | [Pi 扩展](systems/pi/extensions-and-skills.md) |
| MCP | 宿主与外部能力交换工具、资源等的协议，不等于 Skill 文件格式 | [扩展层次](concepts/extensibility-layers.md) |
| 源码事实 / 工程推断 | 前者能在固定版本定位到实现；后者是基于证据的解释，必须单独标记 | [来源规则](../sources/README.md) |

读项目图时先问“这是哪个版本、哪条路径、谁保存状态、谁实际执行”。若一幅图没回答这些问题，回到对应文章的范围与来源，不要用通用术语替它补上不存在的机制。

## 读完之后

可以从自己熟悉的一次真实任务反向检验本书：模型提出了什么动作，宿主在哪一步决定是否执行，结果如何进入下一轮，以及中断后哪些状态还能找回。找到这些位置，再去比较另一套系统，差异通常比功能列表更清楚。

本书会继续补齐机制专题、代码导读和横向对照。已有章节锚定各自的源码版本；上游更新时先核对事实、标明变化，再修正文图。欢迎从可复现的源码定位、图文不一致或读者不易理解的具体段落提出改进。构建出的 PDF 是某一时点的阅读快照，不代表所述项目的最新行为。
