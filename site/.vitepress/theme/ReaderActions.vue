<script setup>
import { ref, watch } from 'vue'
import { useRoute } from 'vitepress'

const route = useRoute()
const message = ref('')
const manualLink = ref('')
watch(() => route.path, () => {
  message.value = ''
  manualLink.value = ''
})

async function share() {
  const url = new URL(route.path, window.location.origin)
  url.search = ''
  url.hash = ''
  const text = url.href
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
</script>

<template>
  <div class="reader-actions">
    <button type="button" @click="share">分享这一页</button>
    <a href="/feedback">哪里没讲清楚？告诉作者</a>
    <span role="status" aria-live="polite">{{ message }}</span>
    <label v-if="manualLink">页面链接<input :value="manualLink" readonly @focus="$event.target.select()"></label>
  </div>
</template>
