<template>
  <div class="space-y-6">
    <!-- 页面标题 -->
    <div class="flex justify-between items-center">
      <h1 class="text-2xl font-bold text-gray-900">📚 作品社区</h1>
    </div>

    <!-- 筛选器 -->
    <div class="bg-white rounded-lg shadow p-4">
      <div class="flex flex-wrap gap-4">
        <select
          v-model="filters.school_stage"
          @change="loadWorks"
          class="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
        >
          <option value="">全部学段</option>
          <option value="elementary">小学</option>
          <option value="middle">初中</option>
          <option value="high">高中</option>
        </select>

        <select
          v-model="filters.genre"
          @change="loadWorks"
          class="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
        >
          <option value="">全部文体</option>
          <option value="记叙文">记叙文</option>
          <option value="议论文">议论文</option>
          <option value="说明文">说明文</option>
          <option value="散文">散文</option>
          <option value="诗歌">诗歌</option>
        </select>

        <input
          v-model="searchQuery"
          @keyup.enter="loadWorks"
          type="text"
          placeholder="搜索标题..."
          class="flex-1 min-w-[200px] px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
        />
      </div>
    </div>

    <!-- 作品网格 -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div
        v-for="work in works"
        :key="work.id"
        @click="$router.push(`/community/${work.id}`)"
        class="bg-white rounded-lg shadow hover:shadow-lg transition cursor-pointer overflow-hidden"
      >
        <!-- 卡片头部 -->
        <div class="p-4 border-b">
          <div class="flex justify-between items-start">
            <h3 class="font-bold text-gray-900 truncate flex-1">{{ work.title }}</h3>
            <span
              v-if="work.is_featured"
              class="ml-2 px-2 py-1 text-xs bg-yellow-100 text-yellow-800 rounded"
            >
              精选
            </span>
          </div>
          <div class="mt-2 text-sm text-gray-500">
            {{ work.author_school_stage }}{{ work.author_grade }}年级
          </div>
        </div>

        <!-- 卡片内容 -->
        <div class="p-4">
          <p class="text-gray-600 text-sm line-clamp-3 h-16">
            {{ work.content?.substring(0, 100) || '' }}...
          </p>
        </div>

        <!-- 卡片底部 -->
        <div class="px-4 py-3 bg-gray-50 flex justify-between items-center text-sm text-gray-500">
          <div class="flex space-x-4">
            <span>👍 {{ work.like_count }}</span>
            <span>💬 {{ work.comment_count }}</span>
            <span>👁 {{ work.view_count }}</span>
          </div>
          <div v-if="work.overall_score" class="font-bold text-green-600">
            {{ work.overall_score.toFixed(1) }}分
          </div>
        </div>
      </div>
    </div>

    <!-- 加载更多 -->
    <div v-if="hasMore" class="text-center">
      <button
        @click="loadMore"
        :disabled="loading"
        class="px-6 py-2 bg-white border border-gray-300 rounded-md text-sm hover:bg-gray-50 disabled:opacity-50"
      >
        {{ loading ? '加载中...' : '加载更多' }}
      </button>
    </div>

    <!-- 空状态 -->
    <div v-if="!loading && works.length === 0" class="text-center py-12">
      <div class="text-6xl mb-4">📭</div>
      <p class="text-gray-500">暂无作品</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api'

const works = ref([])
const loading = ref(false)
const page = ref(1)
const hasMore = ref(true)
const searchQuery = ref('')

const filters = ref({
  school_stage: '',
  genre: ''
})

const loadWorks = async (reset = true) => {
  if (loading.value) return

  if (reset) {
    page.value = 1
    works.value = []
  }

  loading.value = true
  try {
    const params = {
      page: page.value,
      per_page: 12,
      ...filters.value
    }

    const res = await api.get('/community/works', { params })
    const newWorks = res.data.data || []

    if (reset) {
      works.value = newWorks
    } else {
      works.value = [...works.value, ...newWorks]
    }

    hasMore.value = res.data.pagination ? page.value < res.data.pagination.pages : false
  } catch (error) {
    console.error('Failed to load works:', error)
  } finally {
    loading.value = false
  }
}

const loadMore = () => {
  page.value++
  loadWorks(false)
}

onMounted(() => {
  loadWorks()
})
</script>

<style scoped>
.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
