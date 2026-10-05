# 图解 Agent 系统 · 在线阅读站

[线上预览](https://books.aimake.cc/) 是公开阅读入口，**不是** GitHub 书稿仓库的公开镜像。默认构建仅发布书稿清单中的 Markdown 正文、少量阅读索引与来源说明、对应展示用 SVG，以及两张明确许可的分享配图。PDF 与 Markdown ZIP 只有经过独立检查、散列锁定并显式启用时才加入；可编辑 Excalidraw 图源仅在获准的离线 ZIP 内提供，不直接复制整个仓库。

## 唯一内容源

VitePress 1.6.4 只负责静态 HTML 呈现。脚本 `scripts/prepare-public.mjs` 从仓库根目录的 `book/manifest.txt` 按顺序读取正文，生成首页目录、章节路由、章节位置与前后篇导航，以及图稿的文字说明；正文仍只在原 Markdown 文件里维护。GitHub 的 `book/CONTENTS.md` 同样由清单派生。额外公开的 8 篇是机制/系统/对照索引及来源记录，不进入书稿清单。它们帮助保留书内引用的证据路径。

同仓运行时无需指定内容根目录。独立工作树联调可设 `BOOK_CONTENT_ROOT` 指向待验收的书稿根目录，确保生成的是同一版稿件，而不是旧分支。生产构建必须设置实际 HTTPS 站点域名作为 `SITE_URL`，供 canonical、sitemap 和 robots 使用。

本地预览允许未提交修改，但首页、章节末尾、反馈页和 `/version.json` 会标明“本地未提交稿”，不能拿该提交号声称可复现。准备正式上线的候选版应从**干净书稿工作树**构建，并设置 `SITE_RELEASE=1`；脚本发现未提交修改会拒绝该候选版。`/version.json` 分别记录网页、PDF、Markdown 包的完整提交号与文件散列，以及访问统计开关，不存储账号或读者数据。入口改版不必重新导出已审 PDF；不同产物的实际版本必须分别展示，不能冒称都是网页的最新提交。

```bash
cd site
npm ci
SITE_URL=https://books.aimake.cc DEPLOY_TARGET=vercel npm run build:public
```

上述命令用于本地验收。人工确认候选提交后，部署用同一命令额外设置 `SITE_RELEASE=1`，并在部署后运行字节级 `verify:live`；这两个步骤都不能代替正文、权益和图稿审查。

构建输出在 `site/.vitepress/dist/`，不提交到 Git。生成的 `site/content/` 和导航 JSON 也不提交。私有本地小样仍可用 `npm run dev`，但它只有旧的 8 页，不代表公开站覆盖范围。

## 公共产物边界

- `npm run build:public` 将已发布章节的 Markdown 内链改为站内路由，保留固定版本的公开上游源码链接；未收入网站的本仓页面链接到公开 GitHub 源仓。网站产物仍不包含仓库源文件。
- 正文图只复制展示 SVG，同页附文字说明、放大按钮和原尺寸 SVG 链接。分享配图只允许 `assets/share/book.png` 与 `assets/share/cover.png`，并逐字节核对已许可源文件。未纳入书稿的内部计划页、贡献流程和模板页不作为网站正文发布。
- `scripts/verify-public.mjs` 对 HTML 页数、书序位置与前后篇链接、站内路由与标题锚点、sitemap、canonical、分享/结构化元信息、robots 和输出文件类型做发布前门禁。页数由当前书稿清单、补充索引和入口页计算，不另维护硬编码的历史页数；显式启用 PDF 时才增加阅读页和唯一许可的 PDF 文件。`Check guide structure` 的 `public-site` job 在每次推送/PR 运行默认门禁，不自动部署。构建先运行导航/元数据标题测试：正文保留代码标记，侧栏、前后篇及分享标题使用纯文本。
- 首页与每章明确标识“在线预览稿”；静态源码阅读不等于运行实测。站点允许搜索引擎抓取，但 robots 不是访问控制。正文与原创图采用 CC BY 4.0，图内嵌字体的许可另列在 `/THIRD-PARTY-NOTICES.txt`。

## 搜索发现与阅读反馈

首页先给一张图的起点和学习与应用入口，再用三张卡片连接学习/教学/工作、AI 陪读与可选技术路线。完整目录与阅读路线仍由书稿清单派生；广泛受众必须有对应正文和材料，不只写进宣传与元数据。页面输出唯一 canonical、独立 description、1200×630 的 Open Graph 分享配图与适度的 JSON-LD（首页为 WebSite，正文为 Article）；sitemap 与 robots 同源。结构化数据只是帮助机器理解页面，不保证获得富媒体展示或 AI 引用。不要为了所谓 GEO 在正文堆关键词或编造未核验的结论。

[反馈页](https://books.aimake.cc/feedback)与每章末尾的预填邮件链接使用作者已公开的邮箱，邮件预填站点书稿版本；已启用的 GitHub 阅读反馈表单承接公开问题，私人或敏感信息仍走邮件。章节分享按钮调用系统分享或复制干净链接，去掉查询参数和片段；不把搜索词等信息带进分享链接。接入站内表单前，要先决定垃圾邮件、隐私告知、数据留存和处理责任。

访问统计默认关闭。仅经作者确认，生产构建才可设 `VITE_READER_ANALYTICS=1`，启用 Vercel Web Analytics；只在 `books.aimake.cc` 发送页面访问，去掉 URL 查询参数和片段，不上传站内搜索词、邮件内容或自定义事件，反馈页同步披露。免费 Hobby 版有账户级额度，不提供自定义事件或 UTM 报表，页面访问不能当作读完率。浏览器验收拦截统计请求，避免把机器检查当作推广流量。服务条款与额度见 [Vercel 官方说明](https://vercel.com/docs/analytics/limits-and-pricing)。

Search Console 的站点所有权验证、提交 sitemap、索引与点击数据监测是部署后的账号操作；**构建通过或站点能访问都不等于已经被收录**。

## PDF 在线阅读的发布门槛

同域名 PDF 采用独立 `/pdf` 页面、浏览器原生预览和显眼的下载后备；小屏不嵌入 PDF 阅读器，避免浏览器不支持时出现黑框。HTML 仍是主要可搜索、可缩放和辅助技术阅读版。PDF 尚未制作语义标签，封面插画也不是 300 PPI 印刷母版。PDF 文件单独由 Vercel 回应 `X-Robots-Tag: noindex`，其阅读说明页仍可被发现；这种非 HTML 索引控制符合 [Google 的说明](https://developers.google.com/search/docs/crawling-indexing/robots-meta-tag)。

公共阅读版使用同一书稿清单，内部可用链接改到网站；`book.yml` 在每次审稿构建中额外生成并检查它，但仍只上传为审稿 Artifact。**不允许直接把默认校样复制到网站。** 每次更新前人工审查内容、权益、图文和外链，再从最终干净提交构建公共版，运行 `python3 scripts/check_book_pdf.py output/pdf/agent-systems-public-preview.pdf --public-readiness --expected-commit <完整提交号>`，记录该文件的 SHA-256。网站构建会复查 PDF 的“关于本版”提交、干净工作树标记和文件散列；仅旧 PDF 恰好通过基本结构检查不能上线。明确指定文件与散列才会复制已审文件。若保留此前已审版，必须显式指定 `PUBLIC_PDF_COMMIT`，它须是当前书稿历史中的祖先，页面会展示该 PDF 的真实版本；省略时按网页当前提交检查：

```bash
cd site
PUBLIC_PDF_FILE=/绝对路径/agent-systems/output/pdf/agent-systems-public-preview.pdf \
PUBLIC_PDF_SHA256=<已审稿文件的64位sha256> \
PUBLIC_PDF_COMMIT=<PDF实际对应的完整提交号> \
PDF_CHECK_PYTHON=python3 \
SITE_URL=https://books.aimake.cc DEPLOY_TARGET=vercel npm run build:public
```

Vercel 部署前须人工核对 `dist/pdf.html`、`dist/book/agent-systems-public-preview.pdf`、`dist/vercel.json` 和构建日志，再从同一份 `dist/` 部署。`verify:live` 会在 PDF 模式下连同文件字节和线上 `X-Robots-Tag` 一起检查。构建和测试通过并非权益许可或作者的公开发布决定。

目前 Vercel 项目未连接 Git；部署前先从最终书稿重新构建并通过门禁，再把 `dist/` 部署到已有的 `agent-systems-reader` 项目。例如从 `site/` 执行 `vercel link --cwd .vitepress/dist --scope chico-projects --project agent-systems-reader --yes`，核对生成的 `dist/vercel.json` 和链接的项目，再执行 `vercel deploy --cwd .vitepress/dist --prod --yes`。不要让 Vercel 构建直接读取书稿仓库，也不要把推送工作树等同于网站部署。

部署后，在**实际部署的同一份 `dist/`** 仍在本地时运行 `LIVE_URL=https://books.aimake.cc npm run verify:live`。脚本逐一比较 sitemap 中的 HTML、所有展示 SVG、分享配图、离线包、sitemap/robots/字体说明与本地构建的 SHA-256，并检查四个私有路径仍为 404。它只读取线上公开资源，不改变部署；不要在验收前重建 `dist/`：实测同一提交的重复 VitePress 构建仍可能产生不同的前端资源哈希，新产物的 HTML 因引用改变而不能与旧部署逐字节比较。

## Markdown 与 Obsidian 离线包

`/downloads` 始终提供阅读方式说明。可下载 ZIP 需额外设置 `PUBLIC_MARKDOWN_FILE`、`PUBLIC_MARKDOWN_SHA256` 和可选的 `PUBLIC_MARKDOWN_COMMIT`，文件只接受 `output/markdown/agent-systems-md.zip`。门禁调用 `scripts/check_markdown_archive.py`，按当前公开源白名单重新生成预期包，再逐字节比对；不能用一个名字相同的任意 ZIP 通过检查。

获准文件发布到 `/book/agent-systems-md-<提交号前12位>.zip`，返回附件与 `X-Robots-Tag: noindex`，保留准确版本及散列。读者下载、解压后从包内 README 与 `book/CONTENTS.md` 进入；Obsidian 用“打开文件夹作为仓库”，无需插件、登录或运行脚本。更新时另解压新目录，不覆盖读者的个人笔记。

## 浏览器验收与分享配图

`npm test` 检查导航、标题与统计 URL 隐私策略；`npm run build:public` 检查完整发布包。额外浏览器检查覆盖 390/1440px 首页、三张入口卡片、图稿放大/键盘关闭、干净链接分享及离线包入口；截图输出到忽略的 `output/review/`，不作为正文插图。

```bash
python3 -m pip install -r site/requirements-test.txt
python3 -m playwright install chromium
python3 site/scripts/check_reader.py --url http://127.0.0.1:4173
python3 site/scripts/check_reader.py --url https://books.aimake.cc --live
```

本地需另启动 `npm run preview -- --host 127.0.0.1 --port 4173`。若已有 Chrome，可加 `--channel chrome` 而不下载浏览器。分享卡的可维护设计源在 `site/assets/book-share.html`，运行 `check_reader.py --export-share-card` 重导出 1200×630 PNG；重导出后仍须目视检查，不把截图当作正文的 Excalidraw 图源。

## 当前验收记录

本文件只说明构建与验收方法，不维护一份会过期的部署报告。当前覆盖、已验证范围与未完成项见[路线页](../docs/roadmap.md)；线上具体内容以部署后从**同一份 `dist/`**运行的 `verify:live` 结果为准。非作者读者试读、版权终审与印前验收仍是独立门槛，不能由站点检查代替。
