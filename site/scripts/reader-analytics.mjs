import { sanitizeAnalyticsEvent } from './analytics-policy.mjs'

// VitePress calls onAfterRouteChanged for the initial route as well. Keep one
// explicit first view, then count only transitions to a different pathname.
export function installReaderAnalytics({ router, origin, pathname, inject, pageview }) {
  if (origin !== 'https://books.aimake.cc') return

  inject({ mode: 'production', disableAutoTrack: true, beforeSend: sanitizeAnalyticsEvent })
  let lastPath

  function track(to) {
    if (typeof to !== 'string') return
    let url
    try {
      url = new URL(to, `${origin}${lastPath ?? '/'}`)
    } catch {
      return
    }
    if (url.origin !== origin || url.pathname === lastPath) return
    lastPath = url.pathname
    pageview({ path: lastPath })
  }

  track(pathname)
  const previous = router.onAfterRouteChanged
  router.onAfterRouteChanged = function (...args) {
    const result = previous?.apply(this, args)
    track(args[0])
    return result
  }
}
