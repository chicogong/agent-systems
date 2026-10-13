import test from 'node:test'
import assert from 'node:assert/strict'
import { installReaderAnalytics } from './reader-analytics.mjs'
import { sanitizeAnalyticsEvent } from './analytics-policy.mjs'

function fixture({ origin = 'https://books.aimake.cc', pathname = '/feedback', previous } = {}) {
  const injections = []
  const views = []
  const router = { onAfterRouteChanged: previous }
  installReaderAnalytics({
    router, origin, pathname,
    inject: (options) => injections.push(options),
    pageview: (view) => views.push(view)
  })
  return { router, injections, views }
}

test('one explicit first view ignores the initial route callback', () => {
  const { router, injections, views } = fixture()
  assert.deepEqual(injections, [{
    mode: 'production', disableAutoTrack: true, beforeSend: sanitizeAnalyticsEvent
  }])
  router.onAfterRouteChanged('/feedback')
  router.onAfterRouteChanged('https://books.aimake.cc/feedback')
  assert.deepEqual(views, [{ path: '/feedback' }])
})

test('queries and fragments never create a duplicate or enter the view path', () => {
  const { router, views } = fixture()
  for (const route of [
    '/feedback?email=private@example.com#private',
    '?search=private',
    '#private',
    'https://books.aimake.cc/feedback#private'
  ]) router.onAfterRouteChanged(route)
  router.onAfterRouteChanged('/concepts/agent-loop?search=private#private')
  router.onAfterRouteChanged('#another')
  assert.deepEqual(views, [{ path: '/feedback' }, { path: '/concepts/agent-loop' }])
})

test('each different pathname, including returning to a page, counts once', () => {
  const { router, views } = fixture()
  for (const route of ['/', '/', '/systems/pi', '/systems/pi#code', '/feedback']) {
    router.onAfterRouteChanged(route)
  }
  assert.deepEqual(views, [
    { path: '/feedback' }, { path: '/' }, { path: '/systems/pi' }, { path: '/feedback' }
  ])
})

test('external and invalid route callbacks do not send views or reset the current path', () => {
  const { router, views } = fixture()
  for (const route of [
    'https://example.com/elsewhere',
    '//example.com/elsewhere',
    'http://books.aimake.cc/elsewhere',
    'https://books.aimake.cc:444/elsewhere',
    'javascript:alert(1)',
    'http://',
    undefined,
    null
  ]) router.onAfterRouteChanged(route)
  router.onAfterRouteChanged('/feedback')
  assert.deepEqual(views, [{ path: '/feedback' }])
})

test('previous callback keeps its receiver, arguments and exact return value', () => {
  const seen = []
  const expected = Promise.resolve('existing callback result')
  const { router, views } = fixture({ previous: function (...args) {
    seen.push({ receiver: this, args })
    return expected
  } })
  assert.equal(router.onAfterRouteChanged('/', 'extra argument'), expected)
  assert.equal(seen[0].receiver, router)
  assert.deepEqual(seen[0].args, ['/', 'extra argument'])
  assert.deepEqual(views, [{ path: '/feedback' }, { path: '/' }])
})

test('previous callback errors are preserved and do not produce a new view', () => {
  const error = new Error('existing callback error')
  const { router, views } = fixture({ previous: () => { throw error } })
  assert.throws(() => router.onAfterRouteChanged('/'), (actual) => actual === error)
  assert.deepEqual(views, [{ path: '/feedback' }])
})

test('alternate origins neither inject nor replace the existing router callback', () => {
  const previous = () => 'unchanged'
  for (const origin of ['http://localhost:4173', 'https://example.com', 'http://books.aimake.cc', 'https://books.aimake.cc:444']) {
    const { router, injections, views } = fixture({ origin, previous })
    assert.equal(router.onAfterRouteChanged, previous)
    assert.deepEqual(injections, [])
    assert.deepEqual(views, [])
  }
})
