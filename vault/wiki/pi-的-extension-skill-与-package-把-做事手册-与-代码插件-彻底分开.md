# Pi 的 Extension、Skill 与 Package：把「做事手册」与「代码插件」彻底分开

> Synthesized concept page maintained by Aimake LLM Wiki.

## Key Evidence & Provenance

### Source Snapshot (2026-11-22)
- **Origin**: `/Users/haorangong/Github/chicogong/experiments/agent-systems/docs/systems/pi/extensions-and-skills.md`
- **SHA-256**: `3fb6b900d88daa84` · Raw: [[../raw/2026-11-22-pi-的-extension-skill-与-package-把-做事手册-与-代码插件-彻底分开.md|2026-11-22-pi-的-extension-skill-与-package-把-做事手册-与-代码插件-彻底分开.md]]
- 给编码 Agent 加能力时，工程团队很容易掉进两个极端的坑里：要么把二十份内部运维手册、数据库迁移规范全塞进启动时的系统提示词（System Prompt），结果用户哪怕只问一句「当前在哪个分支」，每次请求都要白白烧掉上万个上下文 Token；要么试图靠写纯文本提示词去「模拟」一个需要鉴权与状态管理的新工具，逼着模型在命令行里拼凑脆弱的脚本。
- Pi 在 `pi-coding-agent` 层把扩展机制利落地一分为三：**Skill** 管「按需翻阅的作业指导书」，**Extension** 管「跑在宿主进程里的代码级能力注册」，**Package** 管「把这两者连同模板、主题打包分发」。先分清「什么时候只是读文本、什么时候真正在跑代码」，整个插件体系就一目了然了。
- 图源 · PNG 预览 · 不看图的说明
- 为什么不能把所有技能全文一次性塞进上下文？因为绝大多数对话根本用不上其中 90% 的专项规范，过早注入不仅浪费窗口，还会分散模型对当前任务的注意力。
- Pi 对 Skill 采用了经典的**两阶段渐进式披露**（Progressive Disclosure）：
