/**
 * 文芽 - 前端 API 调用示例（记忆增强功能）
 * 
 * 在 Vue 组件中使用新增的记忆管理 API
 */

// api.js - 添加新的 API 方法
import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:5000/api',
  withCredentials: true
})

// ==================== 记忆管理 API ====================

/**
 * 获取用户记忆画像
 */
export async function getMemoryProfile() {
  const response = await api.get('/memory/profile')
  return response.data.data
}

/**
 * 更新用户记忆画像
 * @param {Object} profile - 画像数据
 */
export async function updateMemoryProfile(profile) {
  const response = await api.put('/memory/profile', {
    writing_profile: profile
  })
  return response.data.data
}

/**
 * 检索记忆片段
 * @param {string} query - 搜索关键词
 * @param {string} category - 类别过滤
 * @param {number} topK - 返回数量
 */
export async function searchMemoryFragments(query, category = null, topK = 10) {
  const params = new URLSearchParams({
    q: query,
    top_k: topK
  })
  if (category) params.append('category', category)
  
  const response = await api.get(`/memory/fragments?${params}`)
  return response.data.data
}

/**
 * 获取记忆聚合摘要
 * @param {number} days - 时间范围（天）
 */
export async function getMemoryAggregate(days = 30) {
  const response = await api.get(`/memory/aggregate?days=${days}`)
  return response.data.data
}

/**
 * 获取交互上下文（用于 AI 对话增强）
 * @param {string} query - 当前查询
 * @param {number} writingId - 作文 ID
 */
export async function getInteractionContext(query, writingId = null) {
  const params = new URLSearchParams({ q: query })
  if (writingId) params.append('writing_id', writingId)
  
  const response = await api.get(`/memory/context?${params}`)
  return response.data.data
}

/**
 * 获取记忆统计
 */
export async function getMemoryStats() {
  const response = await api.get('/memory/stats')
  return response.data.data
}

/**
 * 清空记忆
 * @param {string} type - 类型：all/fragments/profile
 */
export async function clearMemory(type = 'fragments') {
  const response = await api.post('/memory/clear', { type })
  return response.data.data
}

// ==================== Vue 组合式 API 示例 ====================

// stores/memory.js - Pinia Store
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { 
  getMemoryProfile, 
  searchMemoryFragments, 
  getMemoryAggregate,
  getMemoryStats 
} from '../api/memory'

