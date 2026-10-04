// Strip reader-supplied queries and fragments before any analytics transmission.
export function sanitizeAnalyticsEvent(event) {
  if (event.type !== 'pageview') return null
  try {
    const url = new URL(event.url)
    if (url.protocol !== 'https:' || url.hostname !== 'books.aimake.cc') return null
    url.search = ''
    url.hash = ''
    return { ...event, url: url.href }
  } catch {
    return null
  }
}
