const app = getApp()
const api = require('../../utils/api')
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
    // 每次显示时刷新数据
    if (app.globalData.token) {
      this.loadUserData()
    }
  },

  async loadUserData() {
    try {
      // 获取用户信息
      const user = app.globalData.user
      if (user) {
        this.setData({
          nickname: user.nickname || user.username
        })
      }

      // 并行加载数据
      await Promise.all([
        this.loadStats(),
        this.loadRecentWorks(),
        this.loadGrowthChart()
      ])
    } catch (error) {
      console.error('加载用户数据失败:', error)
    }
  },

  async loadStats() {
    try {
      const res = await api.get('/stats')
      const data = res.data || {}
      
      this.setData({
        stats: [
          { label: '总写作数', value: data.total_writings || 0 },
          { label: '平均分', value: (data.average_score || 0).toFixed(1) },
          { label: '最高分', value: (data.best_score || 0).toFixed(1) },
          { label: '连续天数', value: data.profile?.consecutive_days || 0 }
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
      const growthData = res.data?.growth_data?.average_score || []
      
      if (growthData.length > 0) {
        this.setData({
          chartData: growthData.map(d => ({
            date: d.date.slice(5), // MM-DD
            value: d.value
          }))
        }, () => {
          this.renderChart()
        })
      }
    } catch (error) {
      console.error('加载成长曲线失败:', error)
    }
  },

  renderChart() {
    // 简化版图表渲染 - 实际项目中建议使用 echarts-for-weixin
    // 这里仅示例，实际需要引入 ECharts 组件
    console.log('渲染图表数据:', this.data.chartData)
  },

  goToWriting() {
    wx.navigateTo({
      url: '/pages/writing/writing'
    })
  },

  continueWriting() {
    if (this.data.recentDraft) {
      wx.navigateTo({
        url: `/pages/writing/writing?id=${this.data.recentDraft.id}`
      })
    }
  },

  viewAll() {
    wx.navigateTo({
      url: '/pages/writing-detail/writing-detail'
    })
  },

  goToWorkDetail(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({
      url: `/pages/writing-detail/writing-detail?id=${id}`
    })
  },

  onPullDownRefresh() {
    this.loadUserData().then(() => {
      wx.stopPullDownRefresh()
    })
  }
})
