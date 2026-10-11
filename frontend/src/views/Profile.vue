<template>
  <div class="space-y-6">
    <h1 class="text-2xl font-bold text-gray-900">👤 个人中心</h1>

    <!-- 基本信息 -->
    <div class="bg-white rounded-lg shadow p-6">
      <h2 class="text-lg font-bold text-gray-900 mb-4">基本信息</h2>
      <div class="flex items-center space-x-4 mb-6">
        <div v-if="userStore.user?.avatar_url" class="w-20 h-20 rounded-full overflow-hidden">
          <img :src="userStore.user.avatar_url" alt="头像" class="w-full h-full object-cover" />
        </div>
        <div v-else class="w-20 h-20 rounded-full bg-green-500 flex items-center justify-center text-white text-2xl font-bold">
          {{ userStore.user?.nickname?.[0] || userStore.user?.username?.[0] || 'U' }}
        </div>
        <div>
          <div class="text-xl font-bold text-gray-900">
            {{ userStore.user?.nickname || userStore.user?.username }}
          </div>
          <div class="text-sm text-gray-500">
            {{ getSchoolStage(userStore.user?.school_stage) }}{{ userStore.user?.grade }}年级
          </div>
        </div>
      </div>
    </div>

    <!-- 写作画像 -->
    <div class="bg-white rounded-lg shadow p-6">
      <h2 class="text-lg font-bold text-gray-900 mb-4">📊 写作画像</h2>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <!-- 雷达图 -->
        <div ref="radarChart" class="h-64"></div>

        <!-- 标签云 -->
        <div class="space-y-4">
          <div>
            <h3 class="text-sm font-medium text-gray-700 mb-2">✨ 优势标签</h3>
            <div class="flex flex-wrap gap-2">
              <span
                v-for="tag in profile?.strength_tags || []"
                :key="tag"
                class="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm"
              >
                {{ tag }}
              </span>
              <span v-if="!profile?.strength_tags?.length" class="text-sm text-gray-500">
                暂无数据
              </span>
            </div>
          </div>

          <div>
            <h3 class="text-sm font-medium text-gray-700 mb-2">🌱 需要改进</h3>
            <div class="flex flex-wrap gap-2">
              <span
                v-for="tag in profile?.weakness_tags || []"
                :key="tag"
                class="px-3 py-1 bg-amber-100 text-amber-700 rounded-full text-sm"
              >
                {{ tag }}
              </span>
              <span v-if="!profile?.weakness_tags?.length" class="text-sm text-gray-500">
                暂无数据
              </span>
            </div>
          </div>

          <div>
            <h3 class="text-sm font-medium text-gray-700 mb-2">📚 偏好文体</h3>
            <div class="flex flex-wrap gap-2">
              <span
                v-for="genre in profile?.preferred_genres || []"
                :key="genre"
                class="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm"
              >
                {{ genre }}
              </span>
              <span v-if="!profile?.preferred_genres?.length" class="text-sm text-gray-500">
                暂无数据
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 统计数据 -->
    <div class="bg-white rounded-lg shadow p-6">
      <h2 class="text-lg font-bold text-gray-900 mb-4">📈 写作统计</h2>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div class="text-center">
          <div class="text-2xl font-bold text-gray-900">{{ profile?.total_writings || 0 }}</div>
          <div class="text-sm text-gray-500">总写作数</div>
        </div>
        <div class="text-center">
          <div class="text-2xl font-bold text-green-600">{{ profile?.average_score?.toFixed(1) || 0 }}</div>
          <div class="text-sm text-gray-500">平均分</div>
        </div>
        <div class="text-center">
          <div class="text-2xl font-bold text-green-600">{{ profile?.best_score?.toFixed(1) || 0 }}</div>
          <div class="text-sm text-gray-500">最高分</div>
        </div>
        <div class="text-center">
          <div class="text-2xl font-bold text-amber-600">{{ profile?.consecutive_days || 0 }}</div>
          <div class="text-sm text-gray-500">连续天数</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useUserStore } from '@/stores/user'
import api from '@/api'
import * as echarts from 'echarts'

const userStore = useUserStore()
const radarChart = ref(null)
const profile = ref(null)

const getSchoolStage = (stage) => {
  const stages = {
    elementary: '小学',
    middle: '初中',
    high: '高中'
  }
  return stages[stage] || ''
}

const loadProfile = async () => {
  try {
    const res = await api.get('/stats')
    profile.value = res.data.data.profile
    await initRadarChart()
  } catch (error) {
    console.error('Failed to load profile:', error)
  }
}

const initRadarChart = async () => {
  if (!radarChart.value || !profile.value?.dimension_scores) return

  const scores = profile.value.dimension_scores
  const chart = echarts.init(radarChart.value)

  chart.setOption({
    tooltip: {},
    radar: {
      indicator: [
        { name: '立意', max: 100 },
        { name: '内容', max: 100 },
        { name: '结构', max: 100 },
        { name: '语言', max: 100 },
        { name: '创意', max: 100 }
      ],
      radius: '65%'
    },
    series: [{
      name: '写作能力',
      type: 'radar',
      data: [
        {
          value: [
            scores.theme || 0,
            scores.content || 0,
            scores.structure || 0,
            scores.language || 0,
            scores.creativity || 0
          ],
          name: '当前水平',
          areaStyle: {
            color: 'rgba(22, 163, 74, 0.3)'
          },
          lineStyle: {
            color: '#16a34a'
          },
          itemStyle: {
            color: '#16a34a'
          }
        }
      ]
    }]
  })
}

watch(() => profile.value, initRadarChart)
onMounted(loadProfile)
</script>
