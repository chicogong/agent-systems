<script setup>
import { ref, watch } from 'vue'
import { useRoute } from 'vitepress'
import { cleanPageUrl, extractStudyMaterial, buildStudyPack } from '../../scripts/study-pack.mjs'

const route = useRoute()
const message = ref('')
const manualLink = ref('')
const manualPack = ref('')

watch(() => route.path, () => {
  message.value = ''
  manualLink.value = ''
  manualPack.value = ''
})

async function share() {
  manualPack.value = ''
  const text = cleanPageUrl(route.path, window.location.origin)
  try {
    if (navigator.share) {
      await navigator.share({ title: document.title, url: text })
      message.value = '已打开分享菜单'
    } else {
      await navigator.clipboard.writeText(text)
      message.value = '链接已复制，可以发给朋友'
    }
  } catch (error) {
    if (error.name === 'AbortError') return
    manualLink.value = text
    message.value = '请复制下方链接分享'
  }
}

async function copyStudyPack() {
  manualLink.value = ''
  const url = cleanPageUrl(route.path, window.location.origin)
  const { title, content } = extractStudyMaterial(document.querySelector('.vp-doc'), document.title)
  const pack = buildStudyPack({ title, url, content })
  try {
    if (!navigator.clipboard?.writeText) throw new Error('Clipboard unavailable')
    await navigator.clipboard.writeText(pack)
    manualPack.value = ''
    message.value = '已复制本章 AI 陪读材料包，可直接粘贴到常用 AI 助手'
  } catch {
    manualPack.value = pack
    message.value = '请全选下方文本框，复制本章 AI 陪读材料包'
  }
}
</script>

<template>
  <div class="reader-actions">
    <button type="button" @click="share">分享这一页</button>
    <button type="button" class="reader-ai-pack" @click="copyStudyPack">复制本章 AI 陪读包</button>
    <a href="/feedback">哪里没讲清楚？告诉作者</a>
    <span role="status" aria-live="polite">{{ message }}</span>
    <label v-if="manualLink">页面链接<input :value="manualLink" readonly @focus="$event.target.select()"></label>
    <label v-if="manualPack">AI 陪读材料包（请全选复制）<textarea :value="manualPack" rows="6" readonly @focus="$event.target.select()"></textarea></label>
  </div>
</template>
