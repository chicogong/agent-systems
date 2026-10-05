# Pi 的 Extension、Skill 与 Package

[返回 Pi 首页](README.md) · 固定源码版本 [`898ab804`](https://github.com/earendil-works/pi/tree/898ab804050730e9dcefb4443875d5a932aa6a32)

想让 Pi 按一套方法写文档，可以给它一份 Skill；想新增一个它能调用的工具，可以写 Extension；想把指导、工具和主题一起分享给别人，可以打包成 Package。这三个名字分别解决“怎么做”“增加什么能力”和“怎么分发”。

![Pi 的 Skill 与 Extension 分层](../../../figures/pi-extensions/diagram.svg)

[图源](../../../figures/pi-extensions/scene.excalidraw) · [PNG 预览](../../../figures/pi-extensions/preview.png) · [不看图的说明](../../../figures/pi-extensions/README.md)

在本篇研究的 Pi 版本里，Skill 是按需读取的工作指导；Extension 是加载到 Pi 进程中的代码扩展；Package 是可以分发它们的安装包。下面分别看 Pi 在什么时候读文件、运行代码。

## Skill：发现描述，按需读取正文

Pi 先用 `loadSkills` 扫描技能目录、读取 `SKILL.md` 信息。`formatSkillsForPrompt` 再把模型可调用技能的名称、描述和文件位置放进系统提示。模型先看到这份简短目录，需要某项技能时，再去读完整指导。

设置 `disable-model-invocation: true` 的技能会从这份目录中省略；用户仍可输入 `/skill:name` 主动调用。[读取技能信息](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/coding-agent/src/core/skills.ts#L277-L382) · [官方使用文档](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/coding-agent/docs/skills.md)

模型可以通过已有的 `read` 等工具读取 `SKILL.md`；用户输入 `/skill:name` 时，程序则用 [`AgentSession._expandSkillCommand`](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/coding-agent/src/core/agent-session.ts#L1792-L1821) 展开完整内容。Skill 还可以附带脚本、参考资料和素材，指导模型用现有工具完成工作。

Skill 文件提供的是指导。要新增工具或处理程序事件，需要 Extension 的注册接口。若指导里要求运行脚本，仍应检查脚本来源和实际操作。

## Extension：导入模块，注册行为

Extension 是 TypeScript 或 JavaScript 代码模块。加载器用 `jiti` 导入模块，把 `ExtensionAPI` 交给默认导出的初始化函数；扩展通过这个接口注册工具、命令或事件处理函数。加载 Extension 时，Pi 会运行它的代码。[加载扩展](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/coding-agent/src/core/extensions/loader.ts#L487-L553) · [注册接口](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/coding-agent/src/core/extensions/loader.ts#L254-L294) · [官方文档](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/coding-agent/docs/extensions.md)

想看一个短例子，可以打开[仓库自带的 hello.ts](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/coding-agent/examples/extensions/hello.ts#L1-L26)。先看初始化函数如何取得 API，再看它怎样定义工具名称、参数和执行结果。这样就能把图中的“注册工具”对应到几行实际代码。

## Package 把它们一起交给用户

二者可以配合：Extension 用 `resources_discover` 返回 Skill 路径，Pi 再把这些技能加入资源发现流程；Skill 的指导也可以告诉模型如何使用 Extension 注册的工具。[发现扩展提供的资源](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/coding-agent/src/core/agent-session.ts#L2939-L2965) · [仓库自带示例](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/coding-agent/examples/extensions/dynamic-resources/index.ts#L1-L15)

[Pi Package](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/coding-agent/docs/packages.md) 可以从 npm 或 Git 安装，包里可以包含 Extensions、Skills、提示词模板和主题。它方便一起分发这些文件。

安装前，按内容分别检查：Extension 会运行代码，Skill 可能要求执行附带脚本。本文依据固定源码和官方文档，尚未实际安装第三方包或验证运行隔离。
