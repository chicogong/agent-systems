# 图解 Agent 系统 · 在线阅读站

[线上预览](https://books.aimake.cc/) 是公开阅读入口，**不是** GitHub 书稿仓库的公开镜像。默认构建仅发布书稿清单中的 Markdown 正文、少量阅读索引与来源说明，以及对应展示用 SVG；可编辑 Excalidraw 图源、构建脚本和仓库元数据不在网站产物中。PDF 只有经过独立审稿、散列锁定并显式启用时才加入。

## 唯一内容源

VitePress 1.6.4 只负责静态 HTML 呈现。脚本 `scripts/prepare-public.mjs` 从仓库根目录的 `book/manifest.txt` 按顺序读取正文，生成首页目录、章节路由、章节位置与前后篇导航，以及图稿的文字说明；正文仍只在原 Markdown 文件里维护。GitHub 的 `book/CONTENTS.md` 同样由清单派生。额外公开的 8 篇是机制/系统/对照索引及来源记录，不进入书稿清单。它们帮助保留书内引用的证据路径。

同仓运行时无需指定内容根目录。独立工作树联调可设 `BOOK_CONTENT_ROOT` 指向待验收的书稿根目录，确保生成的是同一版稿件，而不是旧分支。生产构建必须设置实际 HTTPS 站点域名作为 `SITE_URL`，供 canonical、sitemap 和 robots 使用。

```bash
cd site
npm ci
SITE_URL=https://books.aimake.cc DEPLOY_TARGET=vercel npm run build:public
```

构建输出在 `site/.vitepress/dist/`，不提交到 Git。生成的 `site/content/` 和导航 JSON 也不提交。私有本地小样仍可用 `npm run dev`，但它只有旧的 8 页，不代表公开站覆盖范围。

## 公共产物边界

- `npm run build:public` 将已发布章节的 Markdown 内链改为站内路由，保留固定版本的公开上游源码链接；未收入网站的本仓页面链接到公开 GitHub 源仓。网站产物仍不包含仓库源文件。
- 图只复制展示 SVG；同页附图的文字说明和原尺寸 SVG 链接，不复制 `.excalidraw` 或 PNG。未纳入书稿的内部计划页、贡献流程和模板页不作为网站正文发布。
- `scripts/verify-public.mjs` 对 HTML 页数、书序位置与前后篇链接、站内路由与标题锚点、sitemap、canonical、分享/结构化元信息、robots 和输出文件类型做发布前门禁。默认生成 64 个 HTML 页面；显式启用 PDF 时才生成第 65 页和唯一许可的 PDF 文件。`Check guide structure` 的 `public-site` job 在每次推送/PR 运行默认门禁，不自动部署。
- 首页与每章明确标识“在线预览稿”；静态源码阅读不等于运行实测。站点允许搜索引擎抓取，但 robots 不是访问控制。正文与原创图采用 CC BY 4.0，图内嵌字体的许可另列在 `/THIRD-PARTY-NOTICES.txt`。

## 搜索发现与阅读反馈

首页先说明本书能解决的问题，再给出初学、实现和架构对照三条路线与一张代表性图；每章仍以原文的具体问题、固定源码证据和边界为主。页面输出唯一 canonical、独立 description、Open Graph 信息与适度的 JSON-LD（首页为 WebSite，正文为 Article）；sitemap 与 robots 同源。结构化数据只是帮助机器理解页面，不保证获得富媒体展示或 AI 引用。不要为了所谓 GEO 在正文堆关键词或编造未核验的结论。

[反馈页](https://books.aimake.cc/feedback)与每章末尾的预填邮件链接使用作者已公开的邮箱，不收集站内评论、账号或阅读行为。GitHub Issues 可用于可公开复现的勘误；私人或敏感信息仍通过邮件沟通。接入公开表单前，要先决定垃圾邮件、隐私告知、数据留存和处理责任。

Search Console 的站点所有权验证、提交 sitemap、索引与点击数据监测是部署后的账号操作；**构建通过或站点能访问都不等于已经被收录**。

## PDF 在线阅读的发布门槛

同域名 PDF 采用独立 `/pdf` 页面、浏览器原生预览和显眼的下载后备；小屏不嵌入 PDF 阅读器，避免浏览器不支持时出现黑框。HTML 仍是主要可搜索、可缩放和辅助技术阅读版。PDF 尚未制作语义标签，封面插画也不是 300 PPI 印刷母版。PDF 文件单独由 Vercel 回应 `X-Robots-Tag: noindex`，其阅读说明页仍可被发现；这种非 HTML 索引控制符合 [Google 的说明](https://developers.google.com/search/docs/crawling-indexing/robots-meta-tag)。

公共阅读版使用同一书稿清单，内部可用链接改到网站；`book.yml` 在每次审稿构建中额外生成并检查它，但仍只上传为审稿 Artifact。**不允许直接把默认校样复制到网站。** 每次更新前人工审查内容、权益、图文和外链，再从最终提交构建公共版，运行 `python3 scripts/check_book_pdf.py output/pdf/agent-systems-public-preview.pdf --public-readiness`，记录该文件的 SHA-256。只有明确指定如下三个变量，网站构建才会再次运行 PDF 检查、比对 SHA 并复制该文件；未设置时维持无 PDF 的默认公开包：

```bash
cd site
PUBLIC_PDF_FILE=/绝对路径/agent-systems/output/pdf/agent-systems-public-preview.pdf \
PUBLIC_PDF_SHA256=<已审稿文件的64位sha256> \
PDF_CHECK_PYTHON=python3 \
SITE_URL=https://books.aimake.cc DEPLOY_TARGET=vercel npm run build:public
```

Vercel 部署前须人工核对 `dist/pdf.html`、`dist/book/agent-systems-public-preview.pdf`、`dist/vercel.json` 和构建日志，再从同一份 `dist/` 部署。`verify:live` 会在 PDF 模式下连同文件字节和线上 `X-Robots-Tag` 一起检查。构建和测试通过并非权益许可或作者的公开发布决定。

目前 Vercel 项目未连接 Git；部署前先从最终书稿重新构建并通过门禁，再把 `dist/` 部署到已有的 `agent-systems-reader` 项目。例如从 `site/` 执行 `vercel link --cwd .vitepress/dist --scope chico-projects --project agent-systems-reader --yes`，核对生成的 `dist/vercel.json` 和链接的项目，再执行 `vercel deploy --cwd .vitepress/dist --prod --yes`。不要让 Vercel 构建直接读取书稿仓库，也不要把推送工作树等同于网站部署。

部署后，在**实际部署的同一份 `dist/`** 仍在本地时运行 `LIVE_URL=https://books.aimake.cc npm run verify:live`。脚本逐一比较 sitemap 中的 HTML、所有展示 SVG、sitemap/robots/字体说明与本地构建的 SHA-256，并检查四个私有路径仍为 404。它只读取线上公开资源，不改变部署；不要在验收前重建 `dist/`：实测同一提交的重复 VitePress 构建仍可能产生不同的前端资源哈希，新产物的 HTML 因引用改变而不能与旧部署逐字节比较。

## 当前验收记录

本文件只说明构建与验收方法，不维护一份会过期的部署报告。当前覆盖、已验证范围与未完成项见[路线页](../docs/roadmap.md)；线上具体内容以部署后从**同一份 `dist/`**运行的 `verify:live` 结果为准。非作者读者试读、版权终审与印前验收仍是独立门槛，不能由站点检查代替。
