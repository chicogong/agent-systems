import DefaultTheme from 'vitepress/theme-without-fonts'
import { h } from 'vue'
import ReaderActions from './ReaderActions.vue'
import { inject, pageview } from '@vercel/analytics'
import { sanitizeAnalyticsEvent } from '../../scripts/analytics-policy.mjs'
import './style.css'

const publicMode = import.meta.env.VITE_PUBLIC_SITE === '1'

function installFigureViewer() {
  if (document.querySelector('.figure-viewer')) return
  const dialog = document.createElement('dialog')
  dialog.className = 'figure-viewer'
  dialog.setAttribute('aria-label', '图稿细读')
  dialog.innerHTML = `<div class="figure-viewer-bar"><span>图稿细读</span><button type="button" aria-label="关闭大图">关闭 ×</button></div><img alt="">${publicMode ? '' : '<div class="figure-viewer-links"><a class="figure-svg" target="_blank" rel="noopener">打开原尺寸 SVG</a><a class="figure-source" target="_blank" rel="noopener">下载可编辑图源</a></div>'}`
  document.body.append(dialog)
  dialog.querySelector('button').addEventListener('click', () => dialog.close())
  dialog.addEventListener('click', (event) => { if (event.target === dialog) dialog.close() })
  document.addEventListener('click', (event) => {
    const button = event.target.closest?.('.figure-open')
    if (!button) return
    const img = button.parentElement?.querySelector('img[src*="/assets/figures/"][src$="/diagram.svg"]')
    if (!img) return
    dialog.querySelector('img').src = img.src
    dialog.querySelector('img').alt = img.alt
    if (!publicMode) {
      dialog.querySelector('.figure-svg').href = img.src
      dialog.querySelector('.figure-source').href = img.src.replace('/diagram.svg', '/scene.excalidraw')
    }
    dialog.showModal()
  })
  const markFigures = () => document.querySelectorAll('.vp-doc img[src*="/assets/figures/"][src$="/diagram.svg"]').forEach((img) => {
    if (img.closest('a')) return
    if (img.parentElement?.querySelector('.figure-open')) return
    const button = document.createElement('button')
    button.type = 'button'
    button.className = 'figure-open'
    button.textContent = '放大图稿'
    button.setAttribute('aria-label', `放大图稿：${img.alt}`)
    img.insertAdjacentElement('afterend', button)
  })
  markFigures()
  new MutationObserver(markFigures).observe(document.body, { childList: true, subtree: true })
}

export default {
  ...DefaultTheme,
  Layout: () => h(DefaultTheme.Layout, null, {
    'doc-footer-before': () => h(ReaderActions)
  }),
  enhanceApp(context) {
    DefaultTheme.enhanceApp?.(context)
    if (typeof window !== 'undefined') {
      if (document.readyState === 'loading') window.addEventListener('DOMContentLoaded', installFigureViewer, { once: true })
      else installFigureViewer()
      if (publicMode && import.meta.env.VITE_READER_ANALYTICS === '1' && window.location.hostname === 'books.aimake.cc') {
        inject({ mode: 'production', disableAutoTrack: true, beforeSend: sanitizeAnalyticsEvent })
        pageview({ path: window.location.pathname })
        const previous = context.router.onAfterRouteChanged
        context.router.onAfterRouteChanged = (to) => {
          previous?.(to)
          pageview({ path: new URL(to, window.location.origin).pathname })
        }
      }
    }
  }
}
