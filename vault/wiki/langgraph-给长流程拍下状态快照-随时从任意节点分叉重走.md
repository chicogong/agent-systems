# LangGraph：给长流程拍下状态快照，随时从任意节点分叉重走

> Synthesized concept page maintained by Aimake LLM Wiki.

## Key Evidence & Provenance

### Source Snapshot (2026-11-22)
- **Origin**: `/Users/haorangong/Github/chicogong/experiments/agent-systems/docs/systems/langgraph/README.md`
- **SHA-256**: `480957ac503bc7f7` · Raw: [[../raw/2026-11-22-langgraph-给长流程拍下状态快照-随时从任意节点分叉重走.md|2026-11-22-langgraph-给长流程拍下状态快照-随时从任意节点分叉重走.md]]
- 当一个 Agent 任务长达十几步——比如先抓取财报、清洗表格、跑核对规则，最后生成投资备忘录——最怕的不是某一步算错，而是**第 9 步提示词没调好，你却不得不从第 1 步把前面抓数据、跑工具的钱和时间重新烧一遍**。又或者，流程走到“即将向客户发送邮件”这一步需要停下来等人工审批，进程重启后怎么精确接回刚才停下的那条边？
- 只靠追加聊天记录（JSONL 消息列表）很难优雅解决这类问题，因为你需要的不是“重读一遍聊天记录”，而是**把整个执行图在某一拍的内存状态完整冻结下来，随时能原位唤醒，甚至拨回旧版本改一个变量走出平行分支**。这就是 LangGraph（基于 Pregel 图执行模型）里 `Checkpoint`（状态快照）的设计初衷。
- 可编辑图源 · PNG 预览 · 图的文字版
- 在 LangGraph 中，工作流被表达为一张由节点（Node）与通道（Channel）组成的图。每走完一个执行拍（Superstep），快照存储组件（`checkpointer`）就会沿同一条任务主线（`thread_id`）存下一份版本快照。打开对外暴露的 `StateSnapshot`，最核心的就是四个字段（`StateSnapshot` 定义）：
- StateSnapshot
