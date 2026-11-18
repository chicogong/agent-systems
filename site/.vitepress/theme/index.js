import DefaultTheme from 'vitepress/theme-without-fonts'
import { useRoute } from 'vitepress'
import { h, nextTick, onMounted, watch } from 'vue'
import ReaderActions from './ReaderActions.vue'
import TracePlayer from './TracePlayer.vue'
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
  dialog.innerHTML = `<div class="figure-viewer-bar"><span class="figure-viewer-title">图稿细读</span><div class="figure-viewer-actions"><button type="button" class="figure-viewer-zoom" aria-pressed="false">放大细读</button><button type="button" class="figure-viewer-close" aria-label="关闭大图">关闭 ×</button></div></div><div class="figure-viewer-steps" hidden><div class="figure-viewer-steps-nav"><span class="figure-viewer-steps-count"></span><div class="figure-viewer-steps-buttons"><button type="button" class="figure-viewer-step-prev">上一步</button><button type="button" class="figure-viewer-step-next">下一步</button></div></div><p class="figure-viewer-steps-text"></p></div><div class="figure-viewer-stage"><img alt=""></div>${publicMode ? '' : '<div class="figure-viewer-links"><a class="figure-svg" target="_blank" rel="noopener">打开原尺寸 SVG</a><a class="figure-source" target="_blank" rel="noopener">下载可编辑图源</a></div>'}`
  document.body.append(dialog)
  const zoomButton = dialog.querySelector('.figure-viewer-zoom')
  const closeButton = dialog.querySelector('.figure-viewer-close')
  const stepsBox = dialog.querySelector('.figure-viewer-steps')
  const stepsCount = dialog.querySelector('.figure-viewer-steps-count')
  const stepsText = dialog.querySelector('.figure-viewer-steps-text')
  const stepPrevButton = dialog.querySelector('.figure-viewer-step-prev')
  const stepNextButton = dialog.querySelector('.figure-viewer-step-next')
  const viewerStage = dialog.querySelector('.figure-viewer-stage')
  const viewerImg = dialog.querySelector('img')
  let lastTrigger = null
  let recentClosedLabel = ''
  let recentClosedAt = 0
  let figureSteps = []
  let figureStepIndex = 0
  const renderFigureStep = (index) => {
    if (!figureSteps.length) {
      stepsBox.hidden = true
      return
    }
    figureStepIndex = Math.max(0, Math.min(figureSteps.length - 1, index))
    stepsBox.hidden = false
    stepsCount.textContent = `读图步骤 ${figureStepIndex + 1} / ${figureSteps.length}（支持 ← / → 切换）`
    stepsText.textContent = figureSteps[figureStepIndex]
    stepPrevButton.disabled = figureStepIndex === 0
    stepNextButton.disabled = figureStepIndex >= figureSteps.length - 1
  }
  const resolveLiveTrigger = (trigger) => {
    if (trigger && trigger.isConnected) return trigger
    const label = trigger?.getAttribute?.('aria-label') || recentClosedLabel
    if (label) {
      const match = Array.from(document.querySelectorAll('.figure-open')).find(
        (el) => el.getAttribute('aria-label') === label
      )
      if (match) return match
    }
    return document.querySelector('.figure-open')
  }
  const setZoom = (zoomed) => {
    dialog.classList.toggle('is-zoomed', zoomed)
    zoomButton.textContent = zoomed ? '适应窗口' : '放大细读'
    zoomButton.setAttribute('aria-pressed', zoomed ? 'true' : 'false')
    if (!zoomed && viewerStage) {
      viewerStage.scrollTo({ top: 0, left: 0, behavior: 'instant' })
    }
  }
  const openFigure = (img, trigger = null) => {
    if (!img) return
    lastTrigger = trigger
    recentClosedLabel = ''
    recentClosedAt = 0
    setZoom(false)
    viewerImg.src = img.src
    viewerImg.alt = img.alt
    const slug = img.src.match(/\/assets\/figures\/([^/]+)\/diagram\.svg/)?.[1]
    const details = slug ? document.getElementById('图的文字说明-' + slug) : null
    const listSteps = Array.from(details?.querySelectorAll('li') ?? [])
      .map((item) => item.textContent.trim())
      .filter(Boolean)
    const paraSteps = Array.from(details?.querySelectorAll('p') ?? [])
      .map((item) => item.textContent.trim())
      .filter((text) => text && !/^状态为/.test(text))
    figureSteps = listSteps.length > 0 ? listSteps : paraSteps
    renderFigureStep(0)
    if (!publicMode) {
      dialog.querySelector('.figure-svg').href = img.src
      dialog.querySelector('.figure-source').href = img.src.replace('/diagram.svg', '/scene.excalidraw')
    }
    dialog.showModal()
  }
  zoomButton.addEventListener('click', () => setZoom(!dialog.classList.contains('is-zoomed')))
  stepPrevButton.addEventListener('click', () => renderFigureStep(figureStepIndex - 1))
  stepNextButton.addEventListener('click', () => renderFigureStep(figureStepIndex + 1))
  const restoreTriggerFocus = () => {
    const rawTrigger = lastTrigger
    lastTrigger = null
    if (rawTrigger) {
      recentClosedLabel = rawTrigger.getAttribute?.('aria-label') || '放大图稿'
      recentClosedAt = performance.now()
    }
    const trigger = resolveLiveTrigger(rawTrigger)
    if (trigger && typeof trigger.focus === 'function') {
      trigger.focus({ preventScroll: true })
      requestAnimationFrame(() => {
        const live = resolveLiveTrigger(trigger)
        if (live && document.activeElement !== live) {
          live.focus({ preventScroll: true })
        }
      })
    }
  }
  const closeViewer = () => {
    setZoom(false)
    if (dialog.open) dialog.close()
    restoreTriggerFocus()
  }
  viewerImg.addEventListener('click', () => setZoom(!dialog.classList.contains('is-zoomed')))
  closeButton.addEventListener('click', closeViewer)
  dialog.addEventListener('cancel', (event) => {
    event.preventDefault()
    closeViewer()
  })
  dialog.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') {
      event.preventDefault()
      closeViewer()
      return
    }
    if (figureSteps.length > 1 && (event.key === 'ArrowLeft' || event.key === 'ArrowRight')) {
      event.preventDefault()
      renderFigureStep(figureStepIndex + (event.key === 'ArrowRight' ? 1 : -1))
    }
  })
  dialog.addEventListener('close', () => {
    setZoom(false)
    restoreTriggerFocus()
  })
  dialog.addEventListener('click', (event) => { if (event.target === dialog) closeViewer() })
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
      openFigure(img, button)
      return
    }
    const directImg = event.target.closest?.('.vp-doc img[src*="/assets/figures/"][src$="/diagram.svg"]')
    if (directImg && !directImg.closest('a')) {
      const pairedButton = directImg.parentElement?.querySelector('.figure-open')
      openFigure(directImg, pairedButton || directImg)
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
      return
    }
    if (event.defaultPrevented || event.metaKey || event.ctrlKey || event.altKey) return
    if (dialog.open || document.querySelector('.VPLocalSearchBox')) return
    const targetTag = event.target?.tagName
    if (targetTag === 'INPUT' || targetTag === 'TEXTAREA' || targetTag === 'SELECT' || event.target?.isContentEditable) return
    if (event.key === '/') {
      const searchBtn = document.querySelector('#local-search button')
      if (searchBtn) {
        event.preventDefault()
        searchBtn.click()
      }
      return
    }
    if (event.key === '[' || event.key === ']') {
      const selector = event.key === '[' ? 'a.reading-position-previous[href]' : 'a.reading-position-next[href]'
      const navLink = document.querySelector(selector)
      if (navLink) {
        event.preventDefault()
        navLink.click()
      }
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
    if (!dialog.open && recentClosedLabel && performance.now() - recentClosedAt < 1500) {
      const live = resolveLiveTrigger(null)
      if (live && document.activeElement !== live) {
        live.focus({ preventScroll: true })
      }
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
        'doc-footer-before': () => [h(TracePlayer), h(ReaderActions)]
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
