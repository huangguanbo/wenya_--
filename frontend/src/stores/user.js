import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/api'

export const useUserStore = defineStore('user', () => {
  const user = ref(null)

  const isAuthenticated = computed(() => !!user.value)

  const fetchUser = async () => {
    try {
      const res = await api.get('/auth/me')
      user.value = res.data.data
    } catch (error) {
      user.value = null
    }
  }

  const login = async (credentials) => {
    const res = await api.post('/auth/login', credentials)
    user.value = res.data.data.user
    return res.data.data
  }

  const register = async (userData) => {
    const res = await api.post('/auth/register', userData)
    user.value = res.data.data.user
    return res.data.data
  }

  const logout = async () => {
    try {
      await api.post('/auth/logout')
    } catch (e) {
      // ignore
    }
    user.value = null
  }

  const init = async () => {
    if (!user.value) {
      await fetchUser()
    }
  }

  return {
    user,
    isAuthenticated,
    fetchUser,
    login,
    register,
    logout,
    init
  }
})
