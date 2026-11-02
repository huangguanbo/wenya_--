const app = getApp()
const auth = require('../../utils/auth')
const util = require('../../utils/util')

Page({
  data: {
    logging: false
  },

  onLoad() {
    if (app.globalData.token) {
      wx.switchTab({
        url: '/pages/index/index'
      })
    }
  },

  async wechatLogin() {
    if (this.data.logging) return

    this.setData({ logging: true })
    util.showLoading('登录中...')

    try {
      const data = await auth.login()

      app.globalData.token = data.token
      app.globalData.user = data.user

      util.hideLoading()
      util.showSuccess('登录成功')

      wx.switchTab({
        url: '/pages/index/index'
      })
    } catch (error) {
      util.hideLoading()
      util.showError(error.message || '登录失败')
    } finally {
      this.setData({ logging: false })
    }
  },

  showUserAgreement() {
    wx.navigateTo({
      url: '/pages/settings/settings?type=agreement'
    })
  },

  showPrivacyPolicy() {
    wx.navigateTo({
      url: '/pages/settings/settings?type=privacy'
    })
  }
})