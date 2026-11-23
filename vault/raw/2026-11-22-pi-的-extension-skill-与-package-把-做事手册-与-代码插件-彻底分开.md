---
title: "Pi 的 Extension、Skill 与 Package：把「做事手册」与「代码插件」彻底分开"
origin: "/Users/haorangong/Github/chicogong/experiments/agent-systems/docs/systems/pi/extensions-and-skills.md"
sha256: "3fb6b900d88daa840099d803beaddd9c9b770a267ce9baf200dc8b3f7b3f7fd9"
ingested_at: "2026-11-22T13:54:22.998Z"
tags: []
---

# Pi 的 Extension、Skill 与 Package：把「做事手册」与「代码插件」彻底分开

# Pi 的 Extension、Skill 与 Package：把「做事手册」与「代码插件」彻底分开

[返回 Pi 首页](README.md) · 固定源码版本 [`898ab804`](https://github.com/earendil-works/pi/tree/898ab804050730e9dcefb4443875d5a932aa6a32)

给编码 Agent 加能力时，工程团队很容易掉进两个极端的坑里：要么把二十份内部运维手册、数据库迁移规范全塞进启动时的系统提示词（System Prompt），结果用户哪怕只问一句「当前在哪个分支」，每次请求都要白白烧掉上万个上下文 Token；要么试图靠写纯文本提示词去「模拟」一个需要鉴权与状态管理的新工具，逼着模型在命令行里拼凑脆弱的脚本。

Pi 在 `pi-coding-agent` 层把扩展机制利落地一分为三：**Skill** 管「按需翻阅的作业指导书」，**Extension** 管「跑在宿主进程里的代码级能力注册」，**Package** 管「把这两者连同模板、主题打包分发」。先分清「什么时候只是读文本、什么时候真正在跑代码」，整个插件体系就一目了然了。

![Pi 的 Skill 与 Extension 分层](../../../figures/pi-extensions/diagram.svg)

[图源](../../../figures/pi-extensions/scene.excalidraw) · [PNG 预览](../../../figures/pi-extensions/preview.png) · [不看图的说明](../../../figures/pi-extensions/README.md)

## Skill：目录常驻、正文懒加载的渐进式披露

为什么不能把所有技能全文一次性塞进上下文？因为绝大多数对话根本用不上其中 90% 的专项规范，过早注入不仅浪费窗口，还会分散模型对当前任务的注意力。

Pi 对 Skill 采用了经典的**两阶段渐进式披露**（Progressive Disclosure）：

1. **启动期只摆书目索引**：`loadSkills` 扫描技能目录并解析每个 `SKILL.md` 的头部元数据，`formatSkillsForPrompt` 只把允许模型自主调用的技能名称、一句话描述和文件路径拼成精简清单放进系统提示词。
2. **执行期按需抽书翻阅**：只有当模型判断手头任务命中某项技能时，才主动调用现成的 `read` 工具去读取那份 `SKILL.md` 的完整正文，或顺着路径使用目录里附带的参考资料与辅助脚本。

如果你有一套高风险或高成本流程（比如发版检查单），不希望模型自己猜着触发，只需在元数据里标上 `disable-model-invocation: true`——它就会从系统提示词的书目索引里隐身，平时零 Token 开销，只有当用户在终端显式输入 `/skill:name` 时，才由 [`AgentSession._expandSkillCommand`](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/coding-agent/src/core/agent-session.ts#L1792-L1821) 原地展开全文（参见[读取技能信息](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/coding-agent/src/core/skills.ts#L277-L382)与[官方使用文档](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/coding-agent/docs/skills.md)）。

```text
启动时注入系统提示词（仅数十 Token / 项）：
  - db-migration: 生产库字段变更与回滚检查规范 -> /path/to/db-migration/SKILL.md
  （注：标有 disable-model-invocation: true 的技能连这一行都不注入）

命中任务或用户输入 /skill:db-migration 时：
  -> 按需读取 / 展开 SKILL.md 完整步骤与同目录参考脚本
```

记住一条硬边界：**Skill 本身只是文本指导**。它能教会模型怎样组合现有的 `read`、`bash`、`edit` 工具把活干漂亮，但它没法凭空往运行时里注册一个全新的原生工具，也没法拦截底层生命周期事件——那是 Extension 的领地。

## Extension：注入宿主进程的代码级能力与钩子

当你需要给模型增加一个结构化新工具、注册自定义斜杠命令，或者在每次工具调用前后挂载审计与拦截逻辑时，就必须写 **Extension**。

Extension 是真正的 TypeScript 或 JavaScript 模块。Pi 的扩展加载器在启动时通过 `jiti` 动态导入模块，把 `ExtensionAPI` 实例传给模块默认导出的初始化函数；扩展代码拿到这个句柄后，直接向宿主注册工具 schema、执行函数、自定义命令与事件监听器（见[加载扩展](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/coding-agent/src/core/extensions/loader.ts#L487-L553)、[注册接口](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/coding-agent/src/core/extensions/loader.ts#L254-L294)及[官方文档](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/coding-agent/docs/extensions.md)）。

打开[仓库自带的 hello.ts](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/coding-agent/examples/extensions/hello.ts#L1-L26)，二十多行代码就能看清全貌：导出一个接收 `pi: ExtensionAPI` 的函数，调用 `registerTool` 声明工具名、参数校验结构与异步 `execute` 实现，模型在下一轮就会像调用内置工具一样看见并调用它。

这也划出了截然不同的安全水位：**加载 Extension 的那一刻，它的代码就已经在当前 Pi 进程里直接运行了**，拥有与宿主完全相同的系统权限；而加载 Skill 目录在启动期只做文本解析，风险主要发生在后续模型按手册提示去执行附带脚本的时刻。

## 左手工具、右手说明书：用 Package 组合分发

在实际工程里，Extension 和 Skill 往往是一对黄金搭档：光靠 Extension 注册一个内部系统的专有工具，模型未必懂你们团队在什么前置条件下才允许调它；反过来光给一份 Skill 文档，又缺少受参数校验保护的专用接口。

因此 Pi 打通了两者的联动通道：Extension 可以通过监听 `resources_discover` 事件动态吐出自己携带的 Skill 目录路径，让 `AgentSession` 把这些技能一并纳入资源发现管线（见[发现扩展提供的资源](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/coding-agent/src/core/agent-session.ts#L2939-L2965)与[仓库自带示例](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/coding-agent/examples/extensions/dynamic-resources/index.ts#L1-L15)）。需要跨团队共享时，再用 [Pi Package](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/coding-agent/docs/packages.md) 把 Extensions、Skills、提示词模板和界面主题打成一个可经由 npm 或 Git 分发的安装包——能力底座与操作规范一次到位。

| 维度 | Skill | Extension | Package |
| --- | --- | --- | --- |
| **本质形态** | `SKILL.md` 文档及同目录参考资源 | TypeScript / JavaScript 代码模块 | npm 或 Git 分发包 |
| **解决的问题** | 教模型「按什么步骤和规范做事」 | 给运行时「加原生工具、命令与事件钩子」 | 把整套工具链、规范与主题打包共享 |
| **执行时机** | 启动只读摘要，命中或 `/skill:name` 时读正文 | 加载模块时立即在 Pi 进程内运行代码 | 安装并加载包内对应组件时分别生效 |

## 来源与边界

本文依据官方仓库固定提交 [`earendil-works/pi@898ab804050730e9dcefb4443875d5a932aa6a32`](https://github.com/earendil-works/pi/tree/898ab804050730e9dcefb4443875d5a932aa6a32) 中的 `coding-agent` 源码与配套文档整理，核对日期 2026-09-23。全文聚焦静态源码中的加载机制与扩展边界，未涵盖第三方生态包兼容性测试。
