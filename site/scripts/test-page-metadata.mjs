import test from 'node:test'
import assert from 'node:assert/strict'
import {
  plainLabel,
  chapterTrack,
  sidebarLabel,
  renderChapterNavigation,
  figureTitle,
  renderFigureDetails,
  figureExplanation
} from './page-metadata.mjs'

test('headings are plain labels without changing identifier punctuation', () => {
  assert.equal(plainLabel('`ctx.sessions` 与 **会话记忆**'), 'ctx.sessions 与 会话记忆')
  assert.equal(plainLabel('从 `tool_call` 到 `tool_result`'), '从 tool_call 到 tool_result')
})
test('links and inline HTML retain visible text', () => {
  assert.equal(plainLabel('[Hermes](https://example.org) 与 <span>Browser Use</span>'), 'Hermes 与 Browser Use')
})
test('missing titles and whitespace are normalized', () => {
  assert.equal(plainLabel(undefined), '')
  assert.equal(plainLabel('  沙箱\n   与权限  '), '沙箱 与权限')
})
test('figure alternatives keep teaching text but omit duplicate images and maintenance', () => {
  const markdown = '# 图名\n\n[SVG](diagram.svg)\n\n![预览](diagram.svg)\n\n## 文字版\n\n箭头表示读回，不等于完成。\n\n`build.py` 生成图源。\n\n## 生成与核验\n\n维护者运行导出器。\n\n## 适用边界\n\n不是运行录像。'
  assert.equal(figureExplanation(markdown), '箭头表示读回，不等于完成。\n\n不是运行录像。')
  assert.equal(figureExplanation(markdown.replace('生成与核验', '构建与校准')),
               '箭头表示读回，不等于完成。\n\n不是运行录像。')
})

test('chapterTrack classifies visual mainline, code walkthroughs, labs, and comparisons', () => {
  assert.deepEqual(chapterTrack('docs/concepts/agent-loop.md'), {
    kind: 'visual', label: '图解主线', optional: false
  })
  assert.deepEqual(chapterTrack('docs/systems/pi/README.md'), {
    kind: 'visual', label: '图解主线', optional: false
  })
  assert.deepEqual(chapterTrack('docs/systems/pi/code-walkthrough.md'), {
    kind: 'code', label: '源码深潜 · 可选深入', optional: true
  })
  assert.deepEqual(chapterTrack('docs/labs/first-agent-loop.md'), {
    kind: 'lab', label: '动手实验 · 可选观察', optional: true
  })
  assert.deepEqual(chapterTrack('docs/comparisons/loop-and-stop.md'), {
    kind: 'comparison', label: '横向对照', optional: false
  })
})

test('sidebarLabel marks code-walkthrough chapters clearly without duplicating suffix', () => {
  assert.equal(sidebarLabel('docs/systems/pi/code-walkthrough.md', '跟着 Pi 代码走一轮'), '跟着 Pi 代码走一轮 · 源码导读')
  assert.equal(sidebarLabel('docs/systems/pi/code-walkthrough.md', '跟着 Pi 代码走一轮 · 源码导读'), '跟着 Pi 代码走一轮 · 源码导读')
  assert.equal(sidebarLabel('docs/systems/pi/README.md', 'Pi 架构总览'), 'Pi 架构总览')
})

