// Source headings keep Markdown; navigation and metadata need plain labels.
// This is an inline-label cleaner, not a general Markdown or HTML parser.
export function plainLabel(value) {
  return String(value ?? '')
    .replace(/!\[([^\]]*)\]\([^)]+\)/g, '$1')
    .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
    .replace(/`+([^`]+)`+/g, '$1')
    .replace(/\*\*([^*]+)\*\*/g, '$1')
    .replace(/__([^_]+)__/g, '$1')
    .replace(/~~([^~]+)~~/g, '$1')
    .replace(/<[^>]*>/g, '')
    .replace(/\s+/g, ' ')
    .trim()
}

export function escapeHtml(value) {
  return String(value ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
}

export function chapterTrack(source) {
  if (source.endsWith('/code-walkthrough.md')) {
    return { kind: 'code', label: '源码深潜 · 可选深入', optional: true }
  }
  if (source.startsWith('docs/labs/')) {
    return { kind: 'lab', label: '动手实验 · 可选观察', optional: true }
  }
  if (source.startsWith('docs/comparisons/')) {
    return { kind: 'comparison', label: '横向对照', optional: false }
  }
  return { kind: 'visual', label: '图解主线', optional: false }
}

export function sidebarLabel(source, title) {
  if (source.endsWith('/code-walkthrough.md')) {
    return title.endsWith(' · 源码导读') ? title : `${title} · 源码导读`
  }
  return title
}

export function renderChapterNavigation({ source, bookPaths, bookPosition, bookTitles, route }) {
  const position = bookPosition.get(source)
  if (!position) return ''
  const chapterCount = bookPaths.length
  const { index, group } = position
  const track = chapterTrack(source)
  const previous = bookPaths[index - 1]?.source
  const next = bookPaths[index + 1]?.source
  const link = (target, label, className) => target
    ? `<a class="${className}" href="${route(target)}" aria-label="${label}：${escapeHtml(bookTitles.get(target))}"><span>${label}</span><strong>${escapeHtml(bookTitles.get(target))}</strong></a>`
    : `<span class="${className} is-empty" aria-hidden="true"></span>`
  let skip = ''
  if (!source.endsWith('/code-walkthrough.md') && next && chapterTrack(next).optional) {
    const nextVisual = bookPaths.slice(index + 2).find((item) => !chapterTrack(item.source).optional)?.source
    if (nextVisual) {
      skip = `\n  <div class="reading-position-skip">只想顺着看图解？<a href="${route(nextVisual)}">跳过可选深入，直达：${escapeHtml(bookTitles.get(nextVisual))} →</a></div>`
    }
  }
  return `<nav class="reading-position" aria-label="本书章节导航" data-book-position="${index + 1}/${chapterCount}">
  <div class="reading-position-heading"><span class="reading-position-kicker">图解 Agent 系统 · ${escapeHtml(group.text)}</span><span class="reading-position-meta"><span class="reading-position-badge is-${track.kind}">${track.label}</span><span class="reading-position-number">${String(index + 1).padStart(2, '0')} / ${chapterCount}</span></span></div>
  <div class="reading-position-links">${link(previous, '上一篇', 'reading-position-previous')}<a class="reading-position-contents" href="/#全书目录">全书目录</a>${link(next, '下一篇', 'reading-position-next')}</div>${skip}
</nav>\n\n`
}

export function figureTitle(markdown, fallback = '') {
  const heading = String(markdown ?? '').match(/^#\s+(.+)$/m)?.[1]
  return plainLabel(heading) || fallback
}

export function renderFigureDetails({ slug, title, explanation }) {
  return `<details class="figure-text-alt" id="图的文字说明-${slug}">\n<summary>展开本图无障碍纯文字导读：${escapeHtml(title)}</summary>\n\n${explanation}\n\n</details>\n`
}

// Figure READMEs serve both readers and maintainers. The public text alternative
// must not duplicate the image or append generation/verification instructions.
export function figureExplanation(markdown) {
  let maintenance = false
  return markdown.split(/\n\s*\n/).filter((part) => {
    const text = part.trim()
    if (/^##\s/.test(text)) maintenance = /^##\s+(?:生成与核验|构建与验收范围|构建与校准)/.test(text)
    if (maintenance || text.startsWith('#') || text.startsWith('[')) return false
    if (/^!\[[^\]]*\]\([^)]+\)\s*$/.test(text)) return false
    return !text.startsWith('可在此目录') && !text.startsWith('状态：') && !text.startsWith('`build.py`')
  }).join('\n\n').trim()
}
