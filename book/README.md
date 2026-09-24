# 同一书稿，两种导出

[`manifest.txt`](manifest.txt) 是 GitHub [书序目录](CONTENTS.md)、阅读网站、PDF 与可携带 Markdown 阅读包共用的**唯一章节顺序**。`@front` 指卷首，`@part` 指分部，`@back` 指卷末；其余行是相对于仓库根目录的正文路径。正文只在 `book/frontmatter/`、`docs/`、`book/backmatter/` 中维护一份，不在导出目录手改副本。未完成的专题不会凭空加入清单；进入清单也只表示进入预览稿，不代表通过正式出版验收。

## Markdown 阅读包

```bash
python3 scripts/build_markdown.py
```

生成 `output/markdown/agent-systems-md.zip`。解压后，从 `agent-systems-md/README.md` 开始阅读；也可以把**整个** `agent-systems-md` 文件夹作为 Obsidian vault 打开，或复制进已有 vault。保留文件夹内部结构：章节、图的文字版、SVG/PNG 和可编辑 `.excalidraw` 图源使用相对路径。阅读包只收书稿和必要的导航、证据与图稿文件；指向写作计划或构建脚本的少数链接改为仓库链接。它使用标准 Markdown 链接，不依赖 Obsidian 专用插件或 wikilink，也不需要 PDF 的字体或渲染依赖。

生成器逐条检查包内本地链接与图片，缺失即失败。ZIP 不提交 Git；每次书稿构建与每周审稿任务会将它和 PDF 一同上传为待复核 Artifact。Action 使用当前提交 SHA 生成指向包外写作文件的固定仓库链接；日后制作 tag 版本可用 `--ref <tag>`。包内 Markdown 是导出物，改稿请回仓库源文件。

## PDF 预览

从仓库根目录构建：

```bash
python3 -m pip install -r book/requirements.txt
python3 scripts/fetch_book_font.py
python3 scripts/check_figure_legibility.py
python3 scripts/build_book.py
python3 scripts/check_book_pdf.py
pdfinfo output/pdf/agent-systems-preview.pdf
```

可用 `--output /绝对路径/书名.pdf` 另存。默认 PDF 是**静态源码阅读预览**，不是对全部项目的运行验证，也不是已授权的正式出版物。PDF 自动把图的 SVG 展示路径映射到同目录的 PNG 预览，不修改正文或 `.excalidraw` 图源。章节中的上游代码链接保留为 PDF 可点击外链。封面、标题页、关于本版、目录与封底由构建器插入；致谢和作者简介仍在 Markdown 中。

默认校样会把未纳入 PDF 的本仓本地链接转成源码仓 URL，**在仓库仍私有时不能直接放到公开网站**。另用同一清单构建公共阅读版：

```bash
python3 scripts/build_book.py --public-links --output output/pdf/agent-systems-public-preview.pdf
python3 scripts/check_book_pdf.py output/pdf/agent-systems-public-preview.pdf --public-readiness
shasum -a 256 output/pdf/agent-systems-public-preview.pdf
```

公共版将可用的内部参考链接改到在线章节或原尺寸 SVG，不把尚未发布的可编辑图源伪装成可点击链接。公共门禁检查已知私有仓与非 HTTPS 注释链接；它不代替权益、外链可访问性、无障碍和整书审稿。电子版仍应以 HTML 为检索与辅助技术阅读的首选；PDF 尚未制作语义标签，也不代表 300 PPI 印刷母版。[当前人工发布的电子校样](https://books.aimake.cc/pdf)与每周 CI 的私有审稿 Artifact 分开维护；定时构建不会自动覆盖网站。

PDF 构建只读书稿与图稿，写入指定输出路径；不会顺手重写仓库中的封面 SVG。封面设计变更时单独运行 `python3 scripts/book_cover.py` 更新该图，并检查 PDF 与 SVG 一致。默认输出不提交 Git，适合完成校稿后作为 Release 附件。没有在 PDF 中内嵌第三方上游代码或仓库文件。文字与原创图采用 [CC BY 4.0](../LICENSE-CONTENT.md)，构建脚本采用 [MIT](../LICENSE-CODE)。正文使用固定 SHA-256 校验的 [Noto Sans SC](https://github.com/google/fonts/tree/e44c4b011a820c2cbe2fd2cfa8052037d7edb571/ofl/notosanssc)；代码拉丁字母使用 [JetBrains Mono](https://github.com/google/fonts/tree/e44c4b011a820c2cbe2fd2cfa8052037d7edb571/ofl/jetbrainsmono)，中文仍由 Noto Sans SC 承载。两者均遵循 [SIL OFL 1.1](https://github.com/google/fonts/blob/e44c4b011a820c2cbe2fd2cfa8052037d7edb571/ofl/jetbrainsmono/OFL.txt)，独立于本仓库内容许可。构建前下载一次，以后可离线重建。发布前仍需确认外链、图片和打印实样；构建成功本身不替代编辑审稿。

[GitHub Actions](../.github/workflows/book.yml) 在书稿、来源、许可、正文或图稿变更、每周一 03:17 UTC（新加坡时间 11:17）和手动触发时重建；先运行图稿最小字号预检与单测，再上传 Markdown ZIP、私有校样、公共链接版和审稿 PNG，保留 30 天。每周还检查 Markdown 外链并上传待复核报告；网络错误不自动改正文。定时任务只给校稿者下载，不自动提交生成文件或发布 Release；正式版本由人工审稿后另行打 tag 并发布。GitHub 定时任务可能延迟或因仓库长期无活动而停用，因此不能把它当作永久存档。

图稿 PNG 在 PDF 中通常有数百 DPI；若 A4 上仍难读，优先检查原图节点文字、注释密度与图在页面中的实际尺寸，单纯提高像素数不会放大印刷字体。正文图与图源同源，校稿时以含图页审稿 PNG 检查节点、箭头及图注，不能只看独立的高分辨率 `preview.png`。

[封面设计与分辨率说明](assets/README.md)应单独看：目前以原图插画加矢量排版维持选定封面的视觉一致性。原插画放到 A4 页约 131 PPI；PDF 页面导出为 300 DPI 也不会增加插画的原始细节。正式印刷前仍需高清分层素材或忠实重绘；生成图中没有经过核对的 ISBN、页码和许可一律不用。

若要核对纸面版式或向印厂询价，先运行 `python3 scripts/prepare_print_proof.py` 生成 108 页 A4 内文校样及封面、封底参考页。它们是本地临时产物，不是可以直接下单的印刷母版；书脊、出血与最终封面必须依据印厂模板重新制作。
