import test from 'node:test'
import assert from 'node:assert/strict'
import { cleanPageUrl, extractStudyMaterial, buildStudyPack } from './study-pack.mjs'

function mockElement(tagName, { text = '', insideSelector = '', stripResultText } = {}) {
  return {
    tagName,
    textContent: text,
    closest(selector) {
      if (!insideSelector) return null
      return selector.split(',').some((item) => item.trim() === insideSelector) ? {} : null
    },
    cloneNode() {
      return {
        textContent: stripResultText ?? text,
        querySelectorAll() {
          return []
        }
      }
    }
  }
}

test('cleanPageUrl strips private query parameters and hashes', () => {
  assert.equal(
    cleanPageUrl('/concepts/agent-loop?token=secret#笔记', 'https://books.aimake.cc'),
    'https://books.aimake.cc/concepts/agent-loop'
  )
  assert.equal(cleanPageUrl('/', 'https://books.aimake.cc'), 'https://books.aimake.cc/')
})

test('extractStudyMaterial collects headings, prose, and lists while excluding navigation and footer noise', () => {
  const h1 = mockElement('H1', { text: '行动怎样闭环 #', stripResultText: '行动怎样闭环' })
  const nodes = [
    mockElement('P', { text: '导航栏噪音', insideSelector: '.reading-position' }),
    mockElement('P', { text: '第一段：把模型、宿主与工具拆清楚。' }),
    mockElement('H2', { text: '为什么会死循环 #', stripResultText: '为什么会死循环' }),
    mockElement('LI', { text: '缺少停止条件时持续重试' }),
    mockElement('P', { text: '列表内嵌段落不重复导出', insideSelector: 'li' }),
    mockElement('P', { text: '', stripResultText: '' }),
    mockElement('SUMMARY', { text: '展开本图无障碍纯文字导读：Agent 从任务到结果：概念总览' }),
    mockElement('P', { text: '箭头从观察结果回到模型决策。' }),
    mockElement('P', { text: '在线预览稿：书稿仍在校稿，系统篇以文内固定源码版本为准。' }),
    mockElement('P', { text: '书稿提交：abcdef123456。' }),
    mockElement('P', { text: '按钮区噪音', insideSelector: '.reader-actions' })
  ]
  const docRoot = {
    querySelector: (sel) => (sel === 'h1' ? h1 : null),
    querySelectorAll: () => nodes
  }
  const { title, content } = extractStudyMaterial(docRoot, '备用标题 | 图解 Agent 系统')
  assert.equal(title, '行动怎样闭环')
  assert.equal(content, [
    '第一段：把模型、宿主与工具拆清楚。',
    '## 为什么会死循环',
    '- 缺少停止条件时持续重试',
    '### 配图文字导读：Agent 从任务到结果：概念总览',
    '箭头从观察结果回到模型决策。'
  ].join('\n\n'))
})

test('buildStudyPack includes all four Socratic steps, clean URL, and extracted chapter material', () => {
  const pack = buildStudyPack({
    title: '上下文与记忆',
    url: 'https://books.aimake.cc/concepts/context-vs-memory',
    content: '保存了不等于进入了本轮输入。'
  })
  assert.match(pack, /我在读《图解 Agent 系统》的「上下文与记忆」（https:\/\/books\.aimake\.cc\/concepts\/context-vs-memory）/)
  assert.match(pack, /1\. 先确认收到的章节材料/)
  assert.match(pack, /2\. 围绕我的卡点举例解释/)
  assert.match(pack, /3\. 听我复述并换一个新情况考我/)
  assert.match(pack, /4\. 给出正文核对位置/)
  assert.match(pack, /保存了不等于进入了本轮输入。/)
})
