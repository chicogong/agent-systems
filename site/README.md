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
- `scripts/verify-public.mjs` 对 HTML 页数、站内链接、sitemap、canonical、robots、私有仓标记和输出文件类型做发布前门禁。生成物约 60 个 HTML 页面，其中 51 篇来自书稿清单。
- 首页与每章明确标识“在线预览稿”；静态源码阅读不等于运行实测。站点允许搜索引擎抓取，但 robots 不是访问控制。正文与原创图采用 CC BY 4.0，图内嵌字体的许可另列在 `/THIRD-PARTY-NOTICES.txt`。

目前 Vercel 项目未连接 Git；部署前先从最终书稿重新构建并通过门禁，再把 `dist/` 部署到已有的 `agent-systems-reader` 项目。不要让 Vercel 构建直接读取私有书稿仓库，也不要上传 PDF 或提交/推送本地工作树来触发部署。

## 本次验收

2026-09-23 由最终书稿工作树构建出 51 篇正文、8 篇补充页和 24 张展示 SVG；本地门禁验证 60 个 HTML 页面及站内链接，线上逐一请求 60 个阅读 URL，并抽查图、sitemap、robots 和版权说明均为 HTTP 200。PDF、仓库元数据、未发布页面和可编辑图源入口返回 HTTP 404。页面在桌面与 390px 手机视口检查了目录、章节、图示与阅读宽度；仍需外部读者试读和内容终审，不能据此称正式出版。
