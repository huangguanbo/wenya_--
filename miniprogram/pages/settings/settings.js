const app = getApp()
const api = require('../../utils/api')
const util = require('../../utils/util')

Page({
  data: {
    type: '',
    user: {},
    version: '1.0.0',
    icpNumber: '',
    algorithmNumber: '',
    feedbackContent: '',
    contactInfo: ''
  },

  onLoad(options) {
    const user = app.globalData.user || wx.getStorageSync('user') || {}
    this.setData({
      type: options.type || '',
      user: {
        ...user,
        grade_name: util.gradeName(user.grade)
      }
    })

    this.loadCompliance()
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

  editProfile() {
    wx.showModal({
      title: '修改昵称',
      editable: true,
      placeholderText: this.data.user.nickname || '请输入昵称（最多 32 字）',
      content: '请输入新的昵称（最多 32 字）',
      success: async (res) => {
        if (!res.confirm) return

        const nickname = (res.content || '').trim()
        if (!nickname) {
          util.showError('昵称不能为空')
          return
        }

        try {
          const response = await api.put('/auth/profile', { nickname })
          const user = (response.data && response.data.user) || {}
          this.saveUser(user)
          util.showSuccess('已更新')
        } catch (error) {
          util.showError(error.message || '更新失败')
        }
      }
    })
  },

  changeGrade() {
    const stages = ['小学', '初中', '高中']
    const ranges = [[1, 6], [7, 9], [10, 12]]

    wx.showActionSheet({
      itemList: stages,
      success: (stageRes) => {
        const [start, end] = ranges[stageRes.tapIndex]
        const grades = []
        for (let i = start; i <= end; i += 1) {
          grades.push(util.gradeName(i))
        }

        wx.showActionSheet({
          itemList: grades,
          success: (gradeRes) => {
            this.saveGrade(start + gradeRes.tapIndex)
          }
        })
      }
    })
  },

  async saveGrade(grade) {
    try {
      const response = await api.put('/auth/profile', { grade })
      const user = (response.data && response.data.user) || {}
      this.saveUser(user)
      util.showSuccess(`已切换为${util.gradeName(grade)}`)
    } catch (error) {
      util.showError(error.message || '更新失败')
    }
  },

  saveUser(user) {
    app.globalData.user = user
    wx.setStorageSync('user', user)

    this.setData({
      user: {
        ...user,
        grade_name: util.gradeName(user.grade)
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

  submitFeedback() {
    util.showError('反馈功能暂未开放')
  }
})