export const useMemoryStore = defineStore('memory', () => {
  // State
  const profile = ref(null)
  const fragments = ref([])
  const stats = ref(null)
  const loading = ref(false)
  const error = ref(null)

  // Getters
  const hasProfile = computed(() => !!profile.value)
  const fragmentCount = computed(() => fragments.value.length)

  // Actions
  async function loadProfile() {
    loading.value = true
    try {
      const data = await getMemoryProfile()
      profile.value = data.profile
      return data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function searchFragments(query, category) {
    loading.value = true
    try {
      const data = await searchMemoryFragments(query, category, 20)
      fragments.value = data.fragments
      return data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function refreshStats() {
    try {
      const data = await getMemoryStats()
      stats.value = data
      return data
    } catch (err) {
      error.value = err.message
      throw err
    }
  }

  function clearProfile() {
    profile.value = null
    fragments.value = []
  }

  return {
    // State
    profile,
    fragments,
    stats,
    loading,
    error,
    // Getters
    hasProfile,
    fragmentCount,
    // Actions
    loadProfile,
    searchFragments,
    refreshStats,
    clearProfile
  }
})

// ==================== Vue 组件示例 ====================

// <script setup>
// MemoryPanel.vue - 记忆管理面板组件
import { ref, onMounted } from 'vue'
import { useMemoryStore } from '@/stores/memory'
import { 
  searchMemoryFragments, 
  getMemoryAggregate, 
  clearMemory 
} from '@/api/memory'

const memoryStore = useMemoryStore()
const searchQuery = ref('')
const selectedCategory = ref('all')
const searchResults = ref([])
const aggregateSummary = ref(null)

onMounted(async () => {
  await memoryStore.loadProfile()
  await loadAggregate()
})

async function loadAggregate() {
  const data = await getMemoryAggregate(30)
  aggregateSummary.value = data.summary
}

async function handleSearch() {
  const data = await searchMemoryFragments(
    searchQuery.value,
    selectedCategory.value === 'all' ? null : selectedCategory.value,
    20
  )
  searchResults.value = data.fragments
}

async function handleClear(type) {
  if (confirm(`确定要清空${type}记忆吗？此操作不可恢复。`)) {
    await clearMemory(type)
    await memoryStore.loadProfile()
    await loadAggregate()
  }
}
// </script>

// <template>
// <!-- MemoryPanel.vue -->
// <div class="memory-panel">
//   <h2>记忆管理</h2>
  
//   <!-- 统计信息 -->
//   <div class="stats-card">
//     <div class="stat-item">
//       <span class="label">总交互次数</span>
//       <span class="value">{{ memoryStore.stats?.user_stats?.total_interactions || 0 }}</span>
//     </div>
//     <div class="stat-item">
//       <span class="label">记忆片段数</span>
//       <span class="value">{{ memoryStore.fragmentCount }}</span>
//     </div>
//   </div>

//   <!-- 搜索记忆 -->
//   <div class="search-section">
//     <input 
//       v-model="searchQuery" 
//       placeholder="搜索记忆..."
//       @keyup.enter="handleSearch"
//     />
//     <select v-model="selectedCategory">
//       <option value="all">全部类别</option>
//       <option value="writing_profile">写作画像</option>
//       <option value="interaction">交互记录</option>
//       <option value="knowledge">知识库</option>
//     </select>
//     <button @click="handleSearch">搜索</button>
//   </div>

//   <!-- 搜索结果 -->
//   <div class="results-section" v-if="searchResults.length > 0">
//     <div 
//       v-for="fragment in searchResults" 
//       :key="fragment.id"
//       class="result-item"
//     >
//       <div class="content">{{ fragment.content }}</div>
//       <div class="meta">
//         <span class="category">{{ fragment.category }}</span>
//         <span class="importance">重要性：{{ (fragment.importance * 100).toFixed(0) }}%</span>
//       </div>
//     </div>
//   </div>

//   <!-- 聚合摘要 -->
//   <div class="aggregate-section" v-if="aggregateSummary">
//     <h3>近 30 天摘要</h3>
//     <div v-for="(summary, category) in aggregateSummary.categories" :key="category">
//       <h4>{{ category }} ({{ summary.count }}条)</h4>
//       <p>平均重要性：{{ (summary.avg_importance * 100).toFixed(0) }}%</p>
//       <div class="keywords">
//         关键词：{{ summary.top_keywords.join(', ') }}
//       </div>
//     </div>
//   </div>

//   <!-- 管理操作 -->
//   <div class="actions-section">
//     <button 
//       class="btn-warning"
//       @click="handleClear('fragments')"
//     >
//       清空记忆片段
//     </button>
//     <button 
//       class="btn-warning"
//       @click="handleClear('profile')"
//     >
//       清空画像
//     </button>
//     <button 
//       class="btn-danger"
//       @click="handleClear('all')"
//     >
//       清空所有
//     </button>
//   </div>
// </div>
// </template>

// ==================== AI 对话增强示例 ====================

// WritingAssistant.vue - 写作助手组件（带记忆增强）
import { ref } from 'vue'
import { getInteractionContext } from '@/api/memory'

const messages = ref([])
const currentQuery = ref('')
const writingId = ref(null)

async function sendMessage(message) {
  // 获取增强上下文
  const context = await getInteractionContext(
    message,
    writingId.value
  )
  
  // 在请求中包含检索到的记忆
  const enhancedMessage = {
    role: 'user',
    content: message,
    context: context.context
  }
  
  // 发送到后端 AI 服务
  const response = await api.post('/writing/ai-chat', {
    message: message,
    writing_id: writingId.value,
    memory_context: context.context
  })
  
  messages.value.push({
    role: 'user',
    content: message
  })
  messages.value.push({
    role: 'assistant',
    content: response.data.data.response
  })
}
