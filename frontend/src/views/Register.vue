<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-2xl w-full space-y-8">
      <div>
        <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
          注册文芽
        </h2>
        <p class="mt-2 text-center text-sm text-gray-600">
          开启 AI 陪伴的写作成长之旅
        </p>
      </div>

      <form class="mt-8 space-y-6" @submit.prevent="handleRegister">
        <!-- 用户信息 -->
        <div class="space-y-4">
          <div>
            <label for="username" class="block text-sm font-medium text-gray-700">用户名</label>
            <input
              id="username"
              v-model="form.username"
              type="text"
              required
              class="mt-1 appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm"
              placeholder="至少 3 个字符"
            />
          </div>

          <div>
            <label for="password" class="block text-sm font-medium text-gray-700">密码</label>
            <input
              id="password"
              v-model="form.password"
              type="password"
              required
              class="mt-1 appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm"
              placeholder="至少 6 个字符"
            />
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label for="grade" class="block text-sm font-medium text-gray-700">年级</label>
              <select
                id="grade"
                v-model="form.grade"
                required
                class="mt-1 appearance-none relative block w-full px-3 py-2 border border-gray-300 text-gray-900 rounded-md focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm"
              >
                <option v-for="n in 12" :key="n" :value="n">{{ n }}年级</option>
              </select>
            </div>

            <div>
              <label for="birth_date" class="block text-sm font-medium text-gray-700">出生日期</label>
              <input
                id="birth_date"
                v-model="form.birth_date"
                type="date"
                class="mt-1 appearance-none relative block w-full px-3 py-2 border border-gray-300 text-gray-900 rounded-md focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm"
              />
            </div>
          </div>
        </div>

        <!-- 监护人信息 -->
        <div class="border-t pt-6 space-y-4">
          <h3 class="text-lg font-medium text-gray-900">监护人信息</h3>
          <p class="text-xs text-gray-500">根据法律要求，未成年人注册需要监护人同意</p>

          <div>
            <label for="guardian_name" class="block text-sm font-medium text-gray-700">监护人姓名</label>
            <input
              id="guardian_name"
              v-model="form.guardian_name"
              type="text"
              required
              class="mt-1 appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm"
            />
          </div>

          <div>
            <label for="guardian_phone" class="block text-sm font-medium text-gray-700">监护人手机号</label>
            <div class="flex space-x-2">
              <input
                id="guardian_phone"
                v-model="form.guardian_phone"
                type="tel"
                required
                class="flex-1 appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm"
                placeholder="11 位手机号"
              />
              <button
                type="button"
                @click="sendCode"
                :disabled="sendingCode || countdown > 0"
                class="px-4 py-2 border border-transparent text-sm font-medium rounded-md text-green-600 bg-green-100 hover:bg-green-200 focus:outline-none disabled:opacity-50"
              >
                {{ countdown > 0 ? `${countdown}s` : '获取验证码' }}
              </button>
            </div>
          </div>

          <div>
            <label for="verification_code" class="block text-sm font-medium text-gray-700">验证码</label>
            <input
              id="verification_code"
              v-model="form.guardian_verification_code"
              type="text"
              required
              maxlength="6"
              class="mt-1 appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm"
              placeholder="6 位数字验证码"
            />
          </div>

          <div>
            <label for="guardian_relationship" class="block text-sm font-medium text-gray-700">与监护人关系</label>
            <select
              id="guardian_relationship"
              v-model="form.guardian_relationship"
              required
              class="mt-1 appearance-none relative block w-full px-3 py-2 border border-gray-300 text-gray-900 rounded-md focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm"
            >
              <option value="">请选择</option>
              <option value="父子">父子</option>
              <option value="母子">母子</option>
              <option value="父女">父女</option>
              <option value="母女">母女</option>
              <option value="其他">其他</option>
            </select>
          </div>
        </div>

        <div>
          <button
            type="submit"
            :disabled="loading"
            class="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span v-if="loading" class="absolute left-0 inset-y-0 flex items-center pl-3">
              <svg class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            </span>
            {{ loading ? '注册中...' : '注册' }}
          </button>
        </div>

        <div v-if="error" class="p-4 bg-red-50 border border-red-200 rounded-md">
          <p class="text-sm text-red-600">{{ error }}</p>
        </div>

        <div class="text-center">
          <router-link to="/login" class="font-medium text-green-600 hover:text-green-500">
            已有账号？立即登录
          </router-link>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import api from '@/api'

const router = useRouter()
const userStore = useUserStore()

const form = ref({
  username: '',
  password: '',
  grade: 1,
  birth_date: '',
  guardian_name: '',
  guardian_phone: '',
  guardian_relationship: '',
  guardian_verification_code: ''
})

const loading = ref(false)
const error = ref('')
const sendingCode = ref(false)
const countdown = ref(0)

const sendCode = async () => {
  if (!form.value.guardian_phone) {
    error.value = '请先输入监护人手机号'
    return
  }

  sendingCode.value = true
  try {
    await api.post('/auth/send-guardian-code', {
      phone: form.value.guardian_phone
    })
    countdown.value = 60
    const timer = setInterval(() => {
      countdown.value--
      if (countdown.value <= 0) {
        clearInterval(timer)
      }
    }, 1000)
  } catch (err) {
    error.value = err.response?.data?.error || '发送验证码失败'
  } finally {
    sendingCode.value = false
  }
}

const handleRegister = async () => {
  loading.value = true
  error.value = ''

  try {
    await userStore.register(form.value)
    router.push('/')
  } catch (err) {
    error.value = err.response?.data?.error || '注册失败'
  } finally {
    loading.value = false
  }
}
</script>
