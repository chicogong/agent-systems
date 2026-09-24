import { readFile, readdir, stat, writeFile } from 'node:fs/promises'
import { createHash } from 'node:crypto'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const site = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const dist = path.join(site, '.vitepress', 'dist')
const origin = process.env.SITE_URL
const pdfPublished = Boolean(process.env.PUBLIC_PDF_FILE)
const pdfPath = 'book/agent-systems-public-preview.pdf'
if (!origin) throw new Error('SITE_URL is required')

if (process.env.DEPLOY_TARGET === 'vercel') {
  const config = { cleanUrls: true }
  if (pdfPublished) config.headers = [{ source: '/' + pdfPath, headers: [
    { key: 'X-Robots-Tag', value: 'noindex' },
    { key: 'Content-Disposition', value: 'inline; filename="agent-systems-public-preview.pdf"' }
  ] }]
  await writeFile(path.join(dist, 'vercel.json'), JSON.stringify(config, null, 2) + '\n')
}
const sidebar = JSON.parse(await readFile(path.join(site, '.vitepress', 'generated-sidebar.json'), 'utf8'))
const expected = ['index.html', 'feedback.html', ...(pdfPublished ? ['pdf.html'] : []), ...sidebar.flatMap((part) => part.items.map((item) => item.link.slice(1) + '.html'))]
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
if (allFiles.some((file) => /\.(?:excalidraw|png)$/i.test(file) || (file.endsWith('.pdf') && !(pdfPublished && file === path.join(dist, pdfPath))))) throw new Error('Unexpected source, PDF, or PNG file in public output')
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
const anchors = new Map([...pages].map(([file, html]) => [file, new Set([...html.matchAll(/\sid="([^"]+)"/g)].map((match) => match[1]))]))
const indexPages = new Set(['feedback.html', 'pdf.html', 'concepts.html', 'systems.html', 'comparisons.html', 'sources.html'])
for (const file of expected) {
  const html = pages.get(file)
  if (html.includes('name="robots" content="noindex')) throw new Error(`${file}: unexpected noindex meta`)
  const pathname = file === 'index.html' ? '/' : `/${file.slice(0, -5)}`
  if (!html.includes(`rel="canonical" href="${origin}${pathname}"`)) throw new Error(`Missing canonical: ${file}`)
  for (const marker of ['property="og:title"', 'property="og:description"', `property="og:url" content="${origin}${pathname}"`, 'name="twitter:card"', 'type="application/ld+json"']) {
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
  if (file !== 'index.html' && file !== 'feedback.html' && file !== 'pdf.html' && !html.includes('mailto:ghr7719@gmail.com')) throw new Error(`${file}: missing chapter feedback link`)
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
