# 图解 Agent 系统 · 在线阅读站

[线上预览](https://books.aimake.cc/) 是公开阅读入口，**不是** GitHub 书稿仓库的公开镜像。书稿仓库目前仍为私有；本站仅发布书稿清单中的 Markdown 正文、少量阅读索引与来源说明，以及对应展示用 SVG。PDF、可编辑 Excalidraw 图源、构建脚本和仓库元数据不在公开产物中。

## 唯一内容源

VitePress 1.6.4 只负责静态 HTML 呈现。脚本 `scripts/prepare-public.mjs` 从仓库根目录的 `book/manifest.txt` 按顺序读取正文，生成首页目录、章节路由、导航和图稿的文字说明；正文仍只在原 Markdown 文件里维护。额外公开的 8 篇是机制/系统/对照索引及来源记录，不进入书稿清单。它们帮助保留书内引用的证据路径。

同仓运行时无需指定内容根目录。独立工作树联调可设 `BOOK_CONTENT_ROOT` 指向待验收的书稿根目录，确保生成的是同一版稿件，而不是旧分支。生产构建必须设置实际 HTTPS 站点域名作为 `SITE_URL`，供 canonical、sitemap 和 robots 使用。

```bash
cd site
npm ci
SITE_URL=https://books.aimake.cc DEPLOY_TARGET=vercel npm run build:public
```

构建输出在 `site/.vitepress/dist/`，不提交到 Git。生成的 `site/content/` 和导航 JSON 也不提交。私有本地小样仍可用 `npm run dev`，但它只有旧的 8 页，不代表公开站覆盖范围。

## 公共产物边界

- `npm run build:public` 将章节 Markdown 内链改为站内路由，保留固定版本的公开上游源码链接。指向私有 `chicogong/agent-systems` 的链接不会输出。
- 图只复制展示 SVG；同页附图的文字说明和原尺寸 SVG 链接，不复制 `.excalidraw` 或 PNG。未纳入书稿的内部计划页、贡献流程和模板页不作为网站正文发布。
- `scripts/verify-public.mjs` 对 HTML 页数、站内路由与标题锚点、sitemap、canonical、分享/结构化元信息、robots、私有仓标记和输出文件类型做发布前门禁。本轮生成 64 个 HTML 页面，其中 54 篇来自书稿清单，另有反馈页。`Check guide structure` 的 `public-site` job 在每次推送/PR 运行同一门禁，不自动部署。
- 首页与每章明确标识“在线预览稿”；静态源码阅读不等于运行实测。站点允许搜索引擎抓取，但 robots 不是访问控制。正文与原创图采用 CC BY 4.0，图内嵌字体的许可另列在 `/THIRD-PARTY-NOTICES.txt`。

## 搜索发现与阅读反馈

首页先说明本书能解决的问题，再给出初学、实现和架构对照三条路线与一张代表性图；每章仍以原文的具体问题、固定源码证据和边界为主。页面输出唯一 canonical、独立 description、Open Graph 信息与适度的 JSON-LD（首页为 WebSite，正文为 Article）；sitemap 与 robots 同源。结构化数据只是帮助机器理解页面，不保证获得富媒体展示或 AI 引用。不要为了所谓 GEO 在正文堆关键词或编造未核验的结论。

[反馈页](https://books.aimake.cc/feedback)与每章末尾的预填邮件链接使用作者已公开的邮箱，不收集站内评论、账号或阅读行为。私有书稿仓的 Issues 暂不作为公共反馈入口。接入公开表单前，要先决定垃圾邮件、隐私告知、数据留存和处理责任。

Search Console 的站点所有权验证、提交 sitemap、索引与点击数据监测是部署后的账号操作；**构建通过或站点能访问都不等于已经被收录**。

## PDF 在线阅读的发布门槛

同域名放 PDF 技术上可行：保留 HTML 为主要可搜索、可缩放的阅读版，再提供独立 PDF 页面、浏览器原生预览与下载后备链接。当前 PDF 仍是私有电子校样，**不得直接复制进 `public/`**：文件内还有指向私有 GitHub 仓库的注释链接，公开读者无法访问；还需完成外部材料/图稿权益、封面与整本书的阅读校验。先从同一书稿生成公共阅读版，替换私有链接，再用 `python3 scripts/check_book_pdf.py --public-readiness` 检查链接；该门禁目前会按预期失败。之后还需核验版本标识及文件散列，再人工决定是否公开。若将 PDF 作为 HTML 的替代格式提供，还要明确其索引策略，避免同一正文的两个 URL 互相竞争。

目前 Vercel 项目未连接 Git；部署前先从最终书稿重新构建并通过门禁，再把 `dist/` 部署到已有的 `agent-systems-reader` 项目。不要让 Vercel 构建直接读取私有书稿仓库，也不要上传 PDF 或提交/推送本地工作树来触发部署。

部署后，在同一份构建产物仍在本地时运行 `LIVE_URL=https://books.aimake.cc npm run verify:live`。脚本逐一比较 sitemap 中的 HTML、所有展示 SVG、sitemap/robots/字体说明与本地构建的 SHA-256，并检查四个私有路径仍为 404。它只读取线上公开资源，不改变部署；若随后重新构建了本地 `dist/`，应先确认新产物与线上对应同一提交再比较。

## 本次验收

2026-09-24 从当前书稿构建出 54 篇正文、8 篇补充页、1 个反馈页和 25 张展示 SVG；本地门禁验证 64 个 HTML 页面及站内链接和标题锚点、sitemap、canonical、分享/结构化元信息、robots 和产物白名单。桌面浏览器已抽看首页、Pi 章节和反馈页；此前的 390px 手机视口检查对应旧站点，新增页面仍需复核。线上字节一致性须在本轮部署后重新执行。非作者读者试读仍是独立验收项，不能据此称正式出版。
