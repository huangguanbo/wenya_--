<template>
  <div class="space-y-6">
    <div v-if="work" class="bg-white rounded-lg shadow overflow-hidden">
      <!-- 头部 -->
      <div class="border-b p-6">
        <h1 class="text-2xl font-bold text-gray-900 mb-2">{{ work.title }}</h1>
        <div class="flex items-center space-x-4 text-sm text-gray-500">
          <span>📚 {{ work.author_school_stage }}{{ work.author_grade }}年级</span>
          <span>✏️ {{ work.word_count }}字</span>
          <span>📅 {{ new Date(work.published_at).toLocaleDateString('zh-CN') }}</span>
        </div>
      </div>

      <!-- 内容 -->
      <div class="p-6">
        <div class="prose max-w-none">
          <p class="whitespace-pre-wrap text-gray-800 leading-relaxed">
            {{ work.content }}
          </p>
        </div>
      </div>

      <!-- 评分 -->
      <div v-if="work.dimension_scores" class="border-t p-6 bg-gray-50">
        <h2 class="text-lg font-bold text-gray-900 mb-4">📊 AI 评分</h2>
        <div class="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
          <div v-for="(score, key) in work.dimension_scores" :key="key"
               class="text-center p-3 bg-white rounded-lg shadow">
            <div class="text-2xl font-bold text-green-600">
              {{ typeof score === 'number' ? score.toFixed(0) : '-' }}
            </div>
            <div class="text-xs text-gray-500 mt-1">
              {{ getDimensionLabel(key) }}
            </div>
          </div>
        </div>
        <div v-if="work.dimension_scores.ai_comment" class="bg-white rounded-lg p-4">
          <h3 class="font-medium text-gray-900 mb-2">总体评语</h3>
          <p class="text-gray-600 text-sm">{{ work.dimension_scores.ai_comment }}</p>
        </div>
      </div>

      <!-- 互动 -->
      <div class="border-t p-6">
        <div class="flex justify-between items-center mb-6">
          <div class="flex space-x-6">
            <button
              @click="toggleLike"
              :class="['flex items-center space-x-2 text-sm',
                       isLiked ? 'text-red-600' : 'text-gray-500']"
            >
              <span>{{ isLiked ? '❤️' : '🤍' }}</span>
              <span>{{ work.like_count }}</span>
            </button>
            <div class="flex items-center space-x-2 text-sm text-gray-500">
              <span>💬</span>
              <span>{{ work.comment_count }}</span>
            </div>
            <div class="flex items-center space-x-2 text-sm text-gray-500">
              <span>👁</span>
              <span>{{ work.view_count }}</span>
            </div>
          </div>
        </div>

        <!-- 评论区 -->
        <div class="space-y-4">
          <h3 class="font-bold text-gray-900">评论</h3>
          
          <!-- 发表评论 -->
          <div class="flex space-x-2">
            <input
              v-model="commentContent"
              type="text"
              placeholder="写下你的评论..."
              class="flex-1 px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 text-sm"
            />
            <button
              @click="postComment"
              :disabled="!commentContent.trim()"
              class="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 text-sm"
            >
              发布
            </button>
          </div>

          <!-- 评论列表 -->
          <div class="space-y-3">
            <div v-for="comment in comments" :key="comment.id"
                 class="p-3 bg-gray-50 rounded-lg">
              <div class="flex justify-between items-start mb-2">
                <div class="text-sm font-medium text-gray-900">
                  用户 #{{ comment.user_id }}
                </div>
                <div class="text-xs text-gray-500">
                  {{ new Date(comment.created_at).toLocaleString('zh-CN') }}
                </div>
              </div>
              <p class="text-sm text-gray-700">{{ comment.content }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="text-center py-12">
      <p class="text-gray-500">作品不存在</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '@/api'

const route = useRoute()
const work = ref(null)
const isLiked = ref(false)
const comments = ref([])
const commentContent = ref('')

const getDimensionLabel = (key) => {
  const labels = {
    theme_score: '立意',
    content_score: '内容',
    structure_score: '结构',
    language_score: '语言',
    thinking_score: '创意',
    ai_comment: '评语'
  }
  return labels[key] || key
}

const loadWork = async () => {
  try {
    const res = await api.get(`/community/works/${route.params.id}`)
    work.value = res.data.data.work
    isLiked.value = res.data.data.is_liked
  } catch (error) {
    console.error('Failed to load work:', error)
  }
}

const loadComments = async () => {
  try {
    const res = await api.get(`/community/works/${route.params.id}/comments`)
    comments.value = res.data.data.comments || []
  } catch (error) {
    console.error('Failed to load comments:', error)
  }
}

const toggleLike = async () => {
  try {
    const res = await api.post(`/community/works/${route.params.id}/like`)
    isLiked.value = res.data.data.is_liked
    work.value.like_count = res.data.data.like_count
  } catch (error) {
    console.error('Failed to toggle like:', error)
  }
}

const postComment = async () => {
  if (!commentContent.value.trim()) return
  
  try {
    const res = await api.post(`/community/works/${route.params.id}/comment`, {
      content: commentContent.value.trim()
    })
    comments.value.push(res.data.data.comment)
    work.value.comment_count++
    commentContent.value = ''
  } catch (error) {
    console.error('Failed to post comment:', error)
  }
}

onMounted(() => {
  loadWork()
  loadComments()
})
</script>
