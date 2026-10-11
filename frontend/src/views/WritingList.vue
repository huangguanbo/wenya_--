<template>
  <div class="space-y-6">
    <h1 class="text-2xl font-bold text-gray-900">📚 我的作文</h1>
    
    <!-- 筛选 -->
    <div class="flex space-x-4">
      <button
        v-for="status in statuses"
        :key="status.value"
        @click="currentStatus = status.value; loadWritings()"
        :class="[
          'px-4 py-2 rounded-md text-sm font-medium',
          currentStatus === status.value
            ? 'bg-green-600 text-white'
            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
        ]"
      >
        {{ status.label }}
      </button>
    </div>

    <!-- 列表 -->
    <div class="bg-white rounded-lg shadow divide-y">
      <div
        v-for="writing in writings"
        :key="writing.id"
        @click="$router.push(`/writing/${writing.id}`)"
        class="p-4 hover:bg-gray-50 cursor-pointer transition"
      >
        <div class="flex justify-between items-start">
          <div class="flex-1">
            <h3 class="font-medium text-gray-900">{{ writing.title }}</h3>
            <p class="text-sm text-gray-500 mt-1">
              {{ writing.word_count }}字 · {{ new Date(writing.created_at).toLocaleDateString('zh-CN') }}
            </p>
          </div>
          <div class="text-right">
            <div v-if="writing.overall_score" class="text-2xl font-bold text-green-600">
              {{ writing.overall_score.toFixed(1) }}
            </div>
            <span
              :class="[
                'px-2 py-1 text-xs rounded',
                getStatusColor(writing.status)
              ]"
            >
              {{ getStatusLabel(writing.status) }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api'

const statuses = [
  { value: 'all', label: '全部' },
  { value: 'draft', label: '草稿' },
  { value: 'submitted', label: '已提交' }
]

const currentStatus = ref('all')
const writings = ref([])

const loadWritings = async () => {
  try {
    const params = { status: currentStatus.value === 'all' ? 'all' : currentStatus.value }
    const res = await api.get('/writing', { params })
    writings.value = res.data.data || []
  } catch (error) {
    console.error('Failed to load writings:', error)
  }
}

const getStatusColor = (status) => {
  const colors = {
    draft: 'bg-gray-100 text-gray-700',
    submitted: 'bg-blue-100 text-blue-700',
    published: 'bg-green-100 text-green-700'
  }
  return colors[status] || colors.draft
}

const getStatusLabel = (status) => {
  const labels = {
    draft: '草稿',
    submitted: '已评分',
    published: '已发布'
  }
  return labels[status] || status
}

onMounted(loadWritings)
</script>
