# 图源与仓库检查

从仓库根目录运行：

```bash
python3 scripts/build_pi_figures.py
python3 scripts/check_repo.py
```

`build_pi_figures.py` 生成两张原生 `.excalidraw` 图源。SVG/PNG 使用已安装的 [excalidraw-agent](https://github.com/chicogong/excalidraw-agent) 的 `scripts/render_excalidraw.py` 从图源导出；分别传入目标图源和 `.svg`、`.png` 输出路径。导出后目视检查原图和 README 宽度的缩小预览，并确认同一幅图的三份文件同步提交。检查脚本核对文件、图源结构与本地 Markdown 链接；它不替代视觉或源码证据审查。

生成器只使用 Python 标准库，没有访问模型或外部账户。固定版本的源码链接保存在各篇正文，不写入图像生成代码的运行时依赖。
