const app = getApp()
const api = require('../../utils/api')
const util = require('../../utils/util')

Page({
  data: {
    currentTab: 'overall',
    dimensions: [
      { label: '任务完成', value: 'task_completion' },
      { label: '主题立意', value: 'theme' },
      { label: '内容充实', value: 'content' },
      { label: '结构逻辑', value: 'structure' },
      { label: '语言表达', value: 'language' },
      { label: '文体规范', value: 'style' },
      { label: '思维深度', value: 'thinking' }
    ],
    dimensionIndex: 0,
    rankingList: [],
    myRank: null,
    loading: false
  },

  onLoad() {
    this.loadRanking()
  },

  onShow() {
    // 每次显示时刷新数据
    this.loadRanking()
  },

  async loadRanking() {
    this.setData({ loading: true })
    
    try {
      let endpoint = '/ranking/overall'
      
      if (this.data.currentTab === 'progress') {
        endpoint = '/ranking/progress'
      } else if (this.data.currentTab === 'dimension') {
        const dim = this.data.dimensions[this.data.dimensionIndex].value
        endpoint = `/ranking/dimension/${dim}`
      }
      
      const res = await api.get(endpoint)
      const data = res.data || []
      
      this.setData({
        rankingList: data.map((item, index) => ({
          ...item,
          rank: index + 1,
          avatar: item.avatar || '/images/default-avatar.png',
          score: currentTab === 'progress' ? item.progress_score : item.score
        }))
      })
      
      // 加载我的排名
      this.loadMyRank()
    } catch (error) {
      console.error('加载排行榜失败:', error)
      util.showError('加载失败')
    } finally {
      this.setData({ loading: false })
    }
  },

  async loadMyRank() {
    try {
      const res = await api.get('/ranking/my-rank')
      this.setData({
        myRank: res.data
      })
    } catch (error) {
      console.error('加载我的排名失败:', error)
    }
  },

  switchTab(e) {
    const type = e.currentTarget.dataset.type
    this.setData({
      currentTab: type,
      rankingList: [],
      myRank: null
    }, () => {
      this.loadRanking()
    })
  },

  onDimensionChange(e) {
    const index = e.detail.value
    this.setData({
      dimensionIndex: index
    }, () => {
      this.loadRanking()
    })
  },

  onPullDownRefresh() {
    this.loadRanking().then(() => {
      wx.stopPullDownRefresh()
    })
  }
})
