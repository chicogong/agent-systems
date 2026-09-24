import { createHash } from 'node:crypto'
import { readFile, readdir } from 'node:fs/promises'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

const dist = join(dirname(fileURLToPath(import.meta.url)), '..', '.vitepress', 'dist')
const site = new URL(process.env.LIVE_URL || 'https://books.aimake.cc')
const canonical = new URL(process.env.SITE_URL || site.origin)
if (!['https:', 'http:'].includes(site.protocol) || !['https:', 'http:'].includes(canonical.protocol)) {
  throw new Error('LIVE_URL and SITE_URL must be HTTP(S) URLs')
}

function sha256(bytes) {
  return createHash('sha256').update(bytes).digest('hex')
}

async function compare(path, file) {
  const response = await fetch(new URL(path, site), { signal: AbortSignal.timeout(15000) })
  if (response.status !== 200) throw new Error(`${path}: HTTP ${response.status}`)
  const [local, remote] = await Promise.all([readFile(join(dist, file)), response.arrayBuffer()])
  if (sha256(local) !== sha256(Buffer.from(remote))) throw new Error(`${path}: deployed bytes differ from local build`)
}

const localSitemap = await readFile(join(dist, 'sitemap.xml'), 'utf8')
const locations = [...localSitemap.matchAll(/<loc>([^<]+)<\/loc>/g)].map((match) => new URL(match[1]))
if (!locations.length || new Set(locations.map((location) => location.pathname)).size !== locations.length) {
  throw new Error('Local sitemap has no pages or contains duplicate paths')
}
for (const location of locations) {
  if (location.origin !== canonical.origin) throw new Error(`Unexpected sitemap origin: ${location.href}`)
}

const figureRoot = join(dist, 'assets', 'figures')
const figures = (await readdir(figureRoot, { withFileTypes: true }))
  .filter((entry) => entry.isDirectory())
  .map((entry) => `assets/figures/${entry.name}/diagram.svg`)
const files = [
  ...locations.map((location) => [location.pathname, location.pathname === '/' ? 'index.html' : `${location.pathname.slice(1)}.html`]),
  ...figures.map((file) => [`/${file}`, file]),
  ['/sitemap.xml', 'sitemap.xml'],
  ['/robots.txt', 'robots.txt'],
  ['/THIRD-PARTY-NOTICES.txt', 'THIRD-PARTY-NOTICES.txt'],
]

const failures = []
for (let start = 0; start < files.length; start += 8) {
  await Promise.all(files.slice(start, start + 8).map(async ([path, file]) => {
    try { await compare(path, file) } catch (error) { failures.push(error.message) }
  }))
}

const privatePaths = [
  '/AGENTS.md',
  '/book/manifest.txt',
  '/output/pdf/agent-systems-preview.pdf',
  '/assets/figures/permission-and-recovery/scene.excalidraw',
]
for (const path of privatePaths) {
  const response = await fetch(new URL(path, site), { method: 'HEAD', signal: AbortSignal.timeout(15000) })
  if (response.status !== 404) failures.push(`${path}: expected HTTP 404, got ${response.status}`)
}

if (failures.length) {
  console.error(failures.join('\n'))
  process.exitCode = 1
} else {
  console.log(`Live ${site.origin}: ${locations.length} HTML pages, ${figures.length} SVG figures and 3 metadata files match the local build byte-for-byte; 4 private paths return 404.`)
}
