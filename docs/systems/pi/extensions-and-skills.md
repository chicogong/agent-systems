# Pi 的 Extension、Skill 与 Package

[返回 Pi 首页](README.md) · 固定源码版本 [`898ab804`](https://github.com/earendil-works/pi/tree/898ab804050730e9dcefb4443875d5a932aa6a32)

![Pi 的 Skill 与 Extension 分层](../../../figures/pi-extensions/diagram.svg)

[图源](../../../figures/pi-extensions/scene.excalidraw) · [PNG 预览](../../../figures/pi-extensions/preview.png) · [不看图的说明](../../../figures/pi-extensions/README.md)

一句话区分：**Skill 是按需读取的工作指导；Extension 是加载到 Pi 进程的代码扩展；Package 是可同时分发两者的容器。** 把它们统称“插件”，会掩盖什么时候只是增加上下文、什么时候真正改变工具和事件处理。这里的事实固定在当前 Pi 版本，不自动适用于所有 Agent 产品。

## Skill：发现描述，按需读取正文

Pi 的 `loadSkills` 扫描技能路径并解析 `SKILL.md`；`formatSkillsForPrompt` 把**可由模型调用的 Skill** 的名称、描述和位置放进系统提示，而不是一启动就把全部正文塞进上下文。设置 `disable-model-invocation: true` 的 Skill 不进入这份提示，但仍可由用户通过 `/skill:name` 显式调用。[加载实现](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/coding-agent/src/core/skills.ts#L277-L382) · [官方使用文档](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/coding-agent/docs/skills.md)

当任务相关时，模型可经已有的 `read` 工具读取 `SKILL.md`；用户也可输入 `/skill:name`，由 [`AgentSession._expandSkillCommand`](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/coding-agent/src/core/agent-session.ts#L1792-L1821) 展开完整内容。Skill 可以带脚本、参考资料和资产，并指导模型调用已有工具去运行脚本；但 Skill 文件本身没有注册新工具或订阅事件的 API。因此“不是可执行插件”不等于“没有运行风险”。

## Extension：导入模块，注册行为

Extension 是 TS/JS 模块。加载器通过 `jiti` 导入默认工厂，把 `ExtensionAPI` 交给它；代码可注册工具、命令和事件处理。[加载工厂](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/coding-agent/src/core/extensions/loader.ts#L487-L553) · [注册 API](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/coding-agent/src/core/extensions/loader.ts#L254-L294) · [官方文档](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/coding-agent/docs/extensions.md)

读一个真实而短的示例：[仓库自带的 `hello.ts`](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/coding-agent/examples/extensions/hello.ts#L1-L26)。关注默认导出如何取得 API、注册的工具何时成为模型可调用能力，以及工具的参数与结果由谁定义。这里不复制完整源码，读者可以按固定链接逐行看。

## 二者能组合，但职责仍不同

Extension 可通过 `resources_discover` 返回 Skill 路径，资源加载流程会再发现这些技能。[资源事件链路](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/coding-agent/src/core/agent-session.ts#L2939-L2965) · [仓库自带示例](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/coding-agent/examples/extensions/dynamic-resources/index.ts#L1-L15)。反过来，Skill 可以告诉模型使用某个 Extension 注册的工具，但 Skill 自己并没有变成那个工具。

[Pi Package](https://github.com/earendil-works/pi/blob/898ab804050730e9dcefb4443875d5a932aa6a32/packages/coding-agent/docs/packages.md) 可从 npm/git 安装并捆绑 Extensions、Skills、Prompt Templates、Themes；它解决分发，不抹平运行权限和提示词边界。第三方 Package 中的 Extension 可执行代码，Skill 可引导模型运行脚本，安装前两者都应审查来源。本篇只做固定源码静态核对，尚未实际安装第三方包或验证沙箱行为。
