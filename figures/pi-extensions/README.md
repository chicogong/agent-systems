# Pi 扩展资源图的文字版

[返回专题](../../docs/systems/pi/extensions-and-skills.md) · [图源](scene.excalidraw) · [SVG](diagram.svg) · [PNG](preview.png)

想给 Pi 一套写作方法，就提供 Skill；想增加一个工具，就提供 Extension。图的上下两路分别说明它怎样读指导、加载代码。Package 是可以把两者一起分发的安装包。

**A 路：先看到技能目录，需要时再读正文。** Pi 从安装包或本地目录发现 `SKILL.md`，用 `loadSkills` 读出名称、描述和路径。`formatSkillsForPrompt` 把模型可调用的技能列进系统提示。模型需要某项指导时，再用已有的 `read` 工具读取完整内容；用户也可以用 `/skill:name` 主动展开它。

**B 路：导入扩展代码，把能力接进程序。** Extension 是 TypeScript/JavaScript（TS/JS）模块，加载时会运行代码，因此应先检查来源。加载器 `jiti` 导入模块并调用其初始化函数，把 `ExtensionAPI` 注册接口交给它。扩展可用 `registerTool` 注册工具，用 `on` 接入事件处理，也可以增加命令。

图下的交叉点 `resources_discover` 是资源发现入口：Extension 可以返回新的 Skill 路径，交给 Pi 继续读取。同一个 Package 也能直接带上两类文件。

有两处条件需要记住：设置 `disable-model-invocation: true` 的 Skill 会从模型目录中省略，但用户仍能用 `/skill:name` 调用。Skill 附带的脚本则要经已有工具执行；图中“Skill 自身没有 `registerTool` API”说明，新增工具使用的是 B 路的扩展接口。

本图依据固定源码 `898ab804`，实现位置和安装前的提醒见[专题正文](../../docs/systems/pi/extensions-and-skills.md)。
