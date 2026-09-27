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

// Figure READMEs serve both readers and maintainers. The public text alternative
// must not duplicate the image or append generation/verification instructions.
export function figureExplanation(markdown) {
  let maintenance = false
  return markdown.split(/\n\s*\n/).filter((part) => {
    const text = part.trim()
    if (/^##\s/.test(text)) maintenance = /^##\s+(?:生成与核验|构建与验收范围)/.test(text)
    if (maintenance || text.startsWith('#') || text.startsWith('[')) return false
    if (/^!\[[^\]]*\]\([^)]+\)\s*$/.test(text)) return false
    return !text.startsWith('可在此目录') && !text.startsWith('状态：') && !text.startsWith('`build.py`')
  }).join('\n\n').trim()
}
