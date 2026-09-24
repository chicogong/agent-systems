import { cp, mkdir, readFile, rm, stat, writeFile } from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const site = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const repo = path.resolve(process.env.BOOK_CONTENT_ROOT || path.join(site, '..'))
const output = path.join(site, 'content')
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
function rewrite(markdown, source) {
  return markdown.replace(/(!?)\[([^\]]+)\]\(([^\s)]+)\)/g, (full, image, label, target) => {
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
      return '[' + label + '](#图的文字说明-' + slug + ')'
    }
    if (/^figures\/[^/]+\/(?:scene\.excalidraw|preview\.png)$/.test(resolved)) return label
    if (resolved === 'README.md') return '[' + label + '](/)'
    if (routes.has(resolved)) return '[' + label + '](' + routes.get(resolved) + suffix + ')'
    unresolved.add(source + ': ' + target)
    return label
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
  await mkdir(path.dirname(destination), { recursive: true })
  await writeFile(destination, frontmatter + transformed + '\n\n---\n\n在线预览稿：书稿仍在校稿，系统篇以文内固定源码版本为准；静态阅读不等于运行验收。\n')
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
const home = '---\ndescription: "《图解 Agent 系统》在线阅读：从 Agent 运行机制到固定源码版本的开源实现与横向对照。"\n---\n\n# 图解 Agent 系统\n\n从运行机制到开源实现，沿问题读懂 Agent 怎样决策、调用工具、管理上下文与记忆，并在权限和失败边界下完成任务。\n\n> **在线预览稿。** 本站已收录书稿清单中的 ' + chapterCount + ' 篇正文和部分阅读索引与来源说明，方便公开阅读；内容仍在校稿。书稿 GitHub 仓库目前保持私有，PDF、可编辑图源和脚本未在本站发布。所有系统剖面都以篇内固定源码版本为准，不代表运行评测。\n\n[从阅读指南开始](/front/reading-guide) · [按学习路径进入](/learning-path) · [先看 Agent loop](/concepts/agent-loop)\n\n' + contents + '\n\n---\n\n原创文字与图：chicogong 与贡献者，按 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) 提供；引用的上游项目、商标和外部材料归各自权利人。当前站点是阅读入口，不表示私有源仓已公开。\n'
await writeFile(path.join(output, 'index.md'), home)
await writeFile(path.join(site, '.vitepress', 'generated-sidebar.json'), JSON.stringify(ordered, null, 2) + '\n')
await writeFile(path.join(output, 'public', 'robots.txt'), 'User-agent: *\nAllow: /\n\nUser-agent: OAI-SearchBot\nAllow: /\n\nUser-agent: GPTBot\nDisallow: /\n\nSitemap: ' + origin + '/sitemap.xml\n')
await writeFile(path.join(output, 'public', 'THIRD-PARTY-NOTICES.txt'), 'Diagram font notices\n\nNunito: Copyright 2014 The Nunito Project Authors. SIL Open Font License 1.1.\nhttps://github.com/google/fonts/blob/main/ofl/nunito/OFL.txt\n\nComic Shanns: Copyright 2018 Shannon Miwa. MIT License.\nhttps://github.com/shannpersand/comic-shanns/blob/master/LICENSE\n')
await mkdir(path.join(output, 'public', 'licenses'), { recursive: true })
await cp(path.join(site, 'third-party', 'Nunito-OFL.txt'), path.join(output, 'public', 'licenses', 'Nunito-OFL.txt'))
await cp(path.join(site, 'third-party', 'ComicShanns-MIT.txt'), path.join(output, 'public', 'licenses', 'ComicShanns-MIT.txt'))
console.log('Prepared ' + chapterCount + ' public book chapters, ' + (paths.length - chapterCount) + ' supplementary pages, ' + figures.size + ' SVG figures, ' + unresolved.size + ' non-book references stripped.')
if (unresolved.size) console.log([...unresolved].slice(0, 25).join('\n'))
