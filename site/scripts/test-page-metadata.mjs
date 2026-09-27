import test from 'node:test'
import assert from 'node:assert/strict'
import { plainLabel, figureExplanation } from './page-metadata.mjs'

test('headings are plain labels without changing identifier punctuation', () => {
  assert.equal(plainLabel('`ctx.sessions` 与 **会话记忆**'), 'ctx.sessions 与 会话记忆')
  assert.equal(plainLabel('从 `tool_call` 到 `tool_result`'), '从 tool_call 到 tool_result')
})
test('links and inline HTML retain visible text', () => {
  assert.equal(plainLabel('[Hermes](https://example.org) 与 <span>Browser Use</span>'), 'Hermes 与 Browser Use')
})
test('missing titles and whitespace are normalized', () => {
  assert.equal(plainLabel(undefined), '')
  assert.equal(plainLabel('  沙箱\n   与权限  '), '沙箱 与权限')
})
test('figure alternatives keep teaching text but omit duplicate images and maintenance', () => {
  const markdown = '# 图名\n\n[SVG](diagram.svg)\n\n![预览](diagram.svg)\n\n## 文字版\n\n箭头表示读回，不等于完成。\n\n`build.py` 生成图源。\n\n## 生成与核验\n\n维护者运行导出器。\n\n## 适用边界\n\n不是运行录像。'
  assert.equal(figureExplanation(markdown), '箭头表示读回，不等于完成。\n\n不是运行录像。')
})
