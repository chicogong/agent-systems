# Pi 扩展资源图的文字版

[返回专题](../../docs/systems/pi/extensions-and-skills.md) · [图源](scene.excalidraw) · [SVG](diagram.svg) · [PNG](preview.png)

A 路：Skill 从 Package 或本地目录被发现，先将名称、描述和路径放进提示；正文由模型按需读取或经 `/skill:name` 命令展开。B 路：Extension 的 TS/JS 模块由加载器导入，调用 `ExtensionAPI` 注册工具、事件或命令。两路可在 `resources_discover` 相交，Extension 提供新的 Skill 路径。Skill 本身不自动执行脚本，也没有工具注册 API。

固定版本的实现证据见[专题正文](../../docs/systems/pi/extensions-and-skills.md)。
