import { cp, mkdir, readFile, rm, writeFile } from 'node:fs/promises'
import { existsSync } from 'node:fs'
import { execFileSync } from 'node:child_process'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const site = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const repo = path.resolve(site, '..')
const output = path.join(site, 'content')
const sourceBase = 'https://github.com/chicogong/agent-systems/blob/main/'
const remoteMain = execFileSync('git', ['rev-parse', 'origin/main'], { cwd: repo, encoding: 'utf8' }).trim()
const checkedFallbacks = new Set()

// This list selects a small reading sample; every chapter body comes from its source file.
const pages = [
  ['README.md', 'index.md'],
  ['docs/concepts/agent-loop.md', 'concepts/agent-loop.md'],
  ['docs/concepts/context-vs-memory.md', 'concepts/context-vs-memory.md'],
  ['docs/concepts/approval-vs-sandbox.md', 'concepts/approval-vs-sandbox.md'],
  ['docs/systems/pi/README.md', 'systems/pi.md'],
  ['docs/systems/codex/README.md', 'systems/codex.md'],
  ['docs/systems/letta/README.md', 'systems/letta.md'],
  ['docs/comparisons/persisted-vs-visible.md', 'comparisons/persisted-vs-visible.md']
]
const routes = new Map(pages)
const assetExtensions = /\.(?:svg|png|jpe?g|webp|excalidraw)$/i

function rewriteTarget(target, source) {
  if (/^(?:[a-z]+:|#|\/\/)/i.test(target)) return target
  const [pathname, suffix = ''] = target.split(/(?=[?#])/)
  const resolved = path.posix.normalize(path.posix.join(path.posix.dirname(source), pathname))
  if (resolved.startsWith('../') || path.posix.isAbsolute(resolved) || !existsSync(path.join(repo, resolved))) {
    throw new Error(`${source}: missing repository target ${target}`)
  }
  if (assetExtensions.test(resolved)) return `/assets/${resolved}${suffix}`
  const selected = routes.get(resolved)
  if (selected) return `/${selected.replace(/(?:index)?\.md$/, '')}${suffix}`
  if (!checkedFallbacks.has(resolved)) {
    // A local-only HEAD may not exist on GitHub. Only send readers to files
    // known to exist on the fetched origin/main tree.
    try { execFileSync('git', ['cat-file', '-e', `origin/main:${resolved}`], { cwd: repo, stdio: 'ignore' }) }
    catch { throw new Error(`${source}: ${resolved} is absent from origin/main (${remoteMain.slice(0, 12)})`) }
    checkedFallbacks.add(resolved)
  }
  return `${sourceBase}${resolved}${suffix}`
}

function transform(markdown, source) {
  // Only Markdown destinations and the one HTML cover image in README need remapping.
  return markdown
    .replace(/(!?\[[^\]]*\]\()([^\s)]+)(\))/g, (_, start, target, end) => `${start}${rewriteTarget(target, source)}${end}`)
    .replace(/(\bsrc=")([^"]+)(")/g, (_, start, target, end) => `${start}${rewriteTarget(target, source)}${end}`)
}

await rm(output, { recursive: true, force: true })
await mkdir(path.join(output, 'public', 'assets'), { recursive: true })
for (const [source, destination] of pages) {
  const input = await readFile(path.join(repo, source), 'utf8')
  const target = path.join(output, destination)
  await mkdir(path.dirname(target), { recursive: true })
  let generated = transform(input, source)
  if (destination === 'index.md') {
    const notice = '> 本地小样只收录 8 页。样本外章节跳转至 GitHub 私有源稿，需要仓库权限；正式公开站须收录完整章节或使用另行确定的规范地址。'
    generated = generated.replace(/^(#[^\n]+\n)/, `$1\n${notice}\n`)
  }
  await writeFile(target, generated)
}
await cp(path.join(repo, 'figures'), path.join(output, 'public', 'assets', 'figures'), {
  recursive: true,
  filter: (src) => src === path.join(repo, 'figures') || !path.extname(src) || assetExtensions.test(src)
})
await mkdir(path.join(output, 'public', 'assets', 'book', 'assets'), { recursive: true })
await cp(path.join(repo, 'book/assets/cover-preview.png'), path.join(output, 'public', 'assets', 'book', 'assets', 'cover-preview.png'))
console.log(`Prepared ${pages.length} pages; checked ${checkedFallbacks.size} sample-external paths on origin/main ${remoteMain.slice(0, 12)}.`)
