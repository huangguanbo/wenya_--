const app = getApp()
const auth = require('../../utils/auth')
const api = require('../../utils/api')
const util = require('../../utils/util')

Page({
  data: {
    hasUserInfo: false,
    userInfo: null,
    wxCode: '',
    username: '',
    nickname: '',
    gradeOptions: ['小学一年级', '小学二年级', '小学三年级', '小学四年级', '小学五年级', '小学六年级', '初中一年级', '初中二年级', '初中三年级', '高中一年级', '高中二年级', '高中三年级'],
    gradeIndex: -1,
    guardianPhone: '',
    code: '',
    codeText: '获取验证码',
    canSendCode: true,
    agreed: false
  },

  countdownTimer: null,

  onLoad(options) {
    // 从微信登录跳转过来
    if (options.code) {
      this.setData({ wxCode: options.code })
    }
  },

  onUnload() {
    if (this.countdownTimer) {
      clearInterval(this.countdownTimer)
    }
  },

  get canRegister() {
    return this.data.username.length >= 3 &&
           this.data.nickname.trim() &&
           this.data.gradeIndex >= 0 &&
           util.validatePhone(this.data.guardianPhone) &&
           this.data.code.length >= 4 &&
           this.data.agreed
  },

  async getUserInfo() {
    try {
      const userProfile = await auth.wxPromise('getUserProfile', {
        lang: 'zh_CN'
      })
      
      this.setData({
        hasUserInfo: true,
        userInfo: userProfile.userInfo,
        nickname: userProfile.userInfo.nickName
      })
    } catch (error) {
      util.showError('获取用户信息失败')
    }
  },

  onUsernameInput(e) {
    this.setData({
      username: e.detail.value
    })
  },

  onNicknameInput(e) {
    this.setData({
      nickname: e.detail.value
    })
  },

  onGradeChange(e) {
    this.setData({
      gradeIndex: e.detail.value
    })
  },

  onGuardianPhoneInput(e) {
    this.setData({
      guardianPhone: e.detail.value
    })
  },

  onCodeInput(e) {
    this.setData({
      code: e.detail.value
    })
  },

  onAgreementChange(e) {
    this.setData({
      agreed: e.detail.value.length > 0
    })
  },

  async sendCode() {
    if (!util.validatePhone(this.data.guardianPhone)) {
      util.showError('请输入正确的手机号')
      return
    }

    this.setData({ canSendCode: false })
    
    try {
      await api.post('/auth/send-code', {
        phone: this.data.guardianPhone
      })
      
      util.showSuccess('验证码已发送')
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

  async register() {
    if (!this.canRegister) {
      util.showError('请填写完整的注册信息')
      return
    }

    util.showLoading('注册中...')
    
    try {
      const userData = {
        username: this.data.username,
        nickname: this.data.nickname,
        grade: this.data.gradeOptions[this.data.gradeIndex],
        guardian: {
          phone: this.data.guardianPhone,
          verification_code: this.data.code
        }
      }

      // 如果有微信信息，一并提交
      if (this.data.userInfo) {
        userData.avatar = this.data.userInfo.avatarUrl
        userData.gender = this.data.userInfo.gender
      }

      const res = await api.post('/auth/register', userData)
      
      if (res.data) {
        // 保存登录状态
        wx.setStorageSync('token', res.data.token)
        wx.setStorageSync('user', res.data.user)
        app.globalData.token = res.data.token
        app.globalData.user = res.data.user
        
        util.hideLoading()
        util.showSuccess('注册成功')
        
        // 跳转到首页
        wx.switchTab({
          url: '/pages/index/index'
        })
      }
    } catch (error) {
      util.hideLoading()
      util.showError(error.message || '注册失败')
    }
  },

  goToLogin() {
    wx.navigateBack()
  },

  showAgreement() {
    wx.navigateTo({
      url: '/pages/settings/settings?type=agreement'
    })
  }
})
