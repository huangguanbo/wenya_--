const app = getApp()
const api = require('../../utils/api')
const util = require('../../utils/util')

Page({
  data: {
    work: {},
    dimensions: [],
    isCommunity: false
  },

  onLoad(options) {
    this.setData({
      isCommunity: options.type === 'community'
    })
    
    if (options.id) {
      this.loadWork(options.id)
    }
  },

  async loadWork(id) {
    util.showLoading()
    
    try {
      const endpoint = this.data.isCommunity 
        ? `/community/works/${id}`
        : `/writing/${id}`
      
      const res = await api.get(endpoint)
      const work = res.data || {}
      
      // 处理评分维度
      const dimensions = []
      const scoreDetails = work.score_details || {}
      
      const dimensionMap = {
        'task_completion': '任务完成',
        'theme': '主题立意',
        'content': '内容充实',
        'structure': '结构逻辑',
        'language': '语言表达',
        'style': '文体规范',
        'thinking': '思维深度'
      }
      
      Object.keys(dimensionMap).forEach(key => {
        const score = scoreDetails[key] || 0
        dimensions.push({
          name: dimensionMap[key],
          score: score.toFixed(1),
          percent: (score / 100) * 100
        })
      })
      
      this.setData({
        work: {
          ...work,
          created_at: util.formatDate(work.created_at, 'YYYY-MM-DD HH:mm')
        },
        dimensions
      })
    } catch (error) {
      console.error('加载作文详情失败:', error)
      util.showError('加载失败')
    } finally {
      util.hideLoading()
    }
  },

  continueEdit() {
    wx.navigateTo({
      url: `/pages/writing/writing?id=${this.data.work.id}`
    })
  },

  async shareWork() {
    if (!this.data.work.overall_score) {
      util.showError('请先提交评分后再分享')
      return
    }
    
    // 生成分享海报或小程序卡片
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
