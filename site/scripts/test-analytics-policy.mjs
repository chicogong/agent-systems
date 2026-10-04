import test from 'node:test'
import assert from 'node:assert/strict'
import { sanitizeAnalyticsEvent } from './analytics-policy.mjs'

test('reader queries and fragments never leave in pageview URLs', () => {
  assert.deepEqual(sanitizeAnalyticsEvent({ type: 'pageview', url: 'https://books.aimake.cc/concepts/agent-loop?email=private@example.com#secret' }),
    { type: 'pageview', url: 'https://books.aimake.cc/concepts/agent-loop' })
})
test('no local previews, alternate hosts or custom events are sent', () => {
  for (const event of [
    { type: 'pageview', url: 'http://localhost:4173/' },
    { type: 'pageview', url: 'https://example.com/' },
    { type: 'event', url: 'https://books.aimake.cc/' },
    { type: 'pageview', url: 'invalid' }
  ]) assert.equal(sanitizeAnalyticsEvent(event), null)
})
