# Letta Code：分层记忆文件系统与提示重编译时序

> Synthesized concept page maintained by Aimake LLM Wiki.

## Key Evidence & Provenance

### Source Snapshot (2026-11-22)
- **Origin**: `/Users/haorangong/Github/chicogong/experiments/agent-systems/docs/systems/letta/README.md`
- **SHA-256**: `b7a23e467ed7f625` · Raw: [[../raw/2026-11-22-letta-code-分层记忆文件系统与提示重编译时序.md|2026-11-22-letta-code-分层记忆文件系统与提示重编译时序.md]]
- 给编码助手加长期记忆时，最容易踩中两个相反的坑：如果把编码规范、排障手册和历史讨论全塞进系统提示，几千行低频细节会迅速挤占上下文窗口，不仅抬高每轮首字延迟，还会冲淡真正关键的约束；反过来，如果把所有经验都扔进外部检索库，聊到第 30 轮时，Agent 又可能因为某次检索没命中，突然忘掉“本项目一律用 `pnpm` 严禁 `npm`”这种每轮必守的底线。更让人
- Letta Code 用 **MemFS**（记忆文件系统）解决这组矛盾：它直接用**目录结构定义知识的驻留层级**，让高频约束常驻系统提示、长篇资料按需读取、早期对话靠历史检索（recall）打捞，并用 Git 提交与显式的提示重编译把“文件落盘”和“上下文生效”拆成受控的两步。下面聚焦 **local MemFS v1** 配置，拆解这套分层设计与生效时
- 可编辑图源 · PNG 预览 · 图的文字版
- 按阅读顺序跟代码
- 如果把模型的上下文窗口比作容量有限的高速缓存，Letta Code 在 local MemFS v1 下把知识拆成了三档成本截然不同的存储层：
