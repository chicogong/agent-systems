import { defineConfig } from 'vitepress'
import { readFileSync } from 'node:fs'
import { plainLabel } from '../scripts/page-metadata.mjs'
import { svgDimensions } from '../scripts/image-metadata.mjs'

const publicMode = process.env.SITE_MODE === 'public'
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
  description: publicMode ? '《图解 Agent 系统》免费中文预览：用图解、讲解和案例连接入门学习、应用实践与开源实现。' : '沿问题、图与固定版本案例阅读 Agent 系统',
  cleanUrls: true,
  markdown: {
    config(md) {
      const image = md.renderer.rules.image
      const dimensions = new Map()
      md.renderer.rules.image = (tokens, index, ...rest) => {
        const token = tokens[index]
        const name = token.attrGet('src')?.match(/^\/assets\/figures\/([a-z0-9-]+)\/diagram\.svg$/)?.[1]
        if (name && publicMode) {
          if (!dimensions.has(name)) {
            // Read the reviewed publish asset, including when the book source
            // was supplied through BOOK_CONTENT_ROOT from another worktree.
            const svg = readFileSync(new URL(`../content/public/assets/figures/${name}/diagram.svg`, import.meta.url), 'utf8')
            dimensions.set(name, svgDimensions(svg))
          }
          const size = dimensions.get(name)
          if (size) {
            token.attrSet('width', String(size.width))
            token.attrSet('height', String(size.height))
            token.attrSet('loading', 'lazy')
            token.attrSet('decoding', 'async')
          }
        }
        return image(tokens, index, ...rest)
      }
    }
  },
  sitemap: publicMode ? { hostname: siteUrl } : undefined,
  transformPageData(pageData) {
    if (!publicMode) return
    const pathname = pageData.relativePath.replace(/index\.md$/, '').replace(/\.md$/, '')
    const canonical = `${siteUrl}/${pathname}`
    const isHome = pathname === ''
    const isArticle = !isHome && !new Set(['feedback', 'pdf', 'downloads', 'concepts', 'systems', 'comparisons', 'sources']).has(pathname)
    const title = plainLabel(pageData.title) || '图解 Agent 系统'
    pageData.title = title
    const description = pageData.frontmatter.description || '用图解、讲解和案例学习 Agent，再按兴趣深入应用与开源实现。'
    pageData.frontmatter.head ??= []
    pageData.frontmatter.head.push(
      ['link', { rel: 'canonical', href: canonical }],
      ['meta', { property: 'og:site_name', content: '图解 Agent 系统' }],
      ['meta', { property: 'og:locale', content: 'zh_CN' }],
      ['meta', { property: 'og:type', content: isArticle ? 'article' : 'website' }],
      ['meta', { property: 'og:title', content: title }],
      ['meta', { property: 'og:description', content: description }],
      ['meta', { property: 'og:url', content: canonical }],
      ['meta', { property: 'og:image', content: `${siteUrl}/assets/share/book.png` }],
      ['meta', { property: 'og:image:width', content: '1200' }],
      ['meta', { property: 'og:image:height', content: '630' }],
      ['meta', { property: 'og:image:alt', content: '图解 Agent 系统：学懂 Agent，把方法用起来' }],
      ['meta', { name: 'twitter:card', content: 'summary_large_image' }],
      ['meta', { name: 'twitter:image', content: `${siteUrl}/assets/share/book.png` }]
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
    sidebarMenuLabel: '目录',
    returnToTopLabel: '回到顶部',
    skipToContentLabel: '跳到正文',
    logo: false,
    nav: publicMode ? [
      { text: '开始阅读', link: '/' },
      { text: '学习与应用', link: '/learning-and-practice' },
      { text: '机制', link: '/concepts/agent-loop' },
      { text: '项目', link: '/systems' },
      { text: '对照', link: '/comparisons/loop-and-stop' },
      { text: '离线阅读', link: '/downloads' },
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
  head: publicMode
    ? [['meta', { name: 'msvalidate.01', content: 'CB718F30B0F11E2795CD6F9FEE86DE7B' }]]
    : [['meta', { name: 'robots', content: 'noindex,nofollow' }]]
})
