import { cp, mkdir, readFile, rm, stat, writeFile } from 'node:fs/promises'
import { createHash } from 'node:crypto'
import { execFileSync } from 'node:child_process'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { plainLabel, figureExplanation } from './page-metadata.mjs'

const site = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const repo = path.resolve(process.env.BOOK_CONTENT_ROOT || path.join(site, '..'))
const output = path.join(site, 'content')
const pdfFile = process.env.PUBLIC_PDF_FILE
const pdfName = 'agent-systems-public-preview.pdf'
const markdownFile = process.env.PUBLIC_MARKDOWN_FILE
const analyticsEnabled = process.env.VITE_READER_ANALYTICS === '1'
if ((pdfFile || markdownFile) && process.env.DEPLOY_TARGET !== 'vercel') throw new Error('Public downloads require the reviewed Vercel noindex header configuration')
const origin = process.env.SITE_URL
if (!origin || !/^https:\/\/[^/]+$/.test(origin)) throw new Error('Set SITE_URL to the intended HTTPS origin')
const sourceCommit = execFileSync('git', ['-C', repo, 'rev-parse', 'HEAD'], { encoding: 'utf8' }).trim()
if (!/^[a-f0-9]{40}$/.test(sourceCommit)) throw new Error('Book source must have a full Git commit')
function artifactCommit(value) {
  const commit = value || sourceCommit
  if (!/^[a-f0-9]{40}$/.test(commit)) throw new Error('Download source revision must be a full Git commit')
  execFileSync('git', ['-C', repo, 'merge-base', '--is-ancestor', commit, sourceCommit])
  return commit
}
const pdfSourceCommit = pdfFile ? artifactCommit(process.env.PUBLIC_PDF_COMMIT) : null
const markdownSourceCommit = markdownFile ? artifactCommit(process.env.PUBLIC_MARKDOWN_COMMIT) : null
const markdownName = markdownFile ? `agent-systems-md-${markdownSourceCommit.slice(0, 12)}.zip` : null
const sourceDirty = Boolean(execFileSync('git', ['-C', repo, 'status', '--porcelain', '--untracked-files=normal'], { encoding: 'utf8' }).trim())
if (process.env.SITE_RELEASE === '1' && sourceDirty) throw new Error('SITE_RELEASE requires a clean book source worktree')
const sourceVersion = sourceDirty
  ? `本地未提交稿（基于 ${sourceCommit.slice(0, 12)}，不能仅凭提交号还原）`
  : `提交 ${sourceCommit}`
const sourceVersionMarkdown = sourceDirty
  ? `本地未提交稿，基于 [${sourceCommit.slice(0, 12)}](https://github.com/chicogong/agent-systems/commit/${sourceCommit})；不能仅凭该提交还原本页。`
  : `书稿提交：[${sourceCommit.slice(0, 12)}](https://github.com/chicogong/agent-systems/commit/${sourceCommit})。`

