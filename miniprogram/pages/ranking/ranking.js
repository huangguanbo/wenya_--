const app = getApp()
const api = require('../../utils/api')
const util = require('../../utils/util')

Page({
  data: {
    currentTab: 'overall',
    dimensions: [
      { label: '主题立意', value: 'theme' },
      { label: '内容充实', value: 'content' },
      { label: '结构逻辑', value: 'structure' },
      { label: '语言表达', value: 'language' },
      { label: '思维深度', value: 'creativity' }
    ],
    dimensionIndex: 0,
    rankingList: [],
    restRankings: [],
    myRank: null,
    loading: false
  },

  onLoad() {
    this.loadRanking()
  },

  onShow() {
    this.loadRanking()
  },

  async loadRanking() {
    if (!app.globalData.token) return

    this.setData({ loading: true })

    try {
      let endpoint = '/ranking/overall'
      let scoreField = 'average_score'

      if (this.data.currentTab === 'progress') {
        endpoint = '/ranking/progress'
        scoreField = 'progress_score'
      } else if (this.data.currentTab === 'dimension') {
        const dimension = this.data.dimensions[this.data.dimensionIndex].value
        endpoint = `/ranking/dimension/${dimension}`
        scoreField = 'dimension_score'
      }

      const res = await api.get(endpoint)
      const data = res.data || {}
      const grade = data.grade || (app.globalData.user && app.globalData.user.grade)

      const rankingList = (data.rankings || []).map(item => ({
        ...item,
        avatar: item.avatar_url || '/images/default-avatar.png',
        grade,
        score: item[scoreField] || 0
      }))

      this.setData({
        rankingList,
        restRankings: rankingList.slice(3),
        myRank: this.formatMyRank(data.user_rank, scoreField)
      })
    } catch (error) {
      console.error('加载排行榜失败:', error)
      this.setData({
        rankingList: [],
        restRankings: [],
        myRank: null
      })
    } finally {
      this.setData({ loading: false })
    }
  },

  formatMyRank(userRank, scoreField) {
    if (!userRank) return null

    return {
      rank: userRank.rank_position,
      score: userRank[scoreField] || userRank.average_score || 0,
      percentile: userRank.percentile || 0
    }
  },

  switchTab(e) {
    const type = e.currentTarget.dataset.type
    this.setData({
      currentTab: type,
      rankingList: [],
      restRankings: [],
      myRank: null
    }, () => {
      this.loadRanking()
    })
  },

  onDimensionChange(e) {
    this.setData({
      dimensionIndex: Number(e.detail.value)
    }, () => {
      this.loadRanking()
    })
  },

  async onPullDownRefresh() {
    await this.loadRanking()
    wx.stopPullDownRefresh()
  }
})