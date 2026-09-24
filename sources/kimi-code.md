# Kimi Code 来源记录

- **对象与版本**：新版 [`MoonshotAI/kimi-code`](https://github.com/MoonshotAI/kimi-code) 的完整提交 [`75a894e9ad5e8d49509664b3daaa1bbc9bb39432`](https://github.com/MoonshotAI/kimi-code/tree/75a894e9ad5e8d49509664b3daaa1bbc9bb39432)（上游提交日期 2026-06-09；本书核对 2026-09-23）。旧 `kimi-cli` 不是本篇对象。
- **取得方式**：通过 GitHub 提交页与 `raw.githubusercontent.com` 读取固定提交的文件；未克隆或运行上游项目。上游 [README](https://github.com/MoonshotAI/kimi-code/blob/75a894e9ad5e8d49509664b3daaa1bbc9bb39432/README.md) 将其定位为终端编码 Agent；[AGENTS.md](https://github.com/MoonshotAI/kimi-code/blob/75a894e9ad5e8d49509664b3daaa1bbc9bb39432/AGENTS.md) 的模块地图将 `agent-core` 称为统一引擎。
- **许可与维护**：[固定版 LICENSE](https://github.com/MoonshotAI/kimi-code/blob/75a894e9ad5e8d49509664b3daaa1bbc9bb39432/LICENSE) 为 MIT；上游仓库目前可访问，当前发布二进制与该提交的对应关系未核查。正式发布前仍需人工许可与链接终审。
- **核心源码**：[`packages/agent-core/src/agent/turn/index.ts`](https://github.com/MoonshotAI/kimi-code/blob/75a894e9ad5e8d49509664b3daaa1bbc9bb39432/packages/agent-core/src/agent/turn/index.ts) 的 `prompt/steer`（120–180）、取消与缓冲（205–279）、`runOneTurn`（415–510）、`runStepLoop` 与权限回调（563–718）；[`packages/agent-core/src/loop/run-turn.ts`](https://github.com/MoonshotAI/kimi-code/blob/75a894e9ad5e8d49509664b3daaa1bbc9bb39432/packages/agent-core/src/loop/run-turn.ts) 的步数、工具续跑与停止检查（74–128）。
- **文档声明**：官方[会话](https://moonshotai.github.io/kimi-code/en/guides/sessions)与[子 Agent](https://moonshotai.github.io/kimi-code/en/customization/agents)文档仅列作后续阅读；本文不据此声称已审计持久化或上下文隔离。
- **证据等级**：主篇与图中的 `steer → 缓冲 → step 边界刷新 → 继续/停止` 为固定版**源码事实**；“互动性放在 step 边界”及等待时延的解释为**工程推断**；CLI 接线、实际延迟、发布版适用性为**未知**。无运行观察。