const manifest = (await readFile(path.join(repo, 'book/manifest.txt'), 'utf8')).split(/\r?\n/)
const groups = [{ text: '导读', items: [] }]
let group = groups[0]
const paths = []
for (const line of manifest) {
  const entry = line.trim()
  if (!entry || entry.startsWith('#')) continue
  if (entry.startsWith('@part ')) {
    group = { text: entry.slice(6), items: [] }
    groups.push(group)
    continue
  }
  const source = entry.replace(/^@(front|back)\s+/, '')
  if (!source.endsWith('.md')) throw new Error('Unexpected manifest entry: ' + entry)
  paths.push({ source, group })
}
if (paths.length < 50) throw new Error('Expected a full book, found only ' + paths.length + ' chapters')
const chapterCount = paths.length
const bookPaths = paths.map(({ source, group }) => ({ source, group }))
const bookTitles = new Map(await Promise.all(bookPaths.map(async ({ source }) => {
  const markdown = await readFile(path.join(repo, source), 'utf8')
  const title = markdown.match(/^#\s+(.+)$/m)?.[1]?.trim()
  if (!title) throw new Error(source + ': missing H1')
  return [source, plainLabel(title)]
})))
const bookPosition = new Map(bookPaths.map(({ source, group }, index) => [source, { index, group }]))
const supplements = { text: '阅读索引与来源说明', items: [] }
groups.push(supplements)
for (const source of [
  'docs/concepts/README.md',
  'docs/systems/README.md',
  'docs/comparisons/README.md',
  'sources/README.md',
  'sources/jev.md',
  'sources/mcp-skill-tool-lifecycle.md',
  'sources/kimi-code.md',
  'sources/mimo-code.md'
]) paths.push({ source, group: supplements })

function route(source) {
  let base = source.replace(/\.md$/, '')
  if (base.startsWith('book/frontmatter/')) base = base.replace('book/frontmatter/', 'front/')
  else if (base.startsWith('book/backmatter/')) base = base.replace('book/backmatter/', 'back/')
  else if (base.startsWith('docs/')) base = base.slice(5)
  base = base.replace(/\/README$/, '')
  return '/' + base
}
const routes = new Map(paths.map(({ source }) => [source, route(source)]))
const figures = new Set()
const unresolved = new Set()
function resolve(source, target) {
  const [pathname, suffix = ''] = target.split(/(?=[?#])/)
  const resolved = path.posix.normalize(path.posix.join(path.posix.dirname(source), pathname))
  if (resolved.startsWith('../') || resolved.startsWith('/')) throw new Error(source + ': path escapes repository: ' + target)
  return { resolved, suffix }
}
const figureOwners = new Map()
for (const { source } of paths) {
  const markdown = await readFile(path.join(repo, source), 'utf8')
  for (const match of markdown.matchAll(/!\[[^\]]*\]\(([^)]+)\)/g)) {
    const resolved = resolve(source, match[1]).resolved
    if (/^figures\/[^/]+\/diagram\.svg$/.test(resolved)) {
      const slug = resolved.split('/')[1]
      if (!figureOwners.has(slug)) figureOwners.set(slug, route(source))
    }
  }
}
function rewrite(markdown, source) {
  // In book source, editable/PNG links often share a line with a public text-version
  // link. Drop their whole list item before rewriting so no inert labels survive.
  const withoutPrivateAssets = markdown.split('\n').map((line) => line.split(/\s+·\s+/).filter((item) =>
    !/^\[[^\]]+\]\([^)]*\/figures\/[^/]+\/(?:scene\.excalidraw|preview\.png)\)$/.test(item)
  ).join(' · ')).join('\n')
  return withoutPrivateAssets.replace(/(!?)\[([^\]]+)\]\(([^\s)]+)\)/g, (full, image, label, target) => {
    if (target.startsWith('#')) return full
    if (/^https?:\/\//.test(target)) return full
    if (/^mailto:[^@\s)]+@[^@\s)]+\.[^@\s)]+$/i.test(target)) return full
    if (/^[a-z]+:/i.test(target) || target.startsWith('//')) throw new Error(source + ': unsupported URL scheme ' + target)
    const { resolved, suffix } = resolve(source, target)
    if (image && /^figures\/[^/]+\/diagram\.svg$/.test(resolved)) {
      const slug = resolved.split('/')[1]
      figures.add(slug)
      return '![' + label + '](/assets/figures/' + slug + '/diagram.svg)\n\n<a class="figure-original" href="/assets/figures/' + slug + '/diagram.svg" target="_blank" rel="noopener">查看原尺寸 SVG（可缩放）</a>'
    }
    if (/^figures\/[^/]+\/diagram\.svg$/.test(resolved)) {
      const slug = resolved.split('/')[1]
      figures.add(slug)
      return '[' + label + '](/assets/figures/' + slug + '/diagram.svg)'
    }
    if (/^figures\/[^/]+\/README\.md$/.test(resolved)) {
      const slug = resolved.split('/')[1]
      figures.add(slug)
      const owner = figureOwners.get(slug)
      if (!owner) throw new Error(source + ': no public host page for figure text ' + slug)
      return '[' + label + '](' + owner + '#图的文字说明-' + slug + ')'
    }
    if (/^figures\/[^/]+\/(?:scene\.excalidraw|preview\.png)$/.test(resolved)) return ''
    if (resolved === 'CONTRIBUTING.md') return '[反馈说明](/feedback)'
    if (resolved === 'LICENSE-CONTENT.md') return '[' + label + '](https://creativecommons.org/licenses/by/4.0/)'
    if (resolved === 'LICENSE-CODE') return '[' + label + '](https://opensource.org/license/mit)'
    if (resolved === 'README.md') return '[' + label + '](/)'
    if (routes.has(resolved)) return '[' + label + '](' + routes.get(resolved) + suffix + ')'
    unresolved.add(source + ': ' + target)
    return '[' + label + '](https://github.com/chicogong/agent-systems/blob/main/' + resolved + suffix + ')'
  })
}
function explanation(markdown) {
  return figureExplanation(markdown)
}
function pageDescription(markdown, title) {
  const paragraphs = markdown.replace(/^---\r?\n[\s\S]*?\r?\n---\r?\n/, '').split(/\n\s*\n/)
  for (const paragraph of paragraphs) {
    const text = paragraph.trim()
    if (!text || /^(?:#|>|[-*+] |[0-9]+\. |\||\x60{3}|~~~|<!--|<)/.test(text)) continue
    if (/^\[返回/.test(text) || /^(?:图源|可编辑图源|PNG 预览|SVG 预览)/.test(text)) continue
    const withoutLinks = text.replace(/!?\[[^\]]*\]\([^)]+\)/g, '').replace(/[·｜|,，;；:：\s]/g, '')
    if (!withoutLinks) continue
    const clean = text
      .replace(/!\[([^\]]*)\]\([^)]+\)/g, '$1')
      .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
      .replace(/<[^>]*>/g, '')
      .replace(/[\x60*_~]/g, '')
      .replace(/\s+/g, ' ')
      .trim()
    if (clean.length < 20) continue
    const chars = [...clean]
    if (chars.length <= 155) return clean
    const cut = chars.slice(0, 150)
    let end = -1
    for (let i = 100; i < cut.length; i++) if (/[。！？；]/.test(cut[i])) end = i
    return end >= 100 ? cut.slice(0, end + 1).join('') : cut.join('') + '…'
  }
  return title
}
function feedbackMailto(subject, body) {
  return 'mailto:ghr7719@gmail.com?subject=' + encodeURIComponent(subject) + '&body=' + encodeURIComponent(body)
}
function escapeHtml(value) {
  return value.replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;')
}
function chapterNavigation(source) {
  const position = bookPosition.get(source)
  if (!position) return ''
  const { index, group } = position
  const previous = bookPaths[index - 1]?.source
  const next = bookPaths[index + 1]?.source
  const link = (target, label, className) => target
    ? `<a class="${className}" href="${route(target)}" aria-label="${label}：${escapeHtml(bookTitles.get(target))}"><span>${label}</span><strong>${escapeHtml(bookTitles.get(target))}</strong></a>`
    : `<span class="${className} is-empty" aria-hidden="true"></span>`
  return `<nav class="reading-position" aria-label="本书章节导航" data-book-position="${index + 1}/${chapterCount}">
  <div class="reading-position-heading"><span class="reading-position-kicker">图解 Agent 系统 · ${escapeHtml(group.text)}</span><span class="reading-position-number">${String(index + 1).padStart(2, '0')} / ${chapterCount}</span></div>
  <div class="reading-position-links">${link(previous, '上一篇', 'reading-position-previous')}<a class="reading-position-contents" href="/#全书目录">全书目录</a>${link(next, '下一篇', 'reading-position-next')}</div>
</nav>\n\n`
}
await rm(output, { recursive: true, force: true })
await mkdir(path.join(output, 'public', 'assets', 'figures'), { recursive: true })
for (const { source, group } of paths) {
  const original = await readFile(path.join(repo, source), 'utf8')
  const title = plainLabel(original.match(/^#\s+(.+)$/m)?.[1])
  if (!title) throw new Error(source + ': missing H1')
  const destination = path.join(output, route(source).slice(1) + '.md')
  group.items.push({ text: title, link: route(source) })
  const usedFigures = [...original.matchAll(/!\[[^\]]*\]\(([^)]+)\)/g)]
    .map((match) => resolve(source, match[1]).resolved)
    .filter((name) => /^figures\/[^/]+\/diagram\.svg$/.test(name))
    .map((name) => name.split('/')[1])
  let transformed = rewrite(original, source)
  for (const slug of [...new Set(usedFigures)]) {
    const readme = await readFile(path.join(repo, 'figures', slug, 'README.md'), 'utf8')
    transformed += '\n\n## 图的文字说明 · ' + slug + ' {#图的文字说明-' + slug + '}\n\n' + rewrite(explanation(readme), 'figures/' + slug + '/README.md') + '\n'
  }
  const frontmatter = '---\ndescription: ' + JSON.stringify(pageDescription(original, title)) + '\n---\n\n'
  const feedback = feedbackMailto('《图解 Agent 系统》阅读反馈：' + title, '章节：' + title + '\n页面：' + origin + route(source) + '\n阅读版本：' + sourceVersion + '\n问题或建议：\n相关证据/链接（如有）：\n')
  await mkdir(path.dirname(destination), { recursive: true })
  await writeFile(destination, frontmatter + chapterNavigation(source) + transformed + '\n\n---\n\n在线预览稿：书稿仍在校稿，系统篇以文内固定源码版本为准；静态阅读不等于运行验收。发现错误或有改进建议？[按本章填写邮件](' + feedback + ')，或查看[反馈说明](/feedback)。\n\n' + sourceVersionMarkdown + '\n')
}
for (const slug of figures) {
  const src = path.join(repo, 'figures', slug, 'diagram.svg')
  await stat(src)
  const dir = path.join(output, 'public', 'assets', 'figures', slug)
  await mkdir(dir, { recursive: true })
  await cp(src, path.join(dir, 'diagram.svg'))
}
const ordered = groups.filter((item) => item.items.length)
const contents = ordered.map((part) => '## ' + part.text + '\n\n' + part.items.map((item) => '- [' + item.text + '](' + item.link + ')').join('\n')).join('\n\n')
await mkdir(path.join(output, 'public', 'assets', 'share'), { recursive: true })
await cp(path.join(site, 'assets', 'book-share.png'), path.join(output, 'public', 'assets', 'share', 'book.png'))
await cp(path.join(repo, 'book', 'assets', 'cover-preview.png'), path.join(output, 'public', 'assets', 'share', 'cover.png'))
const home = `---
title: "图解 Agent 系统：入门学习、应用实践与开源实现"
description: "免费中文图解书，面向学生、老师、AI 工具使用者与感兴趣的读者。用讲解、案例和图理解 Agent，把方法带到学习与工作，再按兴趣深入开源实现。"
---

<div class="reader-hero">
  <div>
    <p class="reader-eyebrow">免费中文图解书 · 持续更新预览</p>
    <h1>图解 Agent 系统</h1>
    <p class="reader-lead">学懂 Agent，把方法用起来。</p>
    <p>为学习、教学和工作找到一个起点。先跟着图与例子理解，再用资料做一份自己的成果；想探索 AI 相关方向，继续选择应用、代码或真实系统。</p>
    <div class="reader-entry-links"><a class="reader-start" href="/concepts/agent-loop">从一张图开始读 →</a><a href="/learning-and-practice">找到我的学习入口</a><a href="/downloads">下载与离线阅读</a></div>
  </div>
  <img src="/assets/share/cover.png" width="160" height="240" alt="图解 Agent 系统封面" fetchpriority="high">
</div>

学生、老师、AI 工具使用者和感兴趣的读者都可以开始，不需要先安装框架或购买 API。本书有 ${chapterCount} 篇书稿单元与 ${figures.size} 张机制与实现图；讲解、案例和横向对照按问题相互连接。源码与编程实验按需深入，不是入门前提。

## 从你想做的事情开始

<div class="topic-grid">
  <a class="topic-card" href="/learning-and-practice"><img src="/assets/figures/agent-loop/diagram.svg" width="200" height="125" alt="从资料到带出处回答的运行循环" loading="lazy"><strong>学习、备课或整理工作资料</strong><span>用同一组材料，尝试学习卡片、讨论活动或短简报。</span></a>
  <a class="topic-card" href="/front/reading-guide#和-ai-一起读"><img src="/assets/figures/context-vs-memory/diagram.svg" width="200" height="125" alt="保存的资料与本轮实际输入的关系" loading="lazy"><strong>请 AI 帮我理解，自己检查</strong><span>解释一个关系，换个例子，留下自己的理解与疑问。</span></a>
  <a class="topic-card" href="/learning-path"><img src="/assets/figures/pi-architecture/diagram.svg" width="200" height="125" alt="可选深入：Pi 的运行核心与会话外壳" loading="lazy"><strong>探索方向，继续深入技术</strong><span>先积累一份成果，再选应用、源码或工程路线。</span></a>
</div>

## 按你的目标继续读

- **学生、老师与好奇的读者**：从[学习与应用](/learning-and-practice)开始；跟着资料任务形成回答，再沿[行动闭环](/concepts/agent-loop)解释过程。
- **已经在用 AI，希望提升能力**：尝试[轻量任务卡](/learning-and-practice#留下一张轻量任务卡)，练习说清目标、选择资料和核对结果。也可选用[AI 陪读](/front/reading-guide#和-ai-一起读)。
- **想探索 AI 相关方向**：用[阅读路线](/learning-path)选择一个小问题，留下作品与修改过程，再决定下一项要学的能力；本书不承诺职位或收入。
- **正在实现 Agent**：沿[学习路径](/learning-path)看机制，再进入 [Pi 源码导读](/systems/pi)、[Codex 源码导读](/systems/codex)等固定版本案例，核对关键代码路径。
- **正在选型或做架构评审**：先看[运行循环与停止条件对照](/comparisons/loop-and-stop)，再按项目与问题跳转；比较的是可验证的设计取舍，不是产品排行榜。

## 先用一张图建立全局认识

![Agent 的观察、思考、行动与反馈循环](/assets/figures/agent-loop/diagram.svg)

[打开原尺寸 SVG](/assets/figures/agent-loop/diagram.svg) · [阅读图的解释与边界](/concepts/agent-loop)

## 反馈与更正

发现事实错误、图中文字难读或源码链接失效？[查看反馈方式](/feedback)。阅读不需要登录；目前不收集站内评论。

## 版本与阅读方式

**在线预览稿。** 系统剖面以篇内固定源码版本为准，不是实时产品排名或运行评测。网页可直接搜索、分享章节；[离线阅读说明](/downloads)提供 PDF、Markdown 与 Obsidian 的入口。可编辑图源与脚本在[公开源码仓](https://github.com/chicogong/agent-systems)。

${sourceVersionMarkdown} 网页与下载文件可能来自不同批次，各自标明来源版本。

## 全书目录

${contents}

---

原创文字与图：chicogong 与贡献者，按 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) 提供；引用的上游项目、商标和外部材料归各自权利人。网站与[源码仓](https://github.com/chicogong/agent-systems)分别发布。
`
await writeFile(path.join(output, 'index.md'), home)
const generalFeedback = feedbackMailto('《图解 Agent 系统》阅读反馈', '章节或页面：\n阅读版本：' + sourceVersion + '\n问题或建议：\n相关证据/链接（如有）：\n')
await writeFile(path.join(output, 'feedback.md'), `---
description: "《图解 Agent 系统》的勘误、图稿与阅读体验反馈方式。"
---

# 阅读反馈

这本书正在校稿。事实、代码路径、图稿、引用、排版与阅读体验方面的反馈都欢迎；请尽可能指出具体章节或页面，以及你核对过的依据。

${sourceVersionMarkdown} PDF 与 Markdown 阅读包有各自的导出版本；请报告你实际阅读的版本或日期。

## 反馈方式

[发送反馈邮件](${generalFeedback}) 给 **ghr7719@gmail.com**。每章末尾的“按本章填写邮件”会预填章节、页面地址和本次站点构建版本；如果设备没有配置邮件客户端，也可以复制邮箱地址手动发送。

可公开的问题也可从[GitHub 阅读反馈表单](https://github.com/chicogong/agent-systems/issues/new?template=reading-feedback.yml)提交。请填写章节位置、所读版本与实际现象。也欢迎告诉作者“哪一段突然没看懂”，不必先证明作者写错了。

建议包含：页面链接、原句或图中位置、问题说明，以及可公开引用的上游源码或文档链接。请不要通过邮件发送密钥、私有资料或个人敏感信息。

目前没有站内账户或评论区。${analyticsEnabled ? '本站启用了 Vercel Web Analytics 的无 Cookie 汇总访问统计，用于了解哪些页面和来源更有帮助；不记录站内搜索词、邮件内容、URL 查询参数或片段，不使用跨站广告追踪。[Vercel 的数据与隐私说明](https://vercel.com/docs/analytics/privacy-policy)列明服务商处理的数据。统计不能证明读者已读完或学会。' : '本站没有启用阅读行为统计。'} 可公开复现的勘误也可提交到[GitHub Issues](https://github.com/chicogong/agent-systems/issues)；涉及个人信息的反馈请使用邮件。重要勘误会在后续版本中修正，并在公开更新说明中标明；收到反馈不代表每项建议都会被采纳。
`)
if (pdfFile) {
  const expected = path.join(repo, 'output', 'pdf', pdfName)
  if (path.resolve(pdfFile) !== expected) throw new Error('PUBLIC_PDF_FILE must point to this book build: ' + expected)
  const sha = process.env.PUBLIC_PDF_SHA256
  if (!/^[a-f0-9]{64}$/.test(sha || '')) throw new Error('PUBLIC_PDF_SHA256 must be the reviewed artifact digest')
  const bytes = await readFile(expected)
  const actual = createHash('sha256').update(bytes).digest('hex')
  if (actual !== sha) throw new Error('Reviewed PDF digest does not match PUBLIC_PDF_FILE')
  try {
    execFileSync(process.env.PDF_CHECK_PYTHON || 'python3', [path.join(repo, 'scripts/check_book_pdf.py'), expected, '--public-readiness', '--expected-commit', pdfSourceCommit], { cwd: repo, encoding: 'utf8' })
  } catch (error) {
    throw new Error('PDF public-readiness check failed: ' + (error.stdout || error.stderr || error.message))
  }
  await mkdir(path.join(output, 'public', 'book'), { recursive: true })
  await cp(expected, path.join(output, 'public', 'book', pdfName))
  await writeFile(path.join(output, 'pdf.md'), `---
description: "《图解 Agent 系统》PDF 电子校样的在线预览、下载及版本校验。"
---

# 阅读 PDF 电子校样

**在线预览稿。** 这是与本网站正文同源构建的电子阅读版，仍在校稿，并非 300 PPI 印刷母版。需要检索和引用单篇内容时，建议优先使用[在线章节目录](/)；PDF 适合离线通读。图像可放大查看，但 PDF 尚未制作语义标签，使用辅助技术阅读时请用 HTML 正文。

PDF 书稿版本：[${pdfSourceCommit.slice(0, 12)}](https://github.com/chicogong/agent-systems/commit/${pdfSourceCommit})。站点 ${sourceVersionMarkdown} 两者可以独立更新；PDF 的“关于本版”页和下方 SHA-256 是文件版本依据。

[打开或下载 PDF 电子校样](/book/${pdfName}) · [返回在线目录](/) · [提交阅读反馈](/feedback)

<object class="book-pdf-preview" data="/book/${pdfName}" type="application/pdf" aria-label="图解 Agent 系统 PDF 电子校样">
  浏览器无法直接显示 PDF。请使用上方下载链接。
</object>

文件 SHA-256：\`${actual}\`。本电子校样已将内部可用链接改为在线阅读站链接，未包含可编辑图源。源码仓与网站分别发布。\n`)
}
if (markdownFile) {
  const expected = path.join(repo, 'output', 'markdown', 'agent-systems-md.zip')
  if (path.resolve(markdownFile) !== expected) throw new Error('PUBLIC_MARKDOWN_FILE must point to this book build')
  const sha = process.env.PUBLIC_MARKDOWN_SHA256
  if (!/^[a-f0-9]{64}$/.test(sha || '')) throw new Error('PUBLIC_MARKDOWN_SHA256 must be the reviewed archive digest')
  const actual = createHash('sha256').update(await readFile(expected)).digest('hex')
  if (actual !== sha) throw new Error('Reviewed Markdown archive digest mismatch')
  execFileSync(process.env.PDF_CHECK_PYTHON || 'python3', [path.join(repo, 'scripts/check_markdown_archive.py'), expected, '--expected-commit', markdownSourceCommit], { cwd: repo })
  await mkdir(path.join(output, 'public', 'book'), { recursive: true })
  await cp(expected, path.join(output, 'public', 'book', markdownName))
}
await writeFile(path.join(output, 'downloads.md'), `---
description: "下载图解 Agent 系统 PDF 与 Markdown 阅读包，在浏览器、Obsidian 或本地 Markdown 阅读器中阅读。"
---

# 下载与离线阅读

**在线预览稿。** 一份 Markdown 书稿生成网页、PDF 和离线包；文件各有来源版本，网站更新不一定同时重导 PDF。打开文件前请看下面的提交号，不把电子校样当作印刷母版。

${sourceVersionMarkdown}

## PDF：离线通读

${pdfFile ? '[打开 PDF 阅读页](/pdf)，或[直接下载电子校样](/book/' + pdfName + ')。PDF 版本：[' + pdfSourceCommit.slice(0, 12) + '](https://github.com/chicogong/agent-systems/commit/' + pdfSourceCommit + ')。' : '本站暂未附带 PDF 文件。可直接阅读[网页章节](/#全书目录)。'}

## Markdown：在 Obsidian 中做笔记

${markdownFile ? '[下载 Markdown 阅读包（ZIP）](/book/' + markdownName + ')。阅读包版本：[' + markdownSourceCommit.slice(0, 12) + '](https://github.com/chicogong/agent-systems/commit/' + markdownSourceCommit + ')。\n\nSHA-256：\`' + process.env.PUBLIC_MARKDOWN_SHA256 + '\`。' : '可从[源码仓](https://github.com/chicogong/agent-systems)获取 Markdown；已审阅读包将在本站提供固定版本下载。'}

1. 解压阅读包，保留全部目录和图片。
2. 用 Markdown 阅读器打开包内的 \`README.md\`；使用 Obsidian 时，选择“打开文件夹作为仓库”，选中解压后的 \`agent-systems-md\`。
3. 从包内目录开始读。章节、图的文字说明、SVG、PNG 和可编辑图源保持相对链接；可选练习放在 \`examples/\`。

不需要安装本书专用插件。阅读包是版本快照，不会覆盖你的笔记，也不会自动更新。新版解压到另一个文件夹，先对照变化，再迁移自己的笔记。解压和看 Markdown 不会运行附带的脚本；可选练习请先阅读说明再执行。

## 在线阅读与反馈

手机阅读、检索和逐章分享优先使用[在线目录](/#全书目录)。发现表述不清、图稿难读或代码问题，请提交[阅读反馈](/feedback)，带上实际阅读的版本。
`)
await writeFile(path.join(output, 'public', 'version.json'), JSON.stringify({
  status: 'preview',
  sourceCommit,
  sourceClean: !sourceDirty,
  pdfSha256: pdfFile ? process.env.PUBLIC_PDF_SHA256 : null,
  pdfSourceCommit,
  markdownSha256: markdownFile ? process.env.PUBLIC_MARKDOWN_SHA256 : null,
  markdownSourceCommit,
  analytics: analyticsEnabled ? 'vercel-aggregate-pageviews' : 'disabled'
}, null, 2) + '\n')
await writeFile(path.join(site, '.vitepress', 'generated-sidebar.json'), JSON.stringify(ordered, null, 2) + '\n')
await writeFile(path.join(output, 'public', 'robots.txt'), 'User-agent: *\nAllow: /\n\nUser-agent: OAI-SearchBot\nAllow: /\n\nUser-agent: GPTBot\nDisallow: /\n\nSitemap: ' + origin + '/sitemap.xml\n')
await writeFile(path.join(output, 'public', 'THIRD-PARTY-NOTICES.txt'), 'Reader and diagram notices\n\nNunito: Copyright 2014 The Nunito Project Authors. SIL Open Font License 1.1.\nhttps://github.com/google/fonts/blob/main/ofl/nunito/OFL.txt\n\nComic Shanns: Copyright 2018 Shannon Miwa. MIT License.\nhttps://github.com/shannpersand/comic-shanns/blob/master/LICENSE\n\n@vercel/analytics 2.0.1: Copyright (c) 2026 Vercel, Inc. MIT License.\nFull license: /licenses/Vercel-Analytics-MIT.txt\n')
await mkdir(path.join(output, 'public', 'licenses'), { recursive: true })
await cp(path.join(site, 'third-party', 'Nunito-OFL.txt'), path.join(output, 'public', 'licenses', 'Nunito-OFL.txt'))
await cp(path.join(site, 'third-party', 'ComicShanns-MIT.txt'), path.join(output, 'public', 'licenses', 'ComicShanns-MIT.txt'))
await cp(path.join(site, 'third-party', 'Vercel-Analytics-MIT.txt'), path.join(output, 'public', 'licenses', 'Vercel-Analytics-MIT.txt'))
console.log('Prepared ' + chapterCount + ' public book chapters, ' + (paths.length - chapterCount) + ' supplementary pages, ' + figures.size + ' SVG figures, ' + unresolved.size + ' non-book references linked to the source repository.')
if (unresolved.size) console.log([...unresolved].slice(0, 25).join('\n'))
