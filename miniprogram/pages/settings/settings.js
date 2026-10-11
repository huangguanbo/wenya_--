const app = getApp()
const api = require('../../utils/api')
const util = require('../../utils/util')

Page({
  data: {
    type: '',
    user: {},
    version: '1.0.0',
    icpNumber: '京 ICP 备 XXXXXXXX 号',
    algorithmNumber: '算法备案编号',
    feedbackContent: '',
    contactInfo: ''
  },

  onLoad(options) {
    this.setData({
      type: options.type || '',
      user: app.globalData.user || {}
    })
  },

  editProfile() {
    wx.navigateTo({
      url: '/pages/settings/profile-edit'
    })
  },

  changeGrade() {
    const grades = ['小学', '初中', '高中']
    wx.showActionSheet({
      itemList: grades,
      success: (res) => {
        // TODO: 调用 API 更新年级
        util.showSuccess(`已切换为${grades[res.tapIndex]}`)
      }
    })
  },

  onFeedbackInput(e) {
    this.setData({
      feedbackContent: e.detail.value
    })
  },

  onContactInput(e) {
    this.setData({
      contactInfo: e.detail.value
    })
  },

  async submitFeedback() {
    if (!this.data.feedbackContent.trim()) {
      util.showError('请输入反馈内容')
      return
    }

    util.showLoading('提交中...')
    
    try {
      await api.post('/feedback', {
        content: this.data.feedbackContent,
        contact: this.data.contactInfo
      })
      
      util.hideLoading()
      util.showSuccess('反馈已提交')
      
      this.setData({
        feedbackContent: '',
        contactInfo: ''
      })
      
      setTimeout(() => {
        wx.navigateBack()
      }, 1500)
    } catch (error) {
      util.hideLoading()
      util.showError('提交失败')
    }
  }
})
