<template>
  <div class="space-y-6">
    <h1 class="text-2xl font-bold text-gray-900">⚙️ 设置</h1>

    <!-- 隐私设置 -->
    <div class="bg-white rounded-lg shadow p-6">
      <h2 class="text-lg font-bold text-gray-900 mb-4">🔒 隐私设置</h2>
      <div class="space-y-4">
        <div class="flex justify-between items-center">
          <div>
            <div class="font-medium text-gray-900">在排行榜中显示</div>
            <div class="text-sm text-gray-500">开启后你的成绩将出现在排行榜中</div>
          </div>
          <button
            @click="toggleRankingVisibility"
            :class="[
              'relative inline-flex h-6 w-11 items-center rounded-full transition-colors',
              showInRanking ? 'bg-green-600' : 'bg-gray-200'
            ]"
          >
            <span
              :class="[
                'inline-block h-4 w-4 transform rounded-full bg-white transition',
                showInRanking ? 'translate-x-6' : 'translate-x-1'
              ]"
            />
          </button>
        </div>

        <div class="flex justify-between items-center">
          <div>
            <div class="font-medium text-gray-900">公开展示作品</div>
            <div class="text-sm text-gray-500">开启后你的作品将出现在社区中</div>
          </div>
          <button
            @click="togglePublicWorks"
            :class="[
              'relative inline-flex h-6 w-11 items-center rounded-full transition-colors',
              showPublicWorks ? 'bg-green-600' : 'bg-gray-200'
            ]"
          >
            <span
              :class="[
                'inline-block h-4 w-4 transform rounded-full bg-white transition',
                showPublicWorks ? 'translate-x-6' : 'translate-x-1'
              ]"
            />
          </button>
        </div>
      </div>
    </div>

    <!-- 监护人信息 -->
    <div class="bg-white rounded-lg shadow p-6">
      <h2 class="text-lg font-bold text-gray-900 mb-4">👨‍👩‍👧 监护人信息</h2>
      <div v-if="guardianInfo" class="space-y-2">
        <div class="flex justify-between">
          <span class="text-gray-500">监护人姓名</span>
          <span class="text-gray-900">{{ guardianInfo.name }}</span>
        </div>
        <div class="flex justify-between">
          <span class="text-gray-500">关系</span>
          <span class="text-gray-900">{{ guardianInfo.relationship }}</span>
        </div>
        <div class="flex justify-between">
          <span class="text-gray-500">验证状态</span>
          <span :class="guardianInfo.is_verified ? 'text-green-600' : 'text-amber-600'">
            {{ guardianInfo.is_verified ? '已验证' : '未验证' }}
          </span>
        </div>
      </div>
      <button
        @click="updateGuardian"
        class="mt-4 px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 text-sm"
      >
        更新监护人信息
      </button>
    </div>

    <!-- 合规信息 -->
    <div class="bg-white rounded-lg shadow p-6">
      <h2 class="text-lg font-bold text-gray-900 mb-4">📋 合规信息</h2>
      <div class="space-y-3 text-sm">
        <div class="flex justify-between">
          <span class="text-gray-500">ICP 备案</span>
          <span class="text-gray-900">{{ complianceInfo.icp_number || '未公示' }}</span>
        </div>
        <div class="flex justify-between">
          <span class="text-gray-500">算法备案</span>
          <span class="text-gray-900">{{ complianceInfo.algorithm_number || '未公示' }}</span>
        </div>
      </div>
      <div class="mt-4 flex space-x-4">
        <a :href="complianceInfo.privacy_policy_url" target="_blank"
           class="text-green-600 hover:text-green-700 text-sm">
          隐私政策
        </a>
        <a :href="complianceInfo.terms_of_service_url" target="_blank"
           class="text-green-600 hover:text-green-700 text-sm">
          服务条款
        </a>
      </div>
    </div>

    <!-- 账号安全 -->
    <div class="bg-white rounded-lg shadow p-6">
      <h2 class="text-lg font-bold text-gray-900 mb-4">🛡️ 账号安全</h2>
      <button
        @click="changePassword"
        class="w-full px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 text-sm mb-3"
      >
        修改密码
      </button>
      <button
        @click="deleteAccount"
        class="w-full px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 text-sm"
      >
        注销账号
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import api from '@/api'

const userStore = useUserStore()

const showInRanking = ref(true)
const showPublicWorks = ref(true)
const guardianInfo = ref(null)
const complianceInfo = ref({
  icp_number: '',
  algorithm_number: '',
  privacy_policy_url: '',
  terms_of_service_url: ''
})

const loadSettings = async () => {
  try {
    const userRes = await api.get('/auth/me')
    showInRanking.value = userRes.data.user.show_in_ranking
    showPublicWorks.value = userRes.data.user.show_works_publicly

    const complianceRes = await api.get('/compliance/info')
    complianceInfo.value = complianceRes.data
  } catch (error) {
    console.error('Failed to load settings:', error)
  }
}

const toggleRankingVisibility = async () => {
  try {
    await api.post('/ranking/toggle-visibility', { show: !showInRanking.value })
    showInRanking.value = !showInRanking.value
    userStore.user.show_in_ranking = showInRanking.value
  } catch (error) {
    console.error('Failed to toggle ranking visibility:', error)
  }
}

const togglePublicWorks = async () => {
  showPublicWorks.value = !showPublicWorks.value
  // TODO: API 实现
}

const updateGuardian = () => {
  alert('此功能开发中')
}

const changePassword = () => {
  alert('此功能开发中')
}

const deleteAccount = async () => {
  if (!confirm('确定要注销账号吗？此操作不可恢复。')) return
  // TODO: API 实现
}

onMounted(loadSettings)
</script>
