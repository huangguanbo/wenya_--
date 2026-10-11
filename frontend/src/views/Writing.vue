<template>
  <div class="h-[calc(100vh-4rem)] flex">
    <!-- 左侧：AI 对话区 -->
    <div :class="['flex flex-col', isDesktop ? 'w-full md:w-1/3 lg:w-1/4 border-r' : 'flex-1', !isDesktop && activeTab === 'editor' ? 'hidden' : '']">
      <!-- 对话历史 -->
      <div ref="chatContainer" class="flex-1 overflow-y-auto p-4 space-y-4">
        <div v-if="messages.length === 0" class="text-center text-gray-400 text-sm mt-8">
          向 AI 教练提问，或点击下方快捷操作开始
        </div>
        <div v-for="(msg, index) in messages" :key="index"
             :class="['flex', msg.role === 'user' ? 'justify-end' : 'justify-start']">
          <div
            :class="['max-w-[85%] rounded-lg px-4 py-2',
                     msg.role === 'user' ? 'bg-green-600 text-white' : 'bg-gray-100 text-gray-800']">
            <p class="text-sm whitespace-pre-wrap">{{ msg.content }}</p>
          </div>
        </div>
        <div v-if="loading" class="flex justify-start">
          <div class="bg-gray-100 rounded-lg px-4 py-2">
            <div class="flex space-x-2">
              <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
              <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
              <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.4s"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- 输入框 -->
      <div class="border-t p-4">
        <div class="flex flex-wrap gap-2 mb-2">
          <button
            v-for="type in quickActions"
            :key="type.value"
            @click="sendQuickAction(type)"
            class="px-3 py-1 text-xs bg-green-50 text-green-700 rounded-full hover:bg-green-100"
          >
            {{ type.label }}
          </button>
        </div>
        <div class="flex space-x-2">
          <input
            v-model="inputMessage"
            @keyup.enter="sendMessage"
            type="text"
            placeholder="向 AI 教练提问..."
            class="flex-1 px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 text-sm"
          />
          <button
            @click="sendMessage"
            :disabled="loading || !inputMessage.trim() || !writingId"
            class="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 text-sm"
          >
            发送
          </button>
        </div>
      </div>
    </div>

    <!-- 右侧：编辑器 -->
    <div :class="['hidden md:flex md:flex-1 flex-col', isDesktop ? '' : 'hidden']">
      <!-- 标题栏 -->
      <div class="border-b p-4">
        <input
          v-model="title"
          type="text"
          placeholder="作文标题"
          class="w-full text-xl font-bold border-none focus:outline-none focus:ring-0"
        />
      </div>

      <!-- 编辑器 -->
      <div class="flex-1 p-4">
        <textarea
          ref="editor"
          v-model="content"
          @input="handleInput"
          placeholder="开始你的写作..."
          class="w-full h-full resize-none border-none focus:outline-none text-base leading-relaxed"
        ></textarea>
      </div>

      <!-- 底部工具栏 -->
      <div class="border-t p-4 flex justify-between items-center">
        <div class="text-sm text-gray-500">
          {{ wordCount }} 字
          <span v-if="autoSaveStatus" class="ml-2 text-xs text-gray-400">{{ autoSaveStatus }}</span>
        </div>
        <div class="flex space-x-3">
          <button
            @click="saveDraft"
            :disabled="saving || !writingId"
            class="px-4 py-2 text-sm text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 disabled:opacity-50"
          >
            {{ saving ? '保存中...' : '保存草稿' }}
          </button>
          <button
            @click="submitWriting"
            :disabled="!canSubmit"
            class="px-4 py-2 text-sm text-white bg-green-600 rounded-md hover:bg-green-700 disabled:opacity-50"
          >
            提交评分
          </button>
        </div>
      </div>
    </div>

    <!-- 移动端编辑器（Tab 切换） -->
    <div v-if="!isDesktop" :class="['flex-1 flex flex-col', activeTab === 'chat' ? 'hidden' : '']">
      <div class="border-b">
        <div class="flex">
          <button
            @click="activeTab = 'editor'"
            :class="['flex-1 px-4 py-2 text-sm font-medium',
                     activeTab === 'editor' ? 'text-green-600 border-b-2 border-green-600' : 'text-gray-500']"
          >
            写作
          </button>
          <button
            @click="activeTab = 'chat'"
            :class="['flex-1 px-4 py-2 text-sm font-medium',
                     activeTab === 'chat' ? 'text-green-600 border-b-2 border-green-600' : 'text-gray-500']"
          >
            AI 指导
          </button>
        </div>
      </div>

      <div class="flex-1 p-4 flex flex-col">
        <input
          v-model="title"
          type="text"
          placeholder="作文标题"
          class="w-full text-lg font-bold border-none focus:outline-none mb-4"
        />
        <textarea
          v-model="content"
          @input="handleInput"
          placeholder="开始你的写作..."
          class="flex-1 w-full resize-none border-none focus:outline-none text-base leading-relaxed"
        ></textarea>
        <div class="border-t pt-3 flex justify-between items-center">
          <div class="text-sm text-gray-500">
            {{ wordCount }} 字
            <span v-if="autoSaveStatus" class="ml-2 text-xs text-gray-400">{{ autoSaveStatus }}</span>
          </div>
          <div class="flex space-x-3">
            <button
              @click="saveDraft"
              :disabled="saving || !writingId"
              class="px-4 py-2 text-sm text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 disabled:opacity-50"
            >
              {{ saving ? '保存中...' : '保存草稿' }}
            </button>
            <button
              @click="submitWriting"
              :disabled="!canSubmit"
              class="px-4 py-2 text-sm text-white bg-green-600 rounded-md hover:bg-green-700 disabled:opacity-50"
            >
              提交评分
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import api from '@/api'

