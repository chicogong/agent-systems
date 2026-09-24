import { defineConfig } from 'vitepress'
import { readFileSync } from 'node:fs'

const publicMode = process.env.SITE_MODE === 'public'
const pdfPublished = publicMode && Boolean(process.env.PUBLIC_PDF_FILE)
const siteUrl = process.env.SITE_URL
const publicSidebar = publicMode ? JSON.parse(readFileSync(new URL('./generated-sidebar.json', import.meta.url), 'utf8')) : []
if (publicMode && (!siteUrl || !/^https:\/\/[^/]+$/.test(siteUrl))) {
  throw new Error('Public builds require SITE_URL as an HTTPS origin without a path')
}

function tokens(text) {
  const words = text.toLocaleLowerCase().match(/[\p{Script=Han}]+|[\p{L}\p{N}_-]+/gu) ?? []
  return words.flatMap((word) => {
    if (!/\p{Script=Han}/u.test(word)) return [word]
    const chars = [...word]
    return [...chars, ...chars.slice(0, -1).map((char, index) => char + chars[index + 1]), word]
  })
}

export default defineConfig({
  srcDir: 'content',
  lang: 'zh-CN',
  title: '图解 Agent 系统',
  description: publicMode ? '《图解 Agent 系统》在线预览：从运行机制、源码导读到横向对照。' : '沿问题、图与固定版本案例阅读 Agent 系统',
  cleanUrls: true,
  sitemap: publicMode ? { hostname: siteUrl } : undefined,
  transformPageData(pageData) {
    if (!publicMode) return
    const pathname = pageData.relativePath.replace(/index\.md$/, '').replace(/\.md$/, '')
    const canonical = `${siteUrl}/${pathname}`
    const isHome = pathname === ''
    const isArticle = !isHome && !new Set(['feedback', 'pdf', 'concepts', 'systems', 'comparisons', 'sources']).has(pathname)
    const title = pageData.title || '图解 Agent 系统'
    const description = pageData.frontmatter.description || '从运行机制、源码导读到横向对照，图解 Agent 系统。'
    pageData.frontmatter.head ??= []
    pageData.frontmatter.head.push(
      ['link', { rel: 'canonical', href: canonical }],
      ['meta', { property: 'og:site_name', content: '图解 Agent 系统' }],
      ['meta', { property: 'og:locale', content: 'zh_CN' }],
      ['meta', { property: 'og:type', content: isArticle ? 'article' : 'website' }],
      ['meta', { property: 'og:title', content: title }],
      ['meta', { property: 'og:description', content: description }],
      ['meta', { property: 'og:url', content: canonical }],
      ['meta', { name: 'twitter:card', content: 'summary' }]
    )
    const identity = { '@type': 'Person', name: 'chicogong', url: `${siteUrl}/back/about-author` }
    const book = { '@type': 'WebSite', '@id': `${siteUrl}/#website`, name: '图解 Agent 系统', url: `${siteUrl}/`, inLanguage: 'zh-CN' }
    const schema = isHome ? book : {
      '@type': isArticle ? 'Article' : 'WebPage',
      headline: title,
      description,
      url: canonical,
      inLanguage: 'zh-CN',
      isPartOf: { '@id': book['@id'] },
      ...(isArticle ? { author: identity } : {})
    }
    pageData.frontmatter.head.push(['script', { type: 'application/ld+json' }, JSON.stringify({ '@context': 'https://schema.org', ...schema }).replace(/</g, '\\u003c')])
  },
  // VitePress treats this source extension as a page, although it is copied to public/.
  ignoreDeadLinks: [/\/assets\/figures\/[^/]+\/scene\.excalidraw$/],
  appearance: false,
  lastUpdated: false,
  themeConfig: {
    siteTitle: '图解 Agent 系统',
    logo: false,
    nav: publicMode ? [
      { text: '阅读目录', link: '/' },
      { text: '学习路径', link: '/learning-path' },
      { text: '机制', link: '/concepts/agent-loop' },
      { text: '项目', link: '/systems/pi' },
      { text: '对照', link: '/comparisons/loop-and-stop' },
      ...(pdfPublished ? [{ text: 'PDF', link: '/pdf' }] : []),
      { text: '反馈', link: '/feedback' }
    ] : [
      { text: '阅读起点', link: '/' },
      { text: '机制', link: '/concepts/agent-loop' },
      { text: '实现', link: '/systems/pi' },
      { text: '对照', link: '/comparisons/persisted-vs-visible' }
    ],
    sidebar: publicMode ? [
      { text: '阅读目录', items: [{ text: '全书目录', link: '/' }] },
      ...publicSidebar.map((part) => ({ ...part, collapsed: true }))
    ] : [
      { text: '先建立问题', items: [{ text: '阅读起点', link: '/' }] },
      { text: '理解机制', items: [
        { text: '行动怎样闭环', link: '/concepts/agent-loop' },
        { text: '上下文与记忆', link: '/concepts/context-vs-memory' },
        { text: '审批与沙箱', link: '/concepts/approval-vs-sandbox' }
      ] },
      { text: '沿源码看实现', items: [
        { text: 'Pi · 核心与外壳', link: '/systems/pi' },
        { text: 'Codex · 执行审批', link: '/systems/codex' },
        { text: 'Letta · 记忆可见性', link: '/systems/letta' }
      ] },
      { text: '比较取舍', items: [
        { text: '持久状态与模型所见', link: '/comparisons/persisted-vs-visible' }
      ] }
    ],
    outline: { level: [2, 3], label: '本页路径' },
    docFooter: { prev: '上一页', next: '下一页' },
    search: {
      provider: 'local',
      options: {
        translations: {
          button: { buttonText: '搜索正文', buttonAriaLabel: '搜索正文' },
          modal: {
            displayDetails: '显示详情', resetButtonTitle: '清空搜索', backButtonTitle: '关闭搜索',
            noResultsText: '没有结果，试试更短的关键词',
            footer: { selectText: '选择', selectKeyAriaLabel: '回车', navigateText: '导航', navigateUpKeyAriaLabel: '上箭头', navigateDownKeyAriaLabel: '下箭头', closeText: '关闭', closeKeyAriaLabel: 'Esc' }
          }
        },
        miniSearch: { options: { tokenize: tokens }, searchOptions: { fuzzy: 0, prefix: true } }
      }
    },
    socialLinks: []
  },
  head: publicMode ? [] : [['meta', { name: 'robots', content: 'noindex,nofollow' }]]
})
