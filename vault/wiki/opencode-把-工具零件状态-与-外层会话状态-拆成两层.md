# OpenCode：把「工具零件状态」与「外层会话状态」拆成两层

> Synthesized concept page maintained by Aimake LLM Wiki.

## Key Evidence & Provenance

### Source Snapshot (2026-11-22)
- **Origin**: `/Users/haorangong/Github/chicogong/experiments/agent-systems/docs/systems/opencode/README.md`
- **SHA-256**: `0d1350a25c045617` · Raw: [[../raw/2026-11-22-opencode-把-工具零件状态-与-外层会话状态-拆成两层.md|2026-11-22-opencode-把-工具零件状态-与-外层会话状态-拆成两层.md]]
- 做过流式编码 Agent 界面的工程师，大多被两类状态错乱折磨过：第一，大模型正在慢吞吞地流式吐出一段两百行的改文件 JSON 参数，整整八秒钟里工具根本还没开始跑，界面却只挂着一个笼统的「忙碌中」，用户根本分不清是网络卡死了还是命令正在执行；第二，某次 `read` 读到了不存在的路径返回报错，或者用户半途按下了取消键——如果把单个工具状态和整场会话绑死在
- OpenCode 的解法非常干脆：把状态拆成互不越界的两层——微观层为每一次工具调用单独建一张挂在助手消息下的零件单 `ToolPart`（流转于 `pending / running / completed / error` 四态），宏观层用独立的 `SessionStatus`（`busy / retry / idle`）表达整场会话的心跳。**单个零件
- 图的文字版 · 可编辑图源 · 关键代码导读
- 在流式协议下，大模型并不是一口气把完整工具调用扔过来的，而是先发调用编号 `callID` 与工具名，再一段段往外挤 JSON 参数增量块。如果等参数收齐才建记录，这几秒钟在消息历史里就是一片空白。
- 因此 OpenCode 把单次调用的进度拆成四个精确阶段，并始终凭 `callID` 对号入座（见建立记录、记录运行、写入结果与标记中断）：
