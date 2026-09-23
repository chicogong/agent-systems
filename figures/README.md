# 图稿约定

每张正式图放在独立目录：`scene.excalidraw` 是可编辑源文件，`diagram.svg` 用于 Markdown，`preview.png` 用于预览，`README.md` 给出文字说明、主张、来源和核验状态。

使用 [excalidraw-agent](https://github.com/chicogong/excalidraw-agent) 绘制和导出。发布前目视检查文字、箭头、边界、留白与移动端可读性。MCP 画布的成功返回只证明已接收，不证明与本地导出视觉一致；需要交互展示时还要检查实际画布。

标题与节点字体、图形语义和导出验收见[视觉规范](STYLE.md)。当前采用 Normal 标题和 Code 节点；MCP 交互画布会强制使用另一字体，因此仓库 SVG/PNG 才是对外展示的视觉基准。

概念图可以表达通用模型，但须说明它不是某个项目的内部结构。实现图只标固定源码版本中能核对的组件和路径。
