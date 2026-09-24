# Pi 扩展资源图的文字版

[返回专题](../../docs/systems/pi/extensions-and-skills.md) · [图源](scene.excalidraw) · [SVG](diagram.svg) · [PNG](preview.png)

A 路：Skill 从 Package 或本地目录被发现；`loadSkills` 解析名称、描述和路径，只有允许模型调用的 Skill 才由 `formatSkillsForPrompt` 列入系统提示。带有 `disable-model-invocation: true` 的 Skill 不进入提示，但用户仍可通过 `/skill:name` 显式展开；提示中可见的 Skill 则可由模型按需经 `read` 读取。B 路：Extension 的 TS/JS 模块由 `jiti` 导入，调用 `ExtensionAPI` 注册工具、事件或命令。同一 Pi Package 可以分发两者；两路也可在 `resources_discover` 相交，由 Extension 提供新的 Skill 路径。Skill 本身不自动执行脚本，也没有工具注册 API；Skill 附带的脚本由模型经已有工具调用。

本图按固定源码 898ab804 绘制。实现证据见[专题正文](../../docs/systems/pi/extensions-and-skills.md)。
