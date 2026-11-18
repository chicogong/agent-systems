// Pure client-side helpers for assembling a chapter's Socratic AI study pack.
// Zero network calls, zero query/fragment leakage, and zero reader Chrome noise.

export function cleanPageUrl(pathname, origin) {
  const url = new URL(pathname || '/', origin)
  url.search = ''
  url.hash = ''
  return url.href
}

function cleanElementText(element, stripSelectors = '') {
  if (!element) return ''
  if (typeof element.cloneNode === 'function') {
    const clone = element.cloneNode(true)
    const selectors = [
      '.header-anchor',
      '.figure-open',
      '.figure-original',
      'button',
      'script',
      'style',
      ...(stripSelectors ? [stripSelectors] : [])
    ].join(', ')
    clone.querySelectorAll?.(selectors).forEach((node) => node.remove())
    return String(clone.textContent ?? '').replace(/\u200b/g, '').replace(/\s+/g, ' ').trim()
  }
  return String(element.textContent ?? '').replace(/\u200b/g, '').replace(/\s+/g, ' ').trim()
}

function isEditorialFooter(text) {
  return /^在线预览稿[：。]/.test(text) || /^(?:书稿提交：|本地未提交稿，基于\s)/.test(text)
}

export function extractStudyMaterial(docRoot, fallbackTitle = '') {
  const fallback = String(fallbackTitle ?? '').replace(/\s*\|\s*图解 Agent 系统.*$/, '').trim() || '当前章节'
  if (!docRoot) return { title: fallback, content: '' }
  const title = cleanElementText(docRoot.querySelector?.('h1')) || fallback
  const nodes = Array.from(docRoot.querySelectorAll?.('h2, h3, p, li, details.figure-text-alt > summary') ?? [])
  const lines = []
  for (const node of nodes) {
    if (node.closest?.('.reading-position, .reader-actions')) continue
    const tag = String(node.tagName ?? '').toUpperCase()
    if (tag === 'P' && node.closest?.('li')) continue
    const text = cleanElementText(node, tag === 'LI' ? 'ul, ol' : '')
    if (!text || isEditorialFooter(text)) continue
    if (tag === 'SUMMARY') {
      const label = text.replace(/^展开本图无障碍纯文字导读：/, '').trim()
      lines.push(`### 配图文字导读：${label}`)
    } else if (tag === 'H2') {
      lines.push(`## ${text}`)
    } else if (tag === 'H3') {
      lines.push(`### ${text}`)
    } else if (tag === 'LI') {
      lines.push(`- ${text}`)
    } else {
      lines.push(text)
    }
  }
  return { title, content: lines.join('\n\n') }
}

export function buildStudyPack({ title, url, content }) {
  const heading = String(title ?? '').trim() || '当前章节'
  const body = String(content ?? '').trim()
  return [
    `我在读《图解 Agent 系统》的「${heading}」（${url}），请做我的苏格拉底式 AI 陪读搭档，按以下四步带我对练：`,
    '1. 先确认收到的章节材料：用一句话概括本章讨论的核心机制，并问我当前卡在哪一段或图中哪条路径（也可先听我讲第一版理解）。',
    '2. 围绕我的卡点举例解释：不要一次性把结论全倒给我，先给一个贴近实际的具体例子，每次只追问一个关键因果关系，等我作答后再继续。',
    '3. 听我复述并换一个新情况考我：检查我的复述是否漏掉前提或边界；理顺后微调一个条件出题考我，让我先判断系统下一步会发生什么。',
    '4. 给出正文核对位置：每次纠正或补充时，明确指出本材料对应的小节标题或原句位置供我回正文核对；若引入了原文之外的类比，请标明“补充类比”。',
    '',
    '我的当前卡点或第一版理解：（可直接发送开始对练，或在此补充你的具体问题）',
    '',
    '---',
    `【本章阅读材料：${heading}】`,
    `页面地址：${url}`,
    ...(body ? ['', body] : [])
  ].join('\n')
}
