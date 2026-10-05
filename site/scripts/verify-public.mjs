import { readFile, readdir, stat, writeFile } from 'node:fs/promises'
import { createHash } from 'node:crypto'
import { execFileSync } from 'node:child_process'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const site = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const dist = path.join(site, '.vitepress', 'dist')
const origin = process.env.SITE_URL
const pdfPublished = Boolean(process.env.PUBLIC_PDF_FILE)
const markdownPublished = Boolean(process.env.PUBLIC_MARKDOWN_FILE)
const pdfPath = 'book/agent-systems-public-preview.pdf'
if (!origin) throw new Error('SITE_URL is required')
const version = JSON.parse(await readFile(path.join(dist, 'version.json'), 'utf8'))
const currentCommit = execFileSync('git', ['rev-parse', 'HEAD'], { cwd: path.join(site, '..'), encoding: 'utf8' }).trim()
const currentClean = !execFileSync('git', ['status', '--porcelain', '--untracked-files=normal'], { cwd: path.join(site, '..'), encoding: 'utf8' }).trim()
if (version.status !== 'preview' || version.sourceCommit !== currentCommit || version.sourceClean !== currentClean) {
  throw new Error('Public version metadata does not match this source checkout')
}
if (process.env.SITE_RELEASE === '1' && !version.sourceClean) throw new Error('Release candidate contains uncommitted source changes')
if (version.pdfSha256 !== (pdfPublished ? process.env.PUBLIC_PDF_SHA256 : null)) throw new Error('Public PDF version metadata mismatch')
if (version.markdownSha256 !== (markdownPublished ? process.env.PUBLIC_MARKDOWN_SHA256 : null)) throw new Error('Public Markdown version metadata mismatch')
if (version.pdfSourceCommit !== (pdfPublished ? process.env.PUBLIC_PDF_COMMIT || currentCommit : null)) throw new Error('PDF source commit mismatch')
if (version.markdownSourceCommit !== (markdownPublished ? process.env.PUBLIC_MARKDOWN_COMMIT || currentCommit : null)) throw new Error('Markdown source commit mismatch')
if (version.analytics !== (process.env.VITE_READER_ANALYTICS === '1' ? 'vercel-aggregate-pageviews' : 'disabled')) throw new Error('Analytics disclosure does not match this build')
const markdownPath = markdownPublished ? `book/agent-systems-md-${version.markdownSourceCommit.slice(0, 12)}.zip` : null

if (process.env.DEPLOY_TARGET === 'vercel') {
  const config = { cleanUrls: true }
  if (pdfPublished) config.headers = [{ source: '/' + pdfPath, headers: [
    { key: 'X-Robots-Tag', value: 'noindex' },
    { key: 'Content-Disposition', value: 'inline; filename="agent-systems-public-preview.pdf"' }
  ] }]
  if (markdownPublished) {
    config.headers ??= []
    config.headers.push({ source: '/' + markdownPath, headers: [
      { key: 'X-Robots-Tag', value: 'noindex' },
      { key: 'Content-Disposition', value: 'attachment; filename="' + path.basename(markdownPath) + '"' }
    ] })
  }
  await writeFile(path.join(dist, 'vercel.json'), JSON.stringify(config, null, 2) + '\n')
}
const sidebar = JSON.parse(await readFile(path.join(site, '.vitepress', 'generated-sidebar.json'), 'utf8'))
const expected = ['index.html', 'feedback.html', 'downloads.html', ...(pdfPublished ? ['pdf.html'] : []), ...sidebar.flatMap((part) => part.items.map((item) => item.link.slice(1) + '.html'))]
const chapterCount = (await readFile(path.join(site, '..', 'book', 'manifest.txt'), 'utf8')).split(/\r?\n/).filter((line) => line.trim() && !line.trim().startsWith('#') && !line.trim().startsWith('@part ')).length
const bookItems = sidebar.flatMap((part) => part.items).slice(0, chapterCount)
if (bookItems.length !== chapterCount) throw new Error('Sidebar has fewer book chapters than the manifest')
if (expected.length < 51) throw new Error('Full public reader has too few chapters: ' + expected.length)
const found = []
async function walk(directory) {
  for (const entry of await readdir(directory, { withFileTypes: true })) {
    const location = path.join(directory, entry.name)
    if (entry.isDirectory()) await walk(location)
    else if (entry.name.endsWith('.html') && entry.name !== '404.html') found.push(path.relative(dist, location).replaceAll(path.sep, '/'))
  }
}
await walk(dist)
if (found.sort().join('|') !== expected.sort().join('|')) throw new Error(`Public HTML whitelist mismatch: ${found}`)

