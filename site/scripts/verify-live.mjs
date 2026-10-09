import { createHash } from 'node:crypto'
import { readFile, readdir, stat } from 'node:fs/promises'
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

const largeMetadataChecked = []

async function compare(path, file) {
  if (process.env.VERIFY_LARGE_AS_ETAG === '1' && /\.(?:pdf|zip)$/.test(path)) {
    const [local, response] = await Promise.all([readFile(join(dist, file)), head(path)])
    const expectedEtag = `"${createHash('md5').update(local).digest('hex')}"`
    if (response.status !== 200 || response.headers.get('content-length') !== String(local.length) || response.headers.get('etag') !== expectedEtag) {
      throw new Error(`${path}: deployed size or ETag differs from local build`)
    }
    largeMetadataChecked.push(path)
    return
  }
  // Public reading downloads are tens of megabytes; a page-sized deadline
  // aborts a healthy but slow transfer before its digest can be checked.
  const timeoutMs = /\.(?:pdf|zip)$/.test(path) ? 180000 : 20000
  for (let attempt = 1; attempt <= 3; attempt++) {
    try {
      const response = await fetch(new URL(path, site), { signal: AbortSignal.timeout(timeoutMs) })
      if (response.status !== 200) throw new Error(`HTTP ${response.status}`)
      const [local, remote] = await Promise.all([readFile(join(dist, file)), response.arrayBuffer()])
      if (sha256(local) !== sha256(Buffer.from(remote))) throw new Error('deployed bytes differ from local build')
      return
    } catch (error) {
      if (attempt === 3 || /^(?:HTTP|deployed bytes differ)/.test(error.message)) {
        throw new Error(`${path}: ${error.message}${error.cause?.code ? ` (${error.cause.code})` : ''}`)
      }
    }
  }
}

async function head(path) {
  for (let attempt = 1; attempt <= 3; attempt++) {
    try {
      return await fetch(new URL(path, site), { method: 'HEAD', signal: AbortSignal.timeout(20000) })
    } catch (error) {
      if (attempt === 3) throw new Error(`${path}: ${error.message}${error.cause?.code ? ` (${error.cause.code})` : ''}`)
    }
  }
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
  ['/version.json', 'version.json'],
  ['/licenses/Nunito-OFL.txt', 'licenses/Nunito-OFL.txt'],
  ['/licenses/ComicShanns-MIT.txt', 'licenses/ComicShanns-MIT.txt'],
  ['/licenses/Vercel-Analytics-MIT.txt', 'licenses/Vercel-Analytics-MIT.txt'],
  ['/assets/share/book.png', 'assets/share/book.png'],
  ['/assets/share/cover.png', 'assets/share/cover.png'],
]
const pdfPath = 'book/agent-systems-public-preview.pdf'
const hasPdf = await stat(join(dist, pdfPath)).then(() => true, () => false)
if (hasPdf) files.push(['/' + pdfPath, pdfPath])
const readingDownloads = (await readdir(join(dist, 'book')).catch(() => [])).filter((name) => name.endsWith('.zip'))
for (const name of readingDownloads) files.push(['/book/' + name, 'book/' + name])

const failures = []
for (let start = 0; start < files.length; start += 4) {
  await Promise.all(files.slice(start, start + 4).map(async ([path, file]) => {
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
  try {
    const response = await head(path)
    if (response.status !== 404) failures.push(`${path}: expected HTTP 404, got ${response.status}`)
  } catch (error) { failures.push(error.message) }
}
if (hasPdf) {
  try {
    const response = await head('/' + pdfPath)
    if (response.headers.get('x-robots-tag') !== 'noindex') failures.push(`${pdfPath}: missing PDF X-Robots-Tag: noindex`)
  } catch (error) { failures.push(error.message) }
}
for (const name of readingDownloads) {
  try {
    const response = await head('/book/' + name)
    if (response.headers.get('x-robots-tag') !== 'noindex' || !response.headers.get('content-disposition')?.startsWith('attachment;')) failures.push(`${name}: incorrect archive response headers`)
  } catch (error) { failures.push(error.message) }
}

if (failures.length) {
  console.error(failures.join('\n'))
  process.exitCode = 1
} else {
  const comparison = largeMetadataChecked.length
    ? `small files match byte-for-byte; ${largeMetadataChecked.join(', ')} match by content length and Vercel ETag (not full-body download)`
    : 'all files match the local build byte-for-byte'
  console.log(`Live ${site.origin}: ${locations.length} HTML pages, ${figures.length} SVG figures, 2 share images, metadata and license notices${hasPdf ? ', public PDF' : ''}${readingDownloads.length ? ', Markdown ZIP' : ''}; ${comparison}; 4 private paths return 404.`)
}
