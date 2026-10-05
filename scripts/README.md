# 图源与仓库检查

从仓库根目录运行：

```bash
python3 scripts/rebuild_scenes.py
python3 scripts/check_repo.py
python3 scripts/check_sources.py
python3 scripts/check_figure_legibility.py
python3 scripts/build_contents.py --check
python3 scripts/build_markdown.py
```

统一命令会运行 Pi、上下文概念图及各图目录中的 `build.py` 或 `build_scene.py`，重建原生 `.excalidraw` 图源；CI 对比重建后的图源与 Git 版本。生成器覆盖测试防止漏掉采用不同文件名的图。SVG/PNG 使用已安装的 [excalidraw-agent](https://github.com/chicogong/excalidraw-agent) 的 `scripts/render_excalidraw.py` 从图源导出；分别传入目标图源和 `.svg`、`.png` 输出路径。导出后目视检查原图和 README 宽度的缩小预览，并确认同一幅图的三份文件同步提交。检查脚本核对文件、图源结构与本地 Markdown 链接；它不替代视觉或源码证据审查。

生成器只使用 Python 标准库，没有访问模型或外部账户。固定版本的源码链接保存在各篇正文，不写入图像生成代码的运行时依赖。`check_repo.py` 还核对源 Markdown 的本地标题锚点（包括 GitHub 书序目录和示例说明），避免文件存在但章节跳转失效；网站实际渲染的锚点仍由站点门禁另查。

同一检查还逐行比较图源与原生 SVG 的标签、重复次数、字号和颜色，防止改完图源却忘记重导旧 SVG。它不判断 PNG 是否同步、字体回退、节点布局或箭头含义；这些仍须重导并目视核对。

CDN 在 Chromium 中间歇性挂起时，可使用 `render_native_figures.py --renderer <excalidraw-agent>/scripts/renderer.html <图目录名>...`，在 Skill 的 Playwright 环境运行。它加载**同一份未改动的原生 renderer**，仅用 curl 取得并缓存静态 jsDelivr 资源，再批量调用相同 `exportToSvg` 逻辑导出 SVG 与 4× PNG；不是自己拼 SVG，也不做字体替换。缓存位于忽略的 `tmp/native-export-cache/`，不进 Git；版本更新时重新审查 renderer 与缓存。不要用旧预览代替新图源导出，成功后仍须目视检查。

`build_contents.py` 从同一书稿清单生成仓库跟踪的 `book/CONTENTS.md`，供 GitHub 按书序阅读；改变章节或标题后运行脚本更新目录，CI 用 `--check` 防止过期。它只有导航，没有第二份正文。`build_markdown.py` 也只使用标准库：从 `book/manifest.txt` 生成确定性的可携带 ZIP，把正文、章节导航、图源、SVG/PNG 与证据规则放在同一个相对路径树中；写作与构建文件只保留仓库链接。构建时检查包内相对链接，不改源 Markdown。PDF 另由 `build_book.py` 生成；它不会修改仓库中跟踪的封面 SVG。需要更新封面时明确运行 `python3 scripts/book_cover.py`，之后由 PDF 检查重建临时 SVG 与跟踪版本比对。

`check_figure_legibility.py` 只用标准库，按书稿清单中的实际图宽和图源字号估算 A4 页上的最小文字尺寸，同时报告有效 PPI。它默认列出需人工审阅的图；单图严格检查可用 `python3 scripts/check_figure_legibility.py --strict --figure agent-loop`。这只是排版预检，不判断箭头是否交叉、语义是否正确，也不取代实际 PDF 含图页目视审稿。

样书询价前可先从最新公共阅读版 PDF 拆出布局参考：`python3 scripts/prepare_print_proof.py`。它写到 Git 忽略的 `output/pdf/print-proof/`，生成 A4 内文校样与封面、封底参考页；不会制作书脊、出血或可送厂封面母版。它依赖 `book/requirements.txt` 中的 `pypdf`。书稿或 PDF 更新后必须重新运行，并核对来源文件版本。