const allFiles = []
async function collect(directory) {
  for (const entry of await readdir(directory, { withFileTypes: true })) {
    const location = path.join(directory, entry.name)
    if (entry.isDirectory()) await collect(location)
    else allFiles.push(location)
  }
}
await collect(dist)
const allowedPng = new Set(['assets/share/book.png', 'assets/share/cover.png'].map((file) => path.join(dist, file)))
if (allFiles.some((file) => file.endsWith('.excalidraw') ||
  (file.endsWith('.png') && !allowedPng.has(file)) ||
  (file.endsWith('.zip') && file !== (markdownPath && path.join(dist, markdownPath))) ||
  (file.endsWith('.pdf') && !(pdfPublished && file === path.join(dist, pdfPath))))) throw new Error('Unexpected source or download file in public output')
for (const [target, source] of [['assets/share/book.png', 'assets/book-share.png'], ['assets/share/cover.png', '../book/assets/cover-preview.png']]) {
  const [published, original] = await Promise.all([readFile(path.join(dist, target)), readFile(path.join(site, source))])
  if (!published.equals(original)) throw new Error(`Share artwork differs from approved source: ${target}`)
}
if (markdownPublished) {
  const digest = createHash('sha256').update(await readFile(path.join(dist, markdownPath))).digest('hex')
  if (digest !== version.markdownSha256) throw new Error('Reading archive digest changed during site build')
}
if (pdfPublished) {
  const bytes = await readFile(path.join(dist, pdfPath))
  const digest = createHash('sha256').update(bytes).digest('hex')
  if (digest !== process.env.PUBLIC_PDF_SHA256) throw new Error('Public PDF digest changed during site build')
  if (process.env.DEPLOY_TARGET === 'vercel') {
    const config = JSON.parse(await readFile(path.join(dist, 'vercel.json'), 'utf8'))
    if (!config.headers?.some((entry) => entry.source === '/' + pdfPath && entry.headers.some((header) => header.key === 'X-Robots-Tag' && header.value === 'noindex'))) throw new Error('PDF noindex response header missing')
  }
}
const text = (await Promise.all(allFiles.filter((file) => /\.(?:html|js|css|json|xml|txt)$/.test(file)).map((file) => readFile(file, 'utf8')))).join('\n')
for (const forbidden of ['href="/assets/figures/scene.excalidraw"', '下载可编辑图源']) {
  if (text.includes(forbidden)) throw new Error(`Public output contains forbidden marker: ${forbidden}`)
}

