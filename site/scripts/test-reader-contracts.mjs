import test from 'node:test'
import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const scriptsDir = path.dirname(fileURLToPath(import.meta.url))
const siteDir = path.resolve(scriptsDir, '..')

test('trial page whitelist stays synchronized across prepare-public, verify-public, and config.mjs', async () => {
  const [prepareSrc, verifySrc, configSrc] = await Promise.all([
    readFile(path.join(scriptsDir, 'prepare-public.mjs'), 'utf8'),
    readFile(path.join(scriptsDir, 'verify-public.mjs'), 'utf8'),
    readFile(path.join(siteDir, '.vitepress/config.mjs'), 'utf8')
  ])

  assert.match(prepareSrc, /routes\.set\('docs\/reader-trial\.md',\s*'\/trial'\)/)
  assert.match(prepareSrc, /path\.join\(output,\s*'trial\.md'\)/)
  assert.doesNotMatch(prepareSrc, /github\.com\/chicogong\/agent-systems\/blob\/main\/docs\/reader-trial\.md/)

  assert.match(verifySrc, /expected\s*=\s*\[[^\]]*'trial\.html'/)
  const verifyIndexSet = verifySrc.match(/indexPages\s*=\s*new Set\(\[([^\]]+)\]\)/)?.[1] ?? ''
  const configNonArticleSet = configSrc.match(/new Set\(\[([^\]]+)\]\)\.has\(pathname\)/)?.[1] ?? ''
  const parseItems = (raw) => raw.split(',').map((s) => s.trim().replace(/^'|'$/g, '').replace(/\.html$/, '')).filter(Boolean).sort()
  assert.deepEqual(parseItems(verifyIndexSet), parseItems(configNonArticleSet))
  assert.ok(parseItems(verifyIndexSet).includes('trial'))
})

test('reader theme components preserve Playwright smoke-check selectors and public asset guards', async () => {
  const [actionsVue, themeIndex, themeCss] = await Promise.all([
    readFile(path.join(siteDir, '.vitepress/theme/ReaderActions.vue'), 'utf8'),
    readFile(path.join(siteDir, '.vitepress/theme/index.js'), 'utf8'),
    readFile(path.join(siteDir, '.vitepress/theme/style.css'), 'utf8')
  ])

  // check_reader.py selectors on ReaderActions.vue
  assert.match(actionsVue, />分享这一页<\/button>/)
  assert.match(actionsVue, />复制本章 AI 陪读包<\/button>/)
  assert.match(actionsVue, /href="\/feedback"/)
  assert.equal([...actionsVue.matchAll(/role="status"/g)].length, 1)
  assert.match(actionsVue, /已复制本章 AI 陪读材料包，可直接粘贴到常用 AI 助手/)

  // check_reader.py selectors and figure viewer controls on index.js
  assert.match(themeIndex, /aria-label',\s*'图稿细读'/)
  assert.match(themeIndex, /aria-label="关闭大图"/)
  assert.match(themeIndex, /放大图稿：\$\{img\.alt\}/)
  assert.match(themeIndex, /放大细读/)
  assert.match(themeIndex, /适应窗口/)
  assert.match(themeIndex, /details\.figure-text-alt/)
  assert.match(themeIndex, /const publicMode = import\.meta\.env\.VITE_PUBLIC_SITE === '1'/)

  // Warm Paper & Blueprint Ink palette and mobile horizontal zoom in style.css
  for (const token of ['#FAF8F4', '#F2EFE9', '#182631', '#145874', '#C0563B']) {
    assert.ok(themeCss.includes(token), `Missing design token ${token}`)
  }
  assert.match(themeCss, /cursor:\s*zoom-in/)
  assert.match(themeCss, /\.figure-viewer\.is-zoomed/)
  assert.match(themeCss, /max\(100%,\s*980px\)/)
  assert.match(themeCss, /max-width:\s*none/)
})
