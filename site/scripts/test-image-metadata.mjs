import test from 'node:test'
import assert from 'node:assert/strict'
import { svgDimensions } from './image-metadata.mjs'

test('SVG viewBox preserves the aspect ratio regardless of export scale', () => {
  assert.deepEqual(svgDimensions('<svg viewBox="0 0 988 687" width="1976" height="1374">'),
    { width: 988, height: 687 })
})
test('SVG dimensions allow comma-separated and nonzero-origin canvases', () => {
  assert.deepEqual(svgDimensions("<svg viewBox='-12, 3, 1200, 840'>"),
    { width: 1200, height: 840 })
})
test('missing, malformed and nonpositive SVG bounds are not guessed', () => {
  for (const source of ['', '<svg>', '<svg viewBox="0 0 20">',
    '<svg viewBox="0 0 nope 20">', '<svg viewBox="0 0 20 0">',
    '<svg viewBox="0 0 -1 20">']) {
    assert.equal(svgDimensions(source), null)
  }
})
