<template>
  <div class="space-y-8">
    <!-- 欢迎区 -->
    <div class="bg-gradient-to-r from-green-500 to-green-600 rounded-lg shadow-lg p-8 text-white">
      <h1 class="text-3xl font-bold mb-2">
        👋 你好，{{ userStore.user?.nickname || userStore.user?.username }}！
      </h1>
      <p class="text-green-100">
        继续你的写作之旅，今天也要加油哦～
      </p>
    </div>

    <!-- 统计数据 -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div v-for="stat in stats" :key="stat.label"
           class="bg-white rounded-lg shadow p-6 text-center">
        <div class="text-3xl font-bold text-green-600">{{ stat.value }}</div>
        <div class="text-sm text-gray-500 mt-1">{{ stat.label }}</div>
      </div>
    </div>

    <!-- 快速入口 -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <!-- 开始写作 -->
      <div class="bg-white rounded-lg shadow p-6">
        <h2 class="text-xl font-bold text-gray-900 mb-4">📝 开始写作</h2>
        <p class="text-gray-600 mb-4">选择一个题目，开始你的创作吧</p>
        <button
          @click="$router.push('/writing')"
          class="w-full px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
        >
          新建作文
        </button>
      </div>

      <!-- 继续写作 -->
      <div class="bg-white rounded-lg shadow p-6">
        <h2 class="text-xl font-bold text-gray-900 mb-4">📖 继续写作</h2>
        <div v-if="recentDraft" class="space-y-2">
          <p class="text-gray-600 truncate">{{ recentDraft.title }}</p>
          <p class="text-sm text-gray-500">上次编辑：{{ formatDate(recentDraft.updated_at) }}</p>
          <button
            @click="$router.push(`/writing/${recentDraft.id}`)"
            class="w-full px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200"
          >
            继续编辑
          </button>
        </div>
        <p v-else class="text-gray-500 text-sm">暂无草稿</p>
      </div>
    </div>

    <!-- 成长曲线 -->
    <div class="bg-white rounded-lg shadow p-6">
      <h2 class="text-xl font-bold text-gray-900 mb-4">📈 成长曲线</h2>
      <div ref="chartContainer" class="h-64"></div>
    </div>

    <!-- 最近作品 -->
    <div class="bg-white rounded-lg shadow p-6">
      <div class="flex justify-between items-center mb-4">
        <h2 class="text-xl font-bold text-gray-900">📚 最近作品</h2>
        <router-link to="/writings" class="text-sm text-green-600 hover:text-green-700">
          查看全部
        </router-link>
      </div>
      <div class="space-y-3">
        <div v-for="work in recentWorks" :key="work.id"
             @click="$router.push(`/writing/${work.id}`)"
             class="p-4 border rounded-lg hover:shadow-md cursor-pointer transition">
          <div class="flex justify-between items-start">
            <div>
              <h3 class="font-medium text-gray-900">{{ work.title }}</h3>
              <p class="text-sm text-gray-500 mt-1">
                {{ work.word_count }}字 · {{ formatDate(work.created_at) }}
              </p>
            </div>
            <div v-if="work.overall_score" class="text-right">
              <div class="text-2xl font-bold text-green-600">{{ work.overall_score }}</div>
              <div class="text-xs text-gray-500">分</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useUserStore } from '@/stores/user'
import api from '@/api'
import * as echarts from 'echarts'

const userStore = useUserStore()
const chartContainer = ref(null)

const stats = ref([
  { label: '总写作数', value: 0 },
  { label: '平均分', value: 0 },
  { label: '最高分', value: 0 },
  { label: '连续天数', value: 0 }
])

const recentDraft = ref(null)
const recentWorks = ref([])

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN')
}

const loadStats = async () => {
  try {
    const res = await api.get('/stats')
    const data = res.data.data
    stats.value = [
      { label: '总写作数', value: data.total_writings || 0 },
      { label: '平均分', value: (data.average_score || 0).toFixed(1) },
      { label: '最高分', value: (data.best_score || 0).toFixed(1) },
      { label: '连续天数', value: data.profile?.consecutive_days || 0 }
    ]
  } catch (error) {
    console.error('Failed to load stats:', error)
  }
}

const loadRecentWorks = async () => {
  try {
    const res = await api.get('/writing', { params: { page: 1, per_page: 5 } })
    recentWorks.value = res.data.data || []
    recentDraft.value = recentWorks.value.find(w => w.status === 'draft')
  } catch (error) {
    console.error('Failed to load recent works:', error)
  }
}

const loadGrowthChart = async () => {
  try {
    const res = await api.get('/ranking/my-growth-curve', { params: { days: 30 } })
    const data = res.data.data.growth_data.average_score

    if (data.length > 0 && chartContainer.value) {
      const chart = echarts.init(chartContainer.value)
      chart.setOption({
        tooltip: {
          trigger: 'axis'
        },
        xAxis: {
          type: 'category',
          data: data.map(d => d.date.slice(5)) // MM-DD
        },
        yAxis: {
          type: 'value',
          min: 60,
          max: 100
        },
        series: [{
          data: data.map(d => d.value),
          type: 'line',
          smooth: true,
          lineStyle: {
            color: '#16a34a',
            width: 3
          },
          itemStyle: {
            color: '#16a34a'
          },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(22, 163, 74, 0.3)' },
              { offset: 1, color: 'rgba(22, 163, 74, 0)' }
            ])
          }
        }]
      })
    }
  } catch (error) {
    console.error('Failed to load growth chart:', error)
  }
}

onMounted(() => {
  loadStats()
  loadRecentWorks()
  loadGrowthChart()
})
</script>
