const app = getApp()
const auth = require('../../utils/auth')
const api = require('../../utils/api')
const util = require('../../utils/util')

Page({
  data: {
    phone: '',
    code: '',
    codeText: '获取验证码',
    canSendCode: true,
    countdown: 0
  },

  countdownTimer: null,

  onLoad() {
    // 如果已登录，跳转到首页
    if (app.globalData.token) {
      wx.switchTab({
        url: '/pages/index/index'
      })
    }
  },

  onUnload() {
    if (this.countdownTimer) {
      clearInterval(this.countdownTimer)
    }
  },

  onPhoneInput(e) {
    this.setData({
      phone: e.detail.value
    })
  },

  onCodeInput(e) {
    this.setData({
      code: e.detail.value
    })
  },

  get canLogin() {
    return util.validatePhone(this.data.phone) && this.data.code.length >= 4
  },

  async sendCode() {
    if (!util.validatePhone(this.data.phone)) {
      util.showError('请输入正确的手机号')
      return
    }

    this.setData({ canSendCode: false })
    
    try {
      // 发送验证码
      await api.post('/auth/send-code', {
        phone: this.data.phone
      })
      
      util.showSuccess('验证码已发送')
      
      // 开始倒计时
      this.startCountdown(60)
    } catch (error) {
      util.showError('发送失败，请稍后重试')
      this.setData({ canSendCode: true })
    }
  },

  startCountdown(seconds) {
    let remaining = seconds
    
    this.countdownTimer = setInterval(() => {
      remaining--
      
      if (remaining <= 0) {
        clearInterval(this.countdownTimer)
        this.setData({
          codeText: '获取验证码',
          canSendCode: true
        })
      } else {
        this.setData({
          codeText: `${remaining}s 后重发`,
          canSendCode: false
        })
      }
    }, 1000)
  },

  async login() {
    if (!this.canLogin) {
      util.showError('请输入完整的登录信息')
      return
    }

    util.showLoading('登录中...')
    
    try {
      const res = await api.post('/auth/login', {
        phone: this.data.phone,
        verification_code: this.data.code
      })
      
      if (res.data) {
        // 保存登录状态
        wx.setStorageSync('token', res.data.token)
        wx.setStorageSync('user', res.data.user)
        app.globalData.token = res.data.token
        app.globalData.user = res.data.user
        
        util.hideLoading()
        util.showSuccess('登录成功')
        
        // 跳转到首页
        wx.switchTab({
          url: '/pages/index/index'
        })
      }
    } catch (error) {
      util.hideLoading()
      util.showError(error.message || '登录失败')
    }
  },

  async wechatLogin() {
    util.showLoading('登录中...')
    
    try {
      // 微信登录
      const loginRes = await auth.wxPromise('login')
      const code = loginRes.code
      
      // 发送到后端
      const res = await api.post('/auth/wx-login', { code })
      
      if (res.data) {
        // 如果需要补充手机号信息，跳转到绑定页面
        if (!res.data.user.phone) {
          util.hideLoading()
          wx.navigateTo({
            url: `/pages/register/register?code=${code}`
          })
          return
        }
        
        // 保存登录状态
        wx.setStorageSync('token', res.data.token)
        wx.setStorageSync('user', res.data.user)
        app.globalData.token = res.data.token
        app.globalData.user = res.data.user
        
        util.hideLoading()
        util.showSuccess('登录成功')
        
        // 跳转到首页
        wx.switchTab({
          url: '/pages/index/index'
        })
      }
    } catch (error) {
      util.hideLoading()
      util.showError('登录失败')
    }
  },

  goToRegister() {
    wx.navigateTo({
      url: '/pages/register/register'
    })
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
