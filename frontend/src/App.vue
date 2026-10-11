<template>
  <div id="app" class="min-h-screen bg-gray-50">
    <!-- 顶部导航栏 -->
    <header v-if="userStore.isAuthenticated" class="bg-white shadow-sm border-b">
      <nav class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <!-- 左侧：Logo 和导航 -->
          <div class="flex">
            <div class="flex-shrink-0 flex items-center">
              <router-link to="/" class="text-2xl font-bold text-green-600">
                🌱 文芽
              </router-link>
            </div>
            
            <!-- PC 端导航 -->
            <div class="hidden sm:ml-8 sm:flex sm:space-x-8">
              <router-link
                v-for="item in navItems"
                :key="item.path"
                :to="item.path"
                class="inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
                :class="route.path === item.path ? 'border-green-500 text-gray-900' : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'"
              >
                {{ item.name }}
              </router-link>
            </div>
          </div>
          
          <!-- 右侧：用户菜单 -->
          <div class="flex items-center space-x-4">
            <!-- 通知 -->
            <button class="p-2 text-gray-400 hover:text-gray-500">
              <span class="sr-only">通知</span>
              <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"/>
              </svg>
            </button>
            
            <!-- 用户头像 -->
            <div class="relative">
              <button @click="showUserMenu = !showUserMenu" class="flex items-center space-x-2">
                <img
                  v-if="userStore.user?.avatar_url"
                  :src="userStore.user.avatar_url"
                  class="h-8 w-8 rounded-full"
                  alt="头像"
                />
                <div v-else class="h-8 w-8 rounded-full bg-green-500 flex items-center justify-center text-white font-medium">
                  {{ userStore.user?.nickname?.[0] || userStore.user?.username?.[0] || 'U' }}
                </div>
                <span class="hidden md:block text-sm font-medium text-gray-700">
                  {{ userStore.user?.nickname || userStore.user?.username }}
                </span>
              </button>
              
              <!-- 下拉菜单 -->
              <div v-if="showUserMenu" class="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 z-50">
                <router-link to="/profile" class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">
                  个人中心
                </router-link>
                <router-link to="/settings" class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">
                  设置
                </router-link>
                <button
                  @click="handleLogout"
                  class="block w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-gray-100"
                >
                  退出登录
                </button>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 移动端导航 -->
        <div class="sm:hidden pb-4">
          <div class="flex space-x-4">
            <router-link
              v-for="item in navItems"
              :key="item.path"
              :to="item.path"
              class="px-3 py-2 rounded-md text-sm font-medium"
              :class="route.path === item.path ? 'bg-green-50 text-green-700' : 'text-gray-500 hover:bg-gray-50'"
            >
              {{ item.name }}
            </router-link>
          </div>
        </div>
      </nav>
    </header>

    <!-- 主内容区 -->
    <main class="py-6">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </div>
    </main>

    <!-- 底部：合规信息 -->
    <footer class="bg-white border-t mt-12">
      <div class="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        <div class="flex flex-col md:flex-row justify-between items-center space-y-4 md:space-y-0">
          <div class="text-sm text-gray-500">
            © 2024 文芽 - 未成年人 AI 写作练习平台
          </div>
          <div class="flex space-x-6 text-sm text-gray-500">
            <a href="/privacy-policy" class="hover:text-gray-700">隐私政策</a>
            <a href="/terms-of-service" class="hover:text-gray-700">服务条款</a>
            <a v-if="complianceInfo.icp_number" href="https://beian.miit.gov.cn/" target="_blank" class="hover:text-gray-700">
              {{ complianceInfo.icp_number }}
            </a>
          </div>
        </div>
        <div v-if="complianceInfo.algorithm_number" class="mt-4 text-center text-xs text-gray-400">
          算法备案编号：{{ complianceInfo.algorithm_number }}
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import api from '@/api'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const showUserMenu = ref(false)
const complianceInfo = ref({
  icp_number: '',
  algorithm_number: ''
})

const navItems = [
  { name: '首页', path: '/' },
  { name: '写作', path: '/writing' },
  { name: '排行榜', path: '/ranking' },
  { name: '社区', path: '/community' }
]

// 获取合规信息
const fetchComplianceInfo = async () => {
  try {
    const res = await api.get('/compliance/info')
    complianceInfo.value = res.data
  } catch (error) {
    console.error('Failed to fetch compliance info:', error)
  }
}

// 登出
const handleLogout = async () => {
  try {
    await api.post('/auth/logout')
    userStore.logout()
    router.push('/login')
  } catch (error) {
    console.error('Logout failed:', error)
  }
}

onMounted(() => {
  fetchComplianceInfo()
})
</script>

<style>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
