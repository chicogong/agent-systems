import DefaultTheme from 'vitepress/theme-without-fonts'
import { useRoute } from 'vitepress'
import { h, nextTick, onMounted, watch } from 'vue'
import ReaderActions from './ReaderActions.vue'
import { inject, pageview } from '@vercel/analytics'
import { installReaderAnalytics } from '../../scripts/reader-analytics.mjs'
import './style.css'

const publicMode = import.meta.env.VITE_PUBLIC_SITE === '1'

function revealHashFigureDetails(rawHash = typeof window !== 'undefined' ? window.location.hash : '') {
  if (typeof document === 'undefined' || !rawHash || rawHash === '#') return false
  let id = ''
  try {
    id = decodeURIComponent(rawHash.replace(/^#/, ''))
  } catch {
    id = rawHash.replace(/^#/, '')
  }
  if (!id) return false
  const target = document.getElementById(id)
  if (!target) return false
  const details = target.matches?.('details.figure-text-alt')
    ? target
    : target.closest?.('details.figure-text-alt')
  if (!details) return false
  details.open = true
  const behavior = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth'
  requestAnimationFrame(() => {
    target.scrollIntoView({ behavior, block: 'start' })
  })
  return true
}

function installReaderControls() {
  if (document.querySelector('.figure-viewer')) {
    revealHashFigureDetails()
    return
  }
  const dialog = document.createElement('dialog')
  dialog.className = 'figure-viewer'
  dialog.setAttribute('aria-label', '图稿细读')
  dialog.innerHTML = `<div class="figure-viewer-bar"><span class="figure-viewer-title">图稿细读</span><div class="figure-viewer-actions"><button type="button" class="figure-viewer-zoom" aria-pressed="false">放大细读</button><button type="button" class="figure-viewer-close" aria-label="关闭大图">关闭 ×</button></div></div><div class="figure-viewer-stage"><img alt=""></div>${publicMode ? '' : '<div class="figure-viewer-links"><a class="figure-svg" target="_blank" rel="noopener">打开原尺寸 SVG</a><a class="figure-source" target="_blank" rel="noopener">下载可编辑图源</a></div>'}`
  document.body.append(dialog)
  const zoomButton = dialog.querySelector('.figure-viewer-zoom')
  const closeButton = dialog.querySelector('.figure-viewer-close')
  const viewerStage = dialog.querySelector('.figure-viewer-stage')
  const viewerImg = dialog.querySelector('img')
  const setZoom = (zoomed) => {
    dialog.classList.toggle('is-zoomed', zoomed)
    zoomButton.textContent = zoomed ? '适应窗口' : '放大细读'
    zoomButton.setAttribute('aria-pressed', zoomed ? 'true' : 'false')
    if (!zoomed && viewerStage) {
      viewerStage.scrollTo({ top: 0, left: 0, behavior: 'instant' })
    }
  }
  const openFigure = (img) => {
    if (!img) return
    setZoom(false)
    viewerImg.src = img.src
    viewerImg.alt = img.alt
    if (!publicMode) {
      dialog.querySelector('.figure-svg').href = img.src
      dialog.querySelector('.figure-source').href = img.src.replace('/diagram.svg', '/scene.excalidraw')
    }
    dialog.showModal()
  }
  zoomButton.addEventListener('click', () => setZoom(!dialog.classList.contains('is-zoomed')))
  viewerImg.addEventListener('click', () => setZoom(!dialog.classList.contains('is-zoomed')))
  closeButton.addEventListener('click', () => dialog.close())
  dialog.addEventListener('close', () => setZoom(false))
  dialog.addEventListener('click', (event) => { if (event.target === dialog) dialog.close() })
  document.addEventListener('click', (event) => {
    const anchor = event.target.closest?.('a[href*="#"]')
    if (anchor) {
      try {
        const url = new URL(anchor.getAttribute('href'), window.location.href)
        if (url.origin === window.location.origin && url.hash) {
          requestAnimationFrame(() => {
            if (!revealHashFigureDetails(url.hash)) {
              setTimeout(() => revealHashFigureDetails(url.hash), 120)
            }
          })
        }
      } catch {}
    }
    const button = event.target.closest?.('.figure-open')
    if (button) {
      const img = button.parentElement?.querySelector('img[src*="/assets/figures/"][src$="/diagram.svg"]')
      openFigure(img)
      return
    }
    const directImg = event.target.closest?.('.vp-doc img[src*="/assets/figures/"][src$="/diagram.svg"]')
    if (directImg && !directImg.closest('a')) {
      openFigure(directImg)
    }
  })
  window.addEventListener('hashchange', () => revealHashFigureDetails())
  const restoreSearchFocus = () => requestAnimationFrame(() => {
    if (!document.querySelector('.VPLocalSearchBox')) {
      document.querySelector('#local-search button')?.focus()
    }
  })
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && event.target.closest?.('.VPLocalSearchBox')) {
      restoreSearchFocus()
    }
  }, true)
  document.addEventListener('click', (event) => {
    if (event.target.closest?.('.VPLocalSearchBox .back-button, .VPLocalSearchBox .backdrop')) {
      restoreSearchFocus()
    }
  }, true)
  const markControls = () => {
    document.querySelectorAll('.vp-doc img[src*="/assets/figures/"][src$="/diagram.svg"]').forEach((img) => {
      if (img.closest('a')) return
      if (img.parentElement?.querySelector('.figure-open')) return
      const button = document.createElement('button')
      button.type = 'button'
      button.className = 'figure-open'
      button.textContent = '放大图稿'
      button.setAttribute('aria-label', `放大图稿：${img.alt}`)
      img.insertAdjacentElement('afterend', button)
    })
    // VitePress 1.6 labels the search field with an icon-only element.
    // Supply text for aria-labelledby without changing the visible control.
    const label = document.getElementById('localsearch-label')
    if (label && !label.querySelector('.reader-search-label')) {
      const text = document.createElement('span')
      text.className = 'reader-search-label'
      text.textContent = label.title || '搜索正文'
      label.append(text)
    }
  }
  markControls()
  revealHashFigureDetails()
  new MutationObserver(markControls).observe(document.body, { childList: true, subtree: true })
}

export default {
  ...DefaultTheme,
  Layout: {
    setup() {
      const route = useRoute()
      // Add interactive controls after Vue has hydrated the server markup.
      onMounted(installReaderControls)
      watch(() => route.path, () => {
        nextTick(() => revealHashFigureDetails())
      })
      return () => h(DefaultTheme.Layout, null, {
        'doc-footer-before': () => h(ReaderActions)
      })
    }
  },
  enhanceApp(context) {
    DefaultTheme.enhanceApp?.(context)
    if (typeof window !== 'undefined') {
      if (publicMode && import.meta.env.VITE_READER_ANALYTICS === '1' && window.location.hostname === 'books.aimake.cc') {
        installReaderAnalytics({
          router: context.router,
          origin: window.location.origin,
          pathname: window.location.pathname,
          inject,
          pageview
        })
      }
    }
  }
}