const pages = new Map(await Promise.all(expected.map(async (file) => [file, await readFile(path.join(dist, file), 'utf8')])))
if (!pages.get('index.html').includes('id="全书目录"')) throw new Error('Home page has no book-order contents anchor')
for (const [index, item] of bookItems.entries()) {
  const file = item.link.slice(1) + '.html'
  const html = pages.get(file)
  if (!html.includes(`data-book-position="${index + 1}/${chapterCount}"`)) throw new Error(`${file}: missing book-position navigation`)
  if (!html.includes('aria-label="本书章节导航"') || !html.includes('href="/#全书目录"')) throw new Error(`${file}: inaccessible or missing table-of-contents navigation`)
  for (const adjacent of [bookItems[index - 1], bookItems[index + 1]].filter(Boolean)) {
    if (!html.includes(`href="${adjacent.link}"`)) throw new Error(`${file}: missing adjacent chapter ${adjacent.link}`)
  }
}
const anchors = new Map([...pages].map(([file, html]) => [file, new Set([...html.matchAll(/\sid="([^"]+)"/g)].map((match) => match[1]))]))
const indexPages = new Set(['feedback.html', 'pdf.html', 'downloads.html', 'concepts.html', 'systems.html', 'comparisons.html', 'sources.html'])
for (const file of expected) {
  const html = pages.get(file)
  if (!html.includes(version.sourceCommit.slice(0, 12))) throw new Error(`${file}: missing reader-visible source revision`)
  for (const [image] of html.matchAll(/<img\b[^>]*>/g)) {
    if (!/src="\/assets\/figures\/[^/]+\/diagram\.svg"/.test(image)) continue
    for (const attribute of ['width', 'height']) {
      const value = Number(image.match(new RegExp(`\\b${attribute}="([^"]+)"`))?.[1])
      if (!(value > 0 && Number.isFinite(value))) throw new Error(`${file}: figure has no valid ${attribute}`)
    }
    if (!/\balt="[^"]+"/.test(image)) throw new Error(`${file}: figure has no text alternative`)
  }
  // Chinese punctuation next to an emphasis delimiter can make Markdown
  // render literal **. Inspect rendered prose, not code examples or scripts.
  const withoutCode = html.replace(/<pre\b[^>]*>[\s\S]*?<\/pre>/g, '').replace(/<code\b[^>]*>[\s\S]*?<\/code>/g, '')
  for (const [, , block] of withoutCode.matchAll(/<(p|li|h[1-6]|td|th)\b[^>]*>([\s\S]*?)<\/\1>/g)) {
    const prose = block.replace(/<[^>]*>/g, '')
    if (prose.includes('**')) throw new Error(`${file}: literal Markdown emphasis in rendered prose: ${prose.slice(0, 100)}`)
  }
  if (html.includes('name="robots" content="noindex')) throw new Error(`${file}: unexpected noindex meta`)
  const pathname = file === 'index.html' ? '/' : `/${file.slice(0, -5)}`
  if (!html.includes(`rel="canonical" href="${origin}${pathname}"`)) throw new Error(`Missing canonical: ${file}`)
  for (const marker of ['property="og:title"', 'property="og:description"', `property="og:url" content="${origin}${pathname}"`, `property="og:image" content="${origin}/assets/share/book.png"`, 'name="twitter:card" content="summary_large_image"', 'type="application/ld+json"']) {
    if (!html.includes(marker)) throw new Error(`${file}: missing social or structured metadata: ${marker}`)
  }
  const structuredData = html.match(/<script type="application\/ld\+json">([^<]+)<\/script>/)?.[1]
  if (!structuredData) throw new Error(`${file}: missing JSON-LD payload`)
  const schema = JSON.parse(structuredData)
  const expectedType = file === 'index.html' ? 'WebSite' : indexPages.has(file) ? 'WebPage' : 'Article'
  if (schema['@type'] !== expectedType || schema.url !== `${origin}${pathname}` || schema.inLanguage !== 'zh-CN') {
    throw new Error(`${file}: structured data does not match the canonical page`)
  }
  if (file !== 'index.html' && file !== 'feedback.html' && !html.includes('在线预览稿')) throw new Error(`Missing editorial status: ${file}`)
  if (file !== 'index.html' && file !== 'feedback.html' && file !== 'pdf.html' && file !== 'downloads.html' && !html.includes('mailto:ghr7719@gmail.com')) throw new Error(`${file}: missing chapter feedback link`)
  if (/图源\s*·\s*PNG 预览|可编辑图源\s*·\s*PNG 预览/.test(html)) throw new Error(`${file}: inert private figure labels leaked into public prose`)
  for (const [, href] of html.matchAll(/href="([^"]+)"/g)) {
    if (href.endsWith('.excalidraw')) throw new Error(`${file}: editable source artifact leaked into site ${href}`)
    if (!href.startsWith('/') && !href.startsWith('#')) continue
    const [rawRoute, fragment] = href.split('#')
    const route = rawRoute ? decodeURI(rawRoute.split('?')[0]) : pathname
    const candidate = route === '/' ? 'index.html' : route.match(/\.[a-z0-9]+$/i) ? route.slice(1) : `${route.slice(1)}.html`
    try { await stat(path.join(dist, candidate)) }
    catch { throw new Error(`${file}: broken local link ${href}`) }
    if (fragment && anchors.has(candidate) && !anchors.get(candidate).has(decodeURIComponent(fragment))) {
      throw new Error(`${file}: broken local heading ${href}`)
    }
  }
}
const sitemap = await readFile(path.join(dist, 'sitemap.xml'), 'utf8')
for (const file of expected) {
  const pathname = file === 'index.html' ? '/' : `/${file.slice(0, -5)}`
  if (!sitemap.includes(`${origin}${pathname}`)) throw new Error(`Sitemap missing ${pathname}`)
}
const robots = await readFile(path.join(dist, 'robots.txt'), 'utf8')
if (!robots.includes(`Sitemap: ${origin}/sitemap.xml`)) throw new Error('robots.txt sitemap does not match canonical origin')
if (!robots.includes('User-agent: GPTBot\nDisallow: /')) throw new Error('Expected training crawler rule is missing')
console.log(`Verified ${expected.length} public pages, local links, sitemap, canonical, robots, and artifact whitelist for ${origin}.`)
