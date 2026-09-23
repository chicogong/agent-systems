# 书稿与 PDF

`manifest.txt` 是印刷阅读顺序，也是 PDF 的唯一章节清单。`@front` 指向前言、导读等卷首 Markdown，`@part` 开始正文分部，`@back` 指向结语、致谢、作者简介等卷末 Markdown；其余行是正文路径。封面、标题页、关于本版、目录与封底由构建器插入，书稿正文保留在 Markdown，避免把致谢或履历硬编码进脚本。系统文章保留固定源码版本和证据边界；尚未完成的机制专题不会凭空加入书稿。新增章节先完成图文、来源和检查，再加入清单。

从仓库根目录构建：

```bash
python3 -m pip install -r book/requirements.txt
python3 scripts/fetch_book_font.py
python3 scripts/build_book.py
python3 scripts/check_book_pdf.py
pdfinfo output/pdf/agent-systems-preview.pdf
```

可用 `--output /绝对路径/书名.pdf` 另存。默认 PDF 是**静态源码阅读预览**，不是对全部项目的运行验证，也不是已授权的正式出版物。网页正文保留为内容原稿；PDF 自动把图的 SVG 展示路径映射到同目录的 PNG 预览，不修改正文或 `.excalidraw` 图源。章节中的上游代码链接保留为 PDF 可点击外链。

构建只读 `book/`、`docs/`、`figures/` 和清单，写入指定 PDF。默认输出不提交 Git，适合在完成校稿后作为 Release 附件。没有在 PDF 中内嵌第三方上游代码或仓库文件。文字与原创图采用 [CC BY 4.0](../LICENSE-CONTENT.md)，构建脚本采用 [MIT](../LICENSE-CODE)。正文使用固定 SHA-256 校验的 [Noto Sans SC](https://github.com/google/fonts/tree/e44c4b011a820c2cbe2fd2cfa8052037d7edb571/ofl/notosanssc)；代码拉丁字母使用 [JetBrains Mono](https://github.com/google/fonts/tree/e44c4b011a820c2cbe2fd2cfa8052037d7edb571/ofl/jetbrainsmono)，中文仍由 Noto Sans SC 承载。两者均遵循 [SIL OFL 1.1](https://github.com/google/fonts/blob/e44c4b011a820c2cbe2fd2cfa8052037d7edb571/ofl/jetbrainsmono/OFL.txt)，独立于本仓库内容许可。构建前下载一次，以后可离线重建。发布前仍需确认外链、图片和打印实样；构建成功本身不替代编辑审稿。

[GitHub Actions](../.github/workflows/book.yml) 在书稿、来源、许可、正文或图稿变更、每周一 03:17 UTC（新加坡时间 11:17）和手动触发时重建，上传 PDF、前五页、末四页、封面与封底 300 DPI 校样及所有含图页的审稿 PNG，保留 30 天。每周还检查 Markdown 外链并上传待复核报告；网络错误不自动改正文。定时任务只给校稿者下载，不自动提交生成文件或发布 Release；正式版本由人工审稿后另行打 tag 并发布。GitHub 定时任务可能延迟或因仓库长期无活动而停用，因此不能把它当作永久存档。

图稿 PNG 在 PDF 中通常有数百 DPI；若 A4 上仍难读，优先检查原图节点文字、注释密度与图在页面中的实际尺寸，单纯提高像素数不会放大印刷字体。正文图与图源同源，校稿时以含图页审稿 PNG 检查节点、箭头及图注，不能只看独立的高分辨率 `preview.png`。

[封面设计与分辨率说明](assets/README.md)应单独看：目前以原图插画加矢量排版维持选定封面的视觉一致性。原插画放到 A4 页约 131 PPI；PDF 页面导出为 300 DPI 也不会增加插画的原始细节。正式印刷前仍需高清分层素材或忠实重绘；生成图中没有经过核对的 ISBN、页码和许可一律不用。
