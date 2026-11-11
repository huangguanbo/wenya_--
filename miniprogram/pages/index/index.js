const app = getApp()
const api = require('../../utils/api')
const auth = require('../../utils/auth')
const util = require('../../utils/util')

Page({
  data: {
    nickname: '',
    stats: [
      { label: '总写作数', value: 0 },
      { label: '平均分', value: 0 },
      { label: '最高分', value: 0 },
      { label: '连续天数', value: 0 }
    ],
    recentDraft: null,
    recentWorks: [],
    chartData: []
  },

  onLoad() {
    this.loadUserData()
  },

  onShow() {
    if (!app.isLoggedIn()) {
      wx.reLaunch({
        url: '/pages/login/login'
      })
      return
    }
    this.loadUserData()
  },

  async loadUserData() {
    await this.loadProfile()

    await Promise.all([
      this.loadStats(),
      this.loadRecentWorks(),
      this.loadGrowthChart()
    ])
  },

  async loadProfile() {
    try {
      const user = await auth.fetchCurrentUser()
      if (user) {
        app.globalData.user = user
        this.setData({
          nickname: user.nickname || user.username
        })
      }
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
        stats: [
          { label: '总写作数', value: data.total_writings || 0 },
          { label: '平均分', value: (data.average_score || 0).toFixed(1) },
          { label: '最高分', value: (data.best_score || 0).toFixed(1) },
          { label: '连续天数', value: profile.consecutive_days || 0 }
        ]
      })
    } catch (error) {
      console.error('加载统计数据失败:', error)
    }
  },

  async loadRecentWorks() {
    try {
      const res = await api.get('/writing', { page: 1, per_page: 5 })
      const works = res.data || []
      const recentDraft = works.find(w => w.status === 'draft')

      this.setData({
        recentWorks: works.map(w => ({
          ...w,
          created_at: util.formatDate(w.created_at, 'MM-DD'),
          updated_at: util.formatDate(w.updated_at, 'MM-DD')
        })),
        recentDraft: recentDraft ? {
          ...recentDraft,
          updated_at: util.formatDate(recentDraft.updated_at, 'MM-DD')
        } : null
      })
    } catch (error) {
      console.error('加载最近作品失败:', error)
    }
  },

  async loadGrowthChart() {
    try {
      const res = await api.get('/ranking/my-growth-curve', { days: 30 })
      const growthData = (res.data && res.data.growth_data && res.data.growth_data.average_score) || []

      this.setData({
        chartData: growthData.map(d => ({
          date: d.date.slice(5),
          value: d.value
        }))
      })
    } catch (error) {
      console.error('加载成长曲线失败:', error)
    }
  },

  goToWriting() {
    // writing 是 tabBar 页面，只能使用 switchTab
    app.globalData.writingIntent = { action: 'new' }
    wx.switchTab({
      url: '/pages/writing/writing'
    })
  },

  continueWriting() {
    if (this.data.recentDraft) {
      app.globalData.writingIntent = {
        action: 'edit',
        id: this.data.recentDraft.id
      }
      wx.switchTab({
        url: '/pages/writing/writing'
      })
    }
  },

  viewAll() {
    wx.showToast({
      title: '作品列表页暂未开放',
      icon: 'none'
    })
  },

  goToWorkDetail(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({
      url: `/pages/writing-detail/writing-detail?id=${id}`
    })
  },

  async onPullDownRefresh() {
    await this.loadUserData()
    wx.stopPullDownRefresh()
  }
})