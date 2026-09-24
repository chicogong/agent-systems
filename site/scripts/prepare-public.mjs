import { cp, mkdir, readFile, rm, stat, writeFile } from 'node:fs/promises'
import { createHash } from 'node:crypto'
import { execFileSync } from 'node:child_process'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const site = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const repo = path.resolve(process.env.BOOK_CONTENT_ROOT || path.join(site, '..'))
const output = path.join(site, 'content')
const pdfFile = process.env.PUBLIC_PDF_FILE
const pdfName = 'agent-systems-public-preview.pdf'
if (pdfFile && process.env.DEPLOY_TARGET !== 'vercel') throw new Error('Public PDF builds require the reviewed Vercel noindex header configuration')
const origin = process.env.SITE_URL
if (!origin || !/^https:\/\/[^/]+$/.test(origin)) throw new Error('Set SITE_URL to the intended HTTPS origin')

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
    if (/^https?:\/\//.test(target)) {
      return /^https:\/\/github\.com\/chicogong\/agent-systems(?:\/|$)/.test(target) ? label : full
    }
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
    return label + '（仓库开放后提供）'
  })
}
function explanation(markdown) {
  return markdown.split(/\n\s*\n/).filter((part) =>
    !part.startsWith('#') && !part.startsWith('[') && !part.startsWith('可在此目录') && !part.startsWith('状态：')
  ).join('\n\n').trim()
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
await rm(output, { recursive: true, force: true })
await mkdir(path.join(output, 'public', 'assets', 'figures'), { recursive: true })
for (const { source, group } of paths) {
  const original = await readFile(path.join(repo, source), 'utf8')
  const title = original.match(/^#\s+(.+)$/m)?.[1]?.trim()
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
  const feedback = feedbackMailto('《图解 Agent 系统》阅读反馈：' + title, '章节：' + title + '\n页面：' + origin + route(source) + '\n问题或建议：\n相关证据/链接（如有）：\n')
  await mkdir(path.dirname(destination), { recursive: true })
  await writeFile(destination, frontmatter + transformed + '\n\n---\n\n在线预览稿：书稿仍在校稿，系统篇以文内固定源码版本为准；静态阅读不等于运行验收。发现错误或有改进建议？[按本章填写邮件](' + feedback + ')，或查看[反馈说明](/feedback)。\n')
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
const home = `---
description: "《图解 Agent 系统》在线阅读：从 Agent 运行机制到固定源码版本的开源实现与横向对照。"
---

# 图解 Agent 系统

从运行机制到开源实现，沿问题读懂 Agent 怎样决策、调用工具、管理上下文与记忆，并在权限和失败边界下完成任务。这是一本持续校稿的免费中文技术书，正文可直接在网页阅读。

> **在线预览稿。** 本站已收录书稿清单中的 ${chapterCount} 篇正文和部分阅读索引与来源说明。${pdfFile ? 'PDF 电子校样可在线阅读' : 'PDF 暂未在本站发布'}；可编辑图源与脚本不随网站发布，能否从源码仓访问取决于仓库可见性。系统剖面以篇内固定源码版本为准，不代表运行评测。

## 选择你的阅读路线

- **初次接触 Agent**：从[阅读指南](/front/reading-guide)和[行动闭环](/concepts/agent-loop)开始。先弄清 Agent、工具、上下文和停止条件分别承担什么责任。
- **正在实现 Agent**：沿[学习路径](/learning-path)看机制，再进入 [Pi 源码导读](/systems/pi)、[Codex 源码导读](/systems/codex)等固定版本案例，核对关键代码路径。
- **正在选型或做架构评审**：先看[运行循环与停止条件对照](/comparisons/loop-and-stop)，再按项目与问题跳转；比较的是可验证的设计取舍，不是产品排行榜。

## 先用一张图建立全局认识

![Agent 的观察、思考、行动与反馈循环](/assets/figures/agent-loop/diagram.svg)

[打开原尺寸 SVG](/assets/figures/agent-loop/diagram.svg) · [阅读图的解释与边界](/concepts/agent-loop)

## 反馈与更正

发现事实错误、图中文字难读或源码链接失效？[查看反馈方式](/feedback)。阅读不需要登录；目前不收集站内评论。

${pdfFile ? '## 离线阅读\n\n[打开 PDF 电子校样](/pdf)。它和在线正文同源，提供浏览器预览与下载；在线章节仍是检索、引用和无障碍阅读的优先入口。\n' : ''}

${contents}

---

原创文字与图：chicogong 与贡献者，按 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) 提供；引用的上游项目、商标和外部材料归各自权利人。网站与源码仓分别发布，以 GitHub 页面显示的仓库可见性为准。
`
await writeFile(path.join(output, 'index.md'), home)
const generalFeedback = feedbackMailto('《图解 Agent 系统》阅读反馈', '章节或页面：\n问题或建议：\n相关证据/链接（如有）：\n')
await writeFile(path.join(output, 'feedback.md'), `---
description: "《图解 Agent 系统》的勘误、图稿与阅读体验反馈方式。"
---

# 阅读反馈

这本书正在校稿。事实、代码路径、图稿、引用、排版与阅读体验方面的反馈都欢迎；请尽可能指出具体章节或页面，以及你核对过的依据。

## 反馈方式

[发送反馈邮件](${generalFeedback}) 给 **ghr7719@gmail.com**。每章末尾的“按本章填写邮件”会预填章节与页面地址；如果设备没有配置邮件客户端，也可以复制邮箱地址手动发送。

建议包含：页面链接、原句或图中位置、问题说明，以及可公开引用的上游源码或文档链接。请不要通过邮件发送密钥、私有资料或个人敏感信息。

目前没有站内账户、评论区或行为追踪；反馈统一使用邮件，GitHub Issues 暂不作为本网站的反馈入口。重要勘误会在后续版本中修正，并在公开更新说明中标明；收到邮件不代表每项建议都会被采纳。
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
    execFileSync(process.env.PDF_CHECK_PYTHON || 'python3', [path.join(repo, 'scripts/check_book_pdf.py'), expected, '--public-readiness'], { cwd: repo, encoding: 'utf8' })
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

[打开或下载 PDF 电子校样](/book/${pdfName}) · [返回在线目录](/) · [提交阅读反馈](/feedback)

<object class="book-pdf-preview" data="/book/${pdfName}" type="application/pdf" aria-label="图解 Agent 系统 PDF 电子校样">
  浏览器无法直接显示 PDF。请使用上方下载链接。
</object>

文件 SHA-256：\`${actual}\`。本电子校样已将内部可用链接改为在线阅读站链接，未包含可编辑图源。源码仓与网站分别发布。\n`)
}
await writeFile(path.join(site, '.vitepress', 'generated-sidebar.json'), JSON.stringify(ordered, null, 2) + '\n')
await writeFile(path.join(output, 'public', 'robots.txt'), 'User-agent: *\nAllow: /\n\nUser-agent: OAI-SearchBot\nAllow: /\n\nUser-agent: GPTBot\nDisallow: /\n\nSitemap: ' + origin + '/sitemap.xml\n')
await writeFile(path.join(output, 'public', 'THIRD-PARTY-NOTICES.txt'), 'Diagram font notices\n\nNunito: Copyright 2014 The Nunito Project Authors. SIL Open Font License 1.1.\nhttps://github.com/google/fonts/blob/main/ofl/nunito/OFL.txt\n\nComic Shanns: Copyright 2018 Shannon Miwa. MIT License.\nhttps://github.com/shannpersand/comic-shanns/blob/master/LICENSE\n')
await mkdir(path.join(output, 'public', 'licenses'), { recursive: true })
await cp(path.join(site, 'third-party', 'Nunito-OFL.txt'), path.join(output, 'public', 'licenses', 'Nunito-OFL.txt'))
await cp(path.join(site, 'third-party', 'ComicShanns-MIT.txt'), path.join(output, 'public', 'licenses', 'ComicShanns-MIT.txt'))
console.log('Prepared ' + chapterCount + ' public book chapters, ' + (paths.length - chapterCount) + ' supplementary pages, ' + figures.size + ' SVG figures, ' + unresolved.size + ' non-book references stripped.')
if (unresolved.size) console.log([...unresolved].slice(0, 25).join('\n'))
