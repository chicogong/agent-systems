# 动手：用本地 HTTP 观察回执与查询

> Synthesized concept page maintained by Aimake LLM Wiki.

## Key Evidence & Provenance

### Source Snapshot (2026-11-22)
- **Origin**: `/Users/haorangong/Github/chicogong/experiments/agent-systems/docs/labs/http-receipt.md`
- **SHA-256**: `88255a38ae2a8b75` · Raw: [[../raw/2026-11-22-动手-用本地-http-观察回执与查询.md|2026-11-22-动手-用本地-http-观察回执与查询.md]]
- 如果说上一节内存版练习是静态沙盘，这一节就是真刀真枪的**本机 TCP/HTTP 显微镜**——程序会在本机 `127.0.0.1` 拉起真实的多线程 HTTP 服务，用真实的 `socket.timeout` 掐断连接，让你在终端里亲眼目睹分布式系统里最容易坑惨 Agent 开发者的两幕奇观：
- 1. **两个一模一样的 404，背后藏着两种完全不同的暗渡陈仓**：在 `lookup_lag` 和 `late_commit` 模式下，客户端先遇到 `POST` 读超时，紧接着开新连接发 `GET` 对账，两次都收到了冷冰冰的 `404 Not Found`！可等服务收尾清理后翻开底账（`observer_after_cleanup`），**账本里竟然
- 2. **同样是超时后重发请求，带原 ID 安全拿回原结果，篡改内容却当场撞上 409 冲突**：你会亲眼看到服务端如何在同一把锁里守住幂等账本（`200 replayed=true` 对比 `409 Conflict`），既防住并发线程撞车，又揪出篡改参数的同名重试。
- 运行仅需 Python 3.10+ 标准库，全程只监听本机回环地址 `127.0.0.1`、用完自动关闭，不写磁盘、不连外网（请保持 `127.0.0.1`，不要改成对外暴露的 `0.0.0.0`；标准库 `http.server` 不适合生产服务）。
- 在仓库根目录先跑通正常模式、单测套件与超时对账模式：
