const logger = require('./utils/logger')

App({
  onLaunch() {
    // 初始化全局错误监听
    logger.setupGlobalErrorHandler()
    
    // 记录启动日志
    logger.warning('小程序启动', {
      scene: this.$options?.scene || 'unknown'
    })
    
    // 初始化登录状态
    this.initLogin()
    
    // 尝试上报未发送的日志
    logger.reportLogs()
  },

  onShow() {
    // 记录前台切换日志
    logger.warning('小程序进入前台', {
      from: this.$options?.scene || 'unknown'
    })
  },

  onHide() {
    // 记录后台切换日志
    logger.warning('小程序进入后台')
  },

  initLogin() {
    try {
      const token = wx.getStorageSync('token')
      const user = wx.getStorageSync('user')

      if (token && user) {
        this.globalData.token = token
        this.globalData.user = user
      }
    } catch (error) {
      logger.error('初始化登录状态失败', {
        error: error.message || error
      })
    }
  },

  checkLogin() {
    try {
      const token = wx.getStorageSync('token')
      if (!token) {
        wx.navigateTo({
          url: '/pages/login/login'
        })
        return false
      }
      return true
    } catch (error) {
      logger.error('检查登录状态失败', {
        error: error.message || error
      })
      return false
    }
  },

  globalData: {
    token: '',
    user: null,
    API_BASE_URL: ''
  }
})