const route = useRoute()
const writingId = ref(route.params.id || null)

const chatContainer = ref(null)
const editor = ref(null)

const title = ref('')
const content = ref('')
const wordCount = ref(0)
const messages = ref([])
const inputMessage = ref('')
const loading = ref(false)
const saving = ref(false)
const activeTab = ref('editor')
const autoSaveStatus = ref('')

let autoSaveTimer = null

const isDesktop = ref(window.innerWidth >= 768)

const handleResize = () => {
  isDesktop.value = window.innerWidth >= 768
}

const quickActions = [
  { label: '💡 审题指导', value: 'help_understand_prompt', sessionType: 'help_understand_prompt' },
  { label: '📚 素材启发', value: 'suggest_materials', sessionType: 'suggest_materials' },
  { label: '✏️ 段落修改', value: 'revise_paragraph', sessionType: 'revise_paragraph' },
  { label: '📊 评分标准', value: 'explain_scoring', sessionType: 'explain_scoring' }
]

const canSubmit = computed(() => {
  return title.value.trim() && content.value.length >= 100 && writingId.value
})

const handleInput = () => {
  wordCount.value = content.value.length
  if (!writingId.value && (title.value || content.value)) {
    createWriting()
  }
  scheduleAutoSave()
}

const scheduleAutoSave = () => {
  if (autoSaveTimer) clearTimeout(autoSaveTimer)
  autoSaveTimer = setTimeout(() => {
    if (writingId.value && (title.value || content.value)) {
      saveDraft()
    }
  }, 5000)
}

const sendMessage = async (sessionType = 'writing_guidance') => {
  if (!inputMessage.value.trim() || loading.value || !writingId.value) return

  const message = inputMessage.value.trim()
  messages.value.push({ role: 'user', content: message })
  inputMessage.value = ''
  loading.value = true

  await nextTick()
  scrollToBottom()

  try {
    const res = await api.post(`/writing/${writingId.value}/ai-chat`, {
      message,
      session_type: sessionType
    })
    messages.value.push({ role: 'assistant', content: res.data.data.response })
  } catch (error) {
    messages.value.push({ role: 'assistant', content: 'AI 教练暂时不可用，请稍后再试。' })
  } finally {
    loading.value = false
    await nextTick()
    scrollToBottom()
  }
}

const sendQuickAction = (type) => {
  inputMessage.value = type.label.replace(/^[^\s]+\s/, '')
  sendMessage(type.sessionType)
}

const scrollToBottom = () => {
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  }
}

const saveDraft = async () => {
  if (!writingId.value) return
  saving.value = true
  autoSaveStatus.value = '保存中...'
  try {
    await api.post(`/writing/${writingId.value}/draft`, {
      title: title.value,
      content: content.value
    })
    autoSaveStatus.value = '已保存'
    setTimeout(() => { autoSaveStatus.value = '' }, 2000)
  } catch (error) {
    autoSaveStatus.value = '保存失败'
    setTimeout(() => { autoSaveStatus.value = '' }, 2000)
  } finally {
    saving.value = false
  }
}

const createWriting = async () => {
  try {
    const res = await api.post('/writing', {
      title: title.value || '未命名作文',
      content: content.value
    })
    writingId.value = res.data.data.id
  } catch (error) {
    console.error('Failed to create writing:', error)
  }
}

const submitWriting = async () => {
  if (!canSubmit.value) return
  if (!confirm('确定要提交作文进行评分吗？')) return

  try {
    await api.post(`/writing/${writingId.value}/submit`, {
      title: title.value,
      content: content.value
    })
    alert('作文已提交，正在评分中...')
  } catch (error) {
    alert('提交失败：' + (error.response?.data?.message || '请稍后重试'))
  }
}

onMounted(async () => {
  window.addEventListener('resize', handleResize)
  if (writingId.value) {
    try {
      const res = await api.get(`/writing/${writingId.value}`)
      title.value = res.data.data.title
      content.value = res.data.data.content
      wordCount.value = res.data.data.word_count || 0
    } catch (error) {
      console.error('Failed to load writing:', error)
    }
  }
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  if (autoSaveTimer) clearTimeout(autoSaveTimer)
})
</script>
