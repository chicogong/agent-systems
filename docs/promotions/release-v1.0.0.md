# 《图解 Agent 系统》v1.0.0 发布说明 (Release Notes)

> **版本代号**：The Architecture Blueprint（架构蓝图）  
> **在线阅读**：[https://books.aimake.cc/](https://books.aimake.cc/)  
> **开源仓库**：[https://github.com/chicogong/agent-systems](https://github.com/chicogong/agent-systems)  
> **开源协议**：正文与图稿采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)，代码采用 MIT

---

经过持续打磨与来自一线工程师的严格验证，《图解 Agent 系统》正式发布 **v1.0.0** 正式版！

本书旨在为广大开发者、学生与架构师提供一份**拒绝玄学调优、深入工程底层物理机制**的现代化 AI Agent 系统图解指南。

---

## 核心版本亮点

### 1. 40 组独创 Excalidraw 矢量架构图（全量开源可二次编辑）
- **一图解一问**：从最小 Agent Loop 闭环推进、上下文漏斗、前缀缓存经济学，到沙箱生命周期与 A2A 协议栈，全面拆解黑盒；
- **全格式支持**：提供高清矢量 SVG、深色模式自适应排版、以及支持在浏览器中一键打开二次编辑的 `.excalidraw` 原始画板文件。

### 2. 16 大核心机制专题 + 10 秒心智模型卡
- 涵盖 Agent Loop、前缀缓存（KV Cache）、上下文与记忆、沙箱隔离、MCP 协议演进、A2A 跨代理协同、中断恢复、评价与观测等 16 个核心工程切面；
- 每章标配 **「10 秒心智模型（Mental Model）」**：一句话直觉比喻 + 核心物理公式 + 致命反模式警示，快速建立准确工程直觉。

### 3. 16 个工业级开源系统源码锁定剖析
- 深度拆解 Pi、Codex、OpenCode、Letta、Hermes、Qwen Code、MiMo Code、Mem0、LangGraph、OpenHands、Browser Use 等主流开源框架；
- 全书 **109 处源码引用全部严格锁定在固定 40 位 Git Commit 哈希上**，拒绝随上游版本漂移的空中楼阁。

### 4. 6 组零依赖本地/浏览器交互式实验台
- **在线单步回放**：无需配置 Python 环境或 API Key，在网页端单步点按即可透视 Agent 状态机流转；
- **本地确定性复现**：纯 Python 标准库编写的 6 组实验脚本，几毫秒内即可在本地复现前缀缓存击穿对比、丢失回执查账与沙箱越权拦截。

### 5. 生产级参考脚手架 (`examples/production-starter/`)
- 包含五层缓存排版、宿主审批门禁、防上下文腐化截断、以及水位线分段压缩的完整参考实现；
- 零外部依赖，支持直接拷贝并适配至生产级自主智能体系统。

---

## 完整内容目录导航

1. **机制图解**：[docs/concepts/](https://books.aimake.cc/concepts/)
2. **系统拆解**：[docs/systems/](https://books.aimake.cc/systems/)
3. **架构对照**：[docs/comparisons/](https://books.aimake.cc/comparisons/)
4. **交互实验**：[docs/labs/](https://books.aimake.cc/labs/)
5. **生态书单**：[docs/comparisons/recommended-reading-and-ecosystem.md](https://books.aimake.cc/comparisons/recommended-reading-and-ecosystem)
6. **工程脚手架**：[examples/production-starter/](https://github.com/chicogong/agent-systems/tree/main/examples/production-starter)
