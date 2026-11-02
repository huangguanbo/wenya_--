const app = getApp()
const api = require('../../utils/api')
const util = require('../../utils/util')

const DIMENSIONS = [
  { key: 'task_score', name: '任务完成' },
  { key: 'theme_score', name: '主题立意' },
  { key: 'content_score', name: '内容充实' },
  { key: 'structure_score', name: '结构逻辑' },
  { key: 'language_score', name: '语言表达' },
  { key: 'genre_score', name: '文体规范' },
  { key: 'thinking_score', name: '思维深度' }
]

Page({
  data: {
    work: {},
    dimensions: [],
    isCommunity: false
  },

  onLoad(options) {
    const isCommunity = options.type === 'community'
    this.setData({ isCommunity })

    if (!options.id) {
      util.showError('缺少作品 ID')
      return
    }

    this.loadWork(options.id)
  },

  async loadWork(id) {
    util.showLoading()

    try {
      const endpoint = this.data.isCommunity
        ? `/community/works/${id}`
        : `/writing/${id}`

      const res = await api.get(endpoint)
      const work = (res.data && (res.data.work || res.data.writing)) || {}
      const scores = work.scores || work.dimension_scores || {}

      const dimensions = DIMENSIONS.map(item => {
        const score = scores[item.key] || 0
        return {
          name: item.name,
          score: score.toFixed(1),
          percent: score
        }
      })

      this.setData({
        work: {
          ...work,
          ai_comment: scores.ai_comment || '',
          suggestions: scores.ai_suggestions || [],
          created_at: util.formatDate(work.published_at || work.created_at, 'full')
        },
        dimensions
      })
    } catch (error) {
      console.error('加载作品详情失败:', error)
      util.showError(error.message || '加载失败')
    } finally {
      util.hideLoading()
    }
  },

  continueEdit() {
    wx.navigateTo({
      url: `/pages/writing/writing?id=${this.data.work.id}`
    })
  },

  shareWork() {
    if (!this.data.work.overall_score) {
      util.showError('请先提交评分后再分享')
      return
    }

    wx.showShareMenu({
      withShareTicket: true,
      menus: ['shareAppMessage', 'shareTimeline']
    })

    util.showSuccess('点击右上角分享')
  },

  onShareAppMessage() {
    return {
      title: `来看看我的作文《${this.data.work.title}》`,
      path: `/pages/writing-detail/writing-detail?id=${this.data.work.id}&type=community`
    }
  }
})