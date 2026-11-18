<script setup>
import { computed, ref, watch } from 'vue'
import { useRoute } from 'vitepress'
import { resolveTraceLab } from '../../scripts/trace-presets.mjs'

const route = useRoute()
const resolved = computed(() => resolveTraceLab(route.path))
const modeIndex = ref(0)
const stepIndex = ref(0)

watch(() => route.path, () => {
  modeIndex.value = 0
  stepIndex.value = 0
})

const currentMode = computed(() => {
  const modes = resolved.value?.lab.modes ?? []
  return modes[modeIndex.value] ?? modes[0] ?? null
})

const currentStep = computed(() => {
  const steps = currentMode.value?.steps ?? []
  return steps[stepIndex.value] ?? steps[0] ?? null
})

function selectMode(index) {
  modeIndex.value = index
  stepIndex.value = 0
}

function goToStep(index) {
  const max = (currentMode.value?.steps.length ?? 1) - 1
  stepIndex.value = Math.max(0, Math.min(max, index))
}
</script>

<template>
  <component
    :is="resolved.isPrimaryLabPage ? 'section' : 'details'"
    v-if="resolved && currentMode && currentStep"
    class="trace-player"
    :class="{ 'trace-player-drawer': !resolved.isPrimaryLabPage }"
    :aria-label="resolved.isPrimaryLabPage ? '交互式状态机回放' : undefined"
  >
    <summary v-if="!resolved.isPrimaryLabPage" class="trace-player-summary">
      <span>动手演练 · 在浏览器里单步回放「{{ resolved.lab.title }}」状态机</span>
      <span class="trace-player-summary-hint">点击展开交互模拟</span>
    </summary>

    <div class="trace-player-body">
      <div class="trace-player-head">
        <span class="trace-player-kicker">确定性教学回放 · 零依赖浏览器沙盒</span>
        <h3 class="trace-player-title">{{ resolved.lab.title }}</h3>
        <p class="trace-player-question">{{ resolved.lab.question }}</p>
      </div>

      <div class="trace-player-modes" role="group" aria-label="运行模式">
        <button
          v-for="(mode, index) in resolved.lab.modes"
          :key="mode.id"
          type="button"
          class="trace-player-mode"
          :aria-pressed="index === modeIndex ? 'true' : 'false'"
          @click="selectMode(index)"
        >
          {{ mode.label }}
        </button>
      </div>

      <div class="trace-player-verdict" :data-tone="currentMode.verdict.tone">
        <strong>{{ currentMode.verdict.badge }}</strong>
        <span>{{ currentMode.verdict.summary }}</span>
      </div>

      <div class="trace-player-nav">
        <div class="trace-player-controls">
          <button type="button" :disabled="stepIndex === 0" @click="goToStep(stepIndex - 1)">上一步</button>
          <button
            type="button"
            :disabled="stepIndex >= currentMode.steps.length - 1"
            @click="goToStep(stepIndex + 1)"
          >
            下一步
          </button>
          <button type="button" :disabled="stepIndex === 0" @click="goToStep(0)">重置</button>
        </div>
        <div class="trace-player-pills" role="group" aria-label="步骤列表">
          <button
            v-for="(step, index) in currentMode.steps"
            :key="`${currentMode.id}-${index}`"
            type="button"
            class="trace-player-pill"
            :aria-current="index === stepIndex ? 'step' : undefined"
            @click="goToStep(index)"
          >
            Step {{ index + 1 }}: {{ step.title }}
          </button>
        </div>
      </div>

      <div class="trace-player-stage">
        <div class="trace-player-meta">
          <span class="trace-player-badge">{{ currentStep.actor }}</span>
          <code class="trace-player-event">{{ currentStep.event }}</code>
        </div>
        <p class="trace-player-explanation">{{ currentStep.explanation }}</p>
        <div class="trace-player-grid">
          <div class="trace-player-pane">
            <div class="trace-player-pane-title">本步事件输入 / 观测 (Event)</div>
            <pre><code>{{ JSON.stringify(currentStep.payload, null, 2) }}</code></pre>
          </div>
          <div class="trace-player-pane">
            <div class="trace-player-pane-title">宿主与账本状态快照 (State)</div>
            <pre><code>{{ JSON.stringify(currentStep.state, null, 2) }}</code></pre>
          </div>
        </div>
      </div>

      <div class="trace-player-footer">
        <div class="trace-player-cli">
          <span>本地复现命令：</span>
          <code>{{ currentMode.cli }}</code>
        </div>
        <a v-if="!resolved.isPrimaryLabPage" class="trace-player-link" :href="resolved.lab.route">
          打开对应实验章节 →
        </a>
      </div>
    </div>
  </component>
</template>
