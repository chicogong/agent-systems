import { readFile, readdir, stat, writeFile } from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const site = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const dist = path.join(site, '.vitepress', 'dist')
const origin = process.env.SITE_URL
if (!origin) throw new Error('SITE_URL is required')

if (process.env.DEPLOY_TARGET === 'vercel') {
  await writeFile(path.join(dist, 'vercel.json'), JSON.stringify({ cleanUrls: true }, null, 2) + '\n')
}
const sidebar = JSON.parse(await readFile(path.join(site, '.vitepress', 'generated-sidebar.json'), 'utf8'))
const expected = ['index.html', ...sidebar.flatMap((part) => part.items.map((item) => item.link.slice(1) + '.html'))]
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
if (allFiles.some((file) => /\.(?:excalidraw|pdf|png)$/i.test(file))) throw new Error('Unexpected source, PDF, or PNG file in public output')
const text = (await Promise.all(allFiles.filter((file) => /\.(?:html|js|css|json|xml|txt)$/.test(file)).map((file) => readFile(file, 'utf8')))).join('\n')
for (const forbidden of ['github.com/chicogong/agent-systems', 'href="/assets/figures/scene.excalidraw"', 'noindex', '下载可编辑图源']) {
  if (text.includes(forbidden)) throw new Error(`Public output contains forbidden marker: ${forbidden}`)
}

for (const file of expected) {
  const html = await readFile(path.join(dist, file), 'utf8')
  const pathname = file === 'index.html' ? '/' : `/${file.slice(0, -5)}`
  if (!html.includes(`rel="canonical" href="${origin}${pathname}"`)) throw new Error(`Missing canonical: ${file}`)
  if (file !== 'index.html' && !html.includes('在线预览稿')) throw new Error(`Missing editorial status: ${file}`)
  for (const [, href] of html.matchAll(/href="([^"]+)"/g)) {
    if (href.includes('github.com/chicogong/agent-systems') || href.endsWith('.excalidraw')) throw new Error(`${file}: private or editable source link ${href}`)
    if (!href.startsWith('/')) continue
    const route = decodeURI(href.split(/[?#]/)[0])
    const candidate = route === '/' ? 'index.html' : route.match(/\.[a-z0-9]+$/i) ? route.slice(1) : `${route.slice(1)}.html`
    try { await stat(path.join(dist, candidate)) }
    catch { throw new Error(`${file}: broken local link ${href}`) }
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
