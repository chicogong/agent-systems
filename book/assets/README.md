# 封面素材与校稿边界

书稿发起人选定的 `cover-selected.png` 是设计参照，也是当前封面中间立体插画、右侧模块栏与手写标语的来源。第一次纯矢量重画虽然清晰，却显著偏离了原图；现改为**忠于原稿的混合设计**：`scripts/book_cover.py` 把这张图放在底层，覆盖并重新排版标题、左侧导语、署名和底栏。PDF 第 1 页与 `cover.svg` 从同一绘图模型生成，`cover-preview.png` 是从 PDF 校样导出的网页预览。SVG 中的形状和文字轮廓可在设计软件中调整；要改文字内容请改脚本并重建。内嵌插画仍是位图，不能称为全矢量封面。

原图为 1024 × 1536 像素，SHA-256 为 `533633cde7a1ce7dbcad0d94bded755b0dbbb69ea2e48fedc284628df9895b28`。在 A4 PDF 中保持原始宽高比、居中留边，插画有效分辨率约 131 PPI；重排文字和底栏为可缩放矢量，**仍不是 300 PPI 印刷母版**。简单插值放大不能补回插画细节。正式印刷前，需要原设计的高清分层素材，或按选定封面忠实地重新绘制中央插画并做实样检查。

编辑 `scripts/book_cover.py` 后运行 `python3 scripts/build_book.py` 重建 PDF 与 SVG，再以 `pdftoppm -f 1 -l 1 -r 180 -png -singlefile output/pdf/agent-systems-preview.pdf book/assets/cover-preview` 更新网页预览。SVG 内嵌原图以便搬运，并把排版文字转为字体轮廓，避免不同设计工具因缺字体改变字形；PDF 则嵌入 Noto Sans SC 与 JetBrains Mono，保留文字检索。封底由构建器以矢量文字和形状绘制，不采用生成图中虚构的 ISBN、条码或错误许可。

封面是书籍品牌素材，不是架构事实图，也不是 `.excalidraw` 导出。其他生成的版权页、目录和封底方案仅供本地比较，其中过时的 CC BY-SA、伪 ISBN 与页码不得进入书稿。公开发布与印刷前仍需完成封面权益和第三方素材复核。
