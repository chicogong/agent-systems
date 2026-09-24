# 图源与仓库检查

从仓库根目录运行：

```bash
python3 scripts/rebuild_scenes.py
python3 scripts/check_repo.py
python3 scripts/check_sources.py
python3 scripts/check_figure_legibility.py
python3 scripts/build_markdown.py
```

统一命令会运行 Pi、上下文概念图及各图目录中的 `build.py`，重建原生 `.excalidraw` 图源；CI 对比重建后的图源与 Git 版本。SVG/PNG 使用已安装的 [excalidraw-agent](https://github.com/chicogong/excalidraw-agent) 的 `scripts/render_excalidraw.py` 从图源导出；分别传入目标图源和 `.svg`、`.png` 输出路径。导出后目视检查原图和 README 宽度的缩小预览，并确认同一幅图的三份文件同步提交。检查脚本核对文件、图源结构与本地 Markdown 链接；它不替代视觉或源码证据审查。

生成器只使用 Python 标准库，没有访问模型或外部账户。固定版本的源码链接保存在各篇正文，不写入图像生成代码的运行时依赖。

`build_markdown.py` 也只使用标准库：从 `book/manifest.txt` 生成确定性的可携带 ZIP，把正文、章节导航、图源、SVG/PNG 与证据规则放在同一个相对路径树中；写作与构建文件只保留仓库链接。构建时检查包内相对链接，不改源 Markdown。PDF 另由 `build_book.py` 生成；它不会修改仓库中跟踪的封面 SVG。需要更新封面时明确运行 `python3 scripts/book_cover.py`，之后由 PDF 检查重建临时 SVG 与跟踪版本比对。

`check_figure_legibility.py` 只用标准库，按书稿清单中的实际图宽和图源字号估算 A4 页上的最小文字尺寸，同时报告有效 PPI。它默认列出需人工审阅的图；单图严格检查可用 `python3 scripts/check_figure_legibility.py --strict --figure agent-loop`。这只是排版预检，不判断箭头是否交叉、语义是否正确，也不取代实际 PDF 含图页目视审稿。

样书询价前可先从最新公共阅读版 PDF 拆出布局参考：`python3 scripts/prepare_print_proof.py`。它写到 Git 忽略的 `output/pdf/print-proof/`，生成 A4 内文校样与封面、封底参考页；不会制作书脊、出血或可送厂封面母版。它依赖 `book/requirements.txt` 中的 `pypdf`。书稿或 PDF 更新后必须重新运行，并核对来源文件版本。
