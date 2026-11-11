const logger = require('./utils/logger')
const auth = require('./utils/auth')

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
      const user = auth.getCachedUser()
      if (user) {
        this.globalData.user = user
      }

      // 复用本地会话；会话失效时静默重新登录，用户无感知
      auth.ensureSession().then((currentUser) => {
        if (currentUser) {
          this.globalData.user = currentUser
        }
      }).catch((error) => {
        logger.error('恢复登录态失败', {
          error: error.message || error
        })
      })
    } catch (error) {
      logger.error('初始化登录状态失败', {
        error: error.message || error
      })
    }
  },

  isLoggedIn() {
    return auth.isLoggedIn()
  },

  checkLogin() {
    if (!auth.isLoggedIn()) {
      wx.navigateTo({
        url: '/pages/login/login'
      })
      return false
    }
    return true
  },

  globalData: {
    user: null,
    writingIntent: null,
    API_BASE_URL: ''
  }
})
