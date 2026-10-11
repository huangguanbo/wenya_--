<template>
  <div class="space-y-6">
    <!-- 页面标题 -->
    <div class="flex justify-between items-center">
      <h1 class="text-2xl font-bold text-gray-900">📊 排行榜</h1>
      <button
        @click="toggleVisibility"
        class="text-sm text-gray-600 hover:text-gray-800"
      >
        {{ userStore.user?.show_in_ranking ? '退出排行榜' : '加入排行榜' }}
      </button>
    </div>

    <!-- Tab 切换 -->
    <div class="border-b">
      <nav class="-mb-px flex space-x-8">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="activeTab = tab.id"
          :class="[
            'py-4 px-1 border-b-2 font-medium text-sm',
            activeTab === tab.id
              ? 'border-green-500 text-green-600'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
          ]"
        >
          {{ tab.name }}
        </button>
      </nav>
    </div>

    <!-- 排行榜说明 -->
    <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
      <p class="text-sm text-blue-800">
        <span v-if="activeTab === 'overall'">
          💡 同年级综合排行榜：展示平均分前 50% 的同学，你是第{{ userRank?.rank_position || '-' }}名
        </span>
        <span v-else-if="activeTab === 'progress'">
          🚀 进步排行榜：根据最近 30 天的进步幅度排名，见证你的成长！
        </span>
        <span v-else-if="activeTab.startsWith('dimension')">
          🌟 {{ getDimensionName(activeTab) }}维度榜：展示该维度得分前 20% 的优秀作品
        </span>
      </p>
    </div>

    <!-- 排行榜列表 -->
    <div class="bg-white rounded-lg shadow overflow-hidden">
      <div class="divide-y">
        <div
          v-for="(item, index) in rankings"
          :key="item.user_id"
          class="p-4 flex items-center justify-between hover:bg-gray-50"
        >
          <div class="flex items-center space-x-4">
            <!-- 排名 -->
            <div
              :class="[
                'w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm',
                getRankStyle(item.rank_position)
              ]"
            >
              {{ item.rank_position }}
            </div>

            <!-- 用户信息 -->
            <div>
              <div class="font-medium text-gray-900">
                {{ item.nickname }}
              </div>
              <div class="text-sm text-gray-500">
                {{ item.average_score?.toFixed(1) || item.progress_score?.toFixed(2) || item.dimension_score }}
                {{ activeTab === 'overall' ? '分' : activeTab === 'progress' ? '进步分' : '分' }}
              </div>
            </div>
          </div>

          <!-- 百分位 -->
          <div v-if="item.percentile" class="text-sm text-green-600 font-medium">
            超过 {{ item.percentile }}% 的同学
          </div>
        </div>

        <div v-if="rankings.length === 0" class="p-8 text-center text-gray-500">
          暂无排名数据
        </div>
      </div>
    </div>

    <!-- 我的排名（固定底部） -->
    <div v-if="userRank" class="fixed bottom-0 left-0 right-0 bg-white border-t shadow-lg p-4">
      <div class="max-w-7xl mx-auto flex justify-between items-center">
        <div>
          <div class="text-sm text-gray-500">我的排名</div>
          <div class="text-lg font-bold text-gray-900">
            第 {{ userRank.rank_position }} 名 ·
            超过 {{ userRank.percentile }}% 的同学
          </div>
        </div>
        <div class="text-3xl font-bold text-green-600">
          {{ userRank.average_score?.toFixed(1) || userRank.progress_score?.toFixed(2) }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useUserStore } from '@/stores/user'
import api from '@/api'

const userStore = useUserStore()
const activeTab = ref('overall')

const tabs = [
  { id: 'overall', name: '综合榜' },
  { id: 'progress', name: '进步榜' },
  { id: 'dimension_theme', name: '立意' },
  { id: 'dimension_content', name: '内容' },
  { id: 'dimension_structure', name: '结构' },
  { id: 'dimension_language', name: '语言' },
  { id: 'dimension_creativity', name: '创意' }
]

const rankings = ref([])
const userRank = ref(null)

const getDimensionName = (tabId) => {
  const tab = tabs.find(t => t.id === tabId)
  return tab?.name || ''
}

const getRankStyle = (position) => {
  if (position === 1) return 'bg-yellow-400 text-yellow-900'
  if (position === 2) return 'bg-gray-300 text-gray-800'
  if (position === 3) return 'bg-amber-600 text-amber-50'
  return 'bg-gray-100 text-gray-600'
}

const loadRankings = async () => {
  try {
    let url
    if (activeTab.value === 'overall') {
      url = '/ranking/overall'
    } else if (activeTab.value === 'progress') {
      url = '/ranking/progress'
    } else if (activeTab.value.startsWith('dimension')) {
      const dimension = activeTab.value.replace('dimension_', '')
      url = `/ranking/dimension/${dimension}`
    }

    const res = await api.get(url)
    rankings.value = res.data.data.rankings || []
    userRank.value = res.data.data.user_rank
  } catch (error) {
    console.error('Failed to load rankings:', error)
  }
}

const toggleVisibility = async () => {
  try {
    await api.post('/ranking/toggle-visibility', {
      show: !userStore.user?.show_in_ranking
    })
    userStore.user.show_in_ranking = !userStore.user.show_in_ranking
    loadRankings()
  } catch (error) {
    console.error('Failed to toggle visibility:', error)
  }
}

watch(activeTab, loadRankings)
onMounted(loadRankings)
</script>