test('renderChapterNavigation preserves adjacent links and offers skip link over optional tracks', () => {
  const group = { text: '第二部分 · 行动、工具与执行' }
  const bookPaths = [
    { source: 'docs/systems/pi/README.md', group },
    { source: 'docs/systems/pi/code-walkthrough.md', group },
    { source: 'docs/comparisons/permission-and-recovery.md', group },
    { source: 'docs/labs/remote-effect.md', group },
    { source: 'docs/labs/http-receipt.md', group },
    { source: 'docs/comparisons/completion-and-evidence.md', group }
  ]
  const bookPosition = new Map(bookPaths.map((item, index) => [item.source, { index, group: item.group }]))
  const bookTitles = new Map([
    ['docs/systems/pi/README.md', 'Pi：极简运行核心与会话外壳'],
    ['docs/systems/pi/code-walkthrough.md', '跟着 Pi 代码走一轮'],
    ['docs/comparisons/permission-and-recovery.md', '超时与恢复对照'],
    ['docs/labs/remote-effect.md', '实验：回执丢失'],
    ['docs/labs/http-receipt.md', '实验：HTTP 回执'],
    ['docs/comparisons/completion-and-evidence.md', '完成与证据对账']
  ])
  const route = (s) => '/' + s.replace(/^docs\//, '').replace(/\/README\.md$/, '').replace(/\.md$/, '')

  // Visual chapter before code-walkthrough: keeps adjacent link AND adds skip link
  const piNav = renderChapterNavigation({
    source: 'docs/systems/pi/README.md',
    bookPaths, bookPosition, bookTitles, route
  })
  assert.match(piNav, /data-book-position="1\/6"/)
  assert.match(piNav, /aria-label="本书章节导航"/)
  assert.match(piNav, /href="\/#全书目录"/)
  assert.match(piNav, /href="\/systems\/pi\/code-walkthrough"/)
  assert.match(piNav, /<span class="reading-position-badge is-visual">图解主线<\/span>/)
  assert.match(piNav, /<div class="reading-position-skip">只想顺着看图解？<a href="\/comparisons\/permission-and-recovery">跳过可选深入，直达：超时与恢复对照 →<\/a><\/div>/)

  // Code-walkthrough itself: shows code badge, keeps prev/next, no skip bar
  const codeNav = renderChapterNavigation({
    source: 'docs/systems/pi/code-walkthrough.md',
    bookPaths, bookPosition, bookTitles, route
  })
  assert.match(codeNav, /<span class="reading-position-badge is-code">源码深潜 · 可选深入<\/span>/)
  assert.match(codeNav, /href="\/systems\/pi"/)
  assert.match(codeNav, /href="\/comparisons\/permission-and-recovery"/)
  assert.doesNotMatch(codeNav, /reading-position-skip/)

  // Chapter before two consecutive labs: skips both labs to the next main chapter
  const compNav = renderChapterNavigation({
    source: 'docs/comparisons/permission-and-recovery.md',
    bookPaths, bookPosition, bookTitles, route
  })
  assert.match(compNav, /<span class="reading-position-badge is-comparison">横向对照<\/span>/)
  assert.match(compNav, /href="\/labs\/remote-effect"/)
  assert.match(compNav, /<div class="reading-position-skip">只想顺着看图解？<a href="\/comparisons\/completion-and-evidence">跳过可选深入，直达：完成与证据对账 →<\/a><\/div>/)
})

test('figureTitle and renderFigureDetails preserve verify-public anchor IDs and Markdown blank lines', () => {
  const readme = '# Agent 从任务到结果：`概念`总览\n\n第一段文字说明。'
  const title = figureTitle(readme, 'agent-loop')
  assert.equal(title, 'Agent 从任务到结果：概念总览')
  const details = renderFigureDetails({
    slug: 'agent-loop',
    title,
    explanation: '第一段 [阅读路线](/learning-path)。\n\n第二段说明。'
  })
  // Must match verify-public.mjs /\sid="([^"]+)"/g check
  const ids = [...details.matchAll(/\sid="([^"]+)"/g)].map((m) => m[1])
  assert.deepEqual(ids, ['图的文字说明-agent-loop'])
  assert.match(details, /^<details class="figure-text-alt" id="图的文字说明-agent-loop">\n<summary>展开本图无障碍纯文字导读：Agent 从任务到结果：概念总览<\/summary>\n\n第一段 \[阅读路线\]\(\/learning-path\)。\n\n第二段说明。\n\n<\/details>\n$/)
})
