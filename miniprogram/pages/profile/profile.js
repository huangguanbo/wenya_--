const app = getApp()
const api = require('../../utils/api')
const auth = require('../../utils/auth')
const util = require('../../utils/util')
const config = require('../../utils/config')

Page({
  data: {
    user: {},
    stats: {
      total_writings: 0,
      average_score: '0.0',
      consecutive_days: 0
    },
    icpNumber: '',
    algorithmNumber: '',
    isDev: false
  },

  onLoad() {
    this.setData({ isDev: config.DEBUG })
    this.loadUserData()
  },

  onShow() {
    if (app.globalData.token) {
      this.loadUserData()
    }
  },

  async loadUserData() {
    await Promise.all([
      this.loadProfile(),
      this.loadStats(),
      this.loadCompliance()
    ])
  },

  async loadProfile() {
    try {
      const user = await auth.fetchCurrentUser()
      if (!user) return

      app.globalData.user = user
      this.setData({
        user: {
          ...user,
          avatar: user.avatar_url || '/images/default-avatar.png',
          grade_name: util.gradeName(user.grade)
        }
      })
    } catch (error) {
      console.error('加载用户信息失败:', error)
    }
  },

  async loadStats() {
    try {
      const res = await api.get('/stats')
      const data = res.data || {}
      const profile = data.profile || {}

      this.setData({
        stats: {
          total_writings: data.total_writings || 0,
          average_score: (data.average_score || 0).toFixed(1),
          consecutive_days: profile.consecutive_days || 0
        }
      })
    } catch (error) {
      console.error('加载统计数据失败:', error)
    }
  },

  async loadCompliance() {
    try {
      const res = await api.get('/compliance/info')
      const data = res.data || {}

      this.setData({
        icpNumber: data.icp_number || '',
        algorithmNumber: data.algorithm_number || ''
      })
    } catch (error) {
      console.error('加载合规信息失败:', error)
    }
  },

  navToPage(e) {
    const page = e.currentTarget.dataset.page
    if (!page) return

    if (page === '/pages/writing-detail/writing-detail') {
      util.showError('作品列表页暂未开放')
      return
    }

    wx.navigateTo({ url: page })
  },

  goToSettings() {
    wx.navigateTo({
      url: '/pages/settings/settings'
    })
  },

  logout() {
    wx.showModal({
      title: '退出登录',
      content: '确定要退出登录吗？',
      success: (res) => {
        if (res.confirm) {
          auth.logout()
        }
      }
    })
  }
})