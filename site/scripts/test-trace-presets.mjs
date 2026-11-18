import test from 'node:test'
import assert from 'node:assert/strict'
import { TRACE_LABS, resolveTraceLab } from './trace-presets.mjs'

test('all 5 labs define deterministic modes, CLI commands, and non-empty trace steps', () => {
  const expectedIds = ['first-agent-loop', 'context-budget', 'evidence-contract', 'remote-effect', 'http-receipt']
  assert.deepEqual(Object.keys(TRACE_LABS), expectedIds)

  for (const lab of Object.values(TRACE_LABS)) {
    assert.ok(lab.title.length > 0)
    assert.ok(lab.question.length > 0)
    assert.match(lab.route, /^\/labs\//)
    assert.ok(lab.companionRoutes.length >= 1)
    assert.ok(lab.modes.length >= 3, `${lab.id} should define at least 3 modes`)

    for (const mode of lab.modes) {
      assert.ok(mode.id && mode.label)
      assert.match(mode.cli, /^python3 examples\//)
      assert.ok(['ok', 'warn', 'danger'].includes(mode.verdict.tone))
      assert.ok(mode.verdict.badge && mode.verdict.summary)
      assert.ok(mode.steps.length >= 2, `${lab.id}:${mode.id} should have at least 2 steps`)
      for (const step of mode.steps) {
        assert.ok(step.title && step.actor && step.event && step.explanation)
        assert.equal(typeof step.payload, 'object')
        assert.equal(typeof step.state, 'object')
      }
    }
  }
})

test('resolveTraceLab routes lab pages and companion reading pages cleanly', () => {
  const primary = resolveTraceLab('/labs/first-agent-loop.html?from=home#top')
  assert.equal(primary?.lab.id, 'first-agent-loop')
  assert.equal(primary?.isPrimaryLabPage, true)

  const companionConcept = resolveTraceLab('/concepts/agent-loop')
  assert.equal(companionConcept?.lab.id, 'first-agent-loop')
  assert.equal(companionConcept?.isPrimaryLabPage, false)

  const companionComparison = resolveTraceLab('/comparisons/completion-and-evidence/')
  assert.equal(companionComparison?.lab.id, 'http-receipt')
  assert.equal(companionComparison?.isPrimaryLabPage, false)

  assert.equal(resolveTraceLab('/'), null)
  assert.equal(resolveTraceLab('/systems/pi'), null)
})
