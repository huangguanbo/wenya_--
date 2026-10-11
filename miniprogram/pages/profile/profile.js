const app = getApp()
const api = require('../../utils/api')
const auth = require('../../utils/auth')
const util = require('../../utils/util')
const config = require('../../utils/config')

Page({
  data: {
    user: {},
    stats: {
      total_writings: 0,
      average_score: '0.0',
      consecutive_days: 0
    },
    icpNumber: '',
    algorithmNumber: '',
    isDev: false  // 是否开发模式（显示日志入口）
  },

  onLoad() {
    // 判断是否开发模式（开发者或管理员可见日志入口）
    const isDev = config.DEBUG || this.checkIsDeveloper()
    this.setData({ isDev })
    
    this.loadUserData()
  },

  onShow() {
    // 每次显示时刷新数据
    if (app.globalData.token) {
      this.loadUserData()
    }
  },

  /**
   * 检查是否为开发者/管理员
   * 可根据实际角色判断逻辑修改
   */
  checkIsDeveloper() {
    const user = app.globalData.user
    if (!user) return false
    
    // 可配置：根据用户角色判断
    // return user.role === 'admin' || user.role === 'developer'
    
    // 临时：所有用户都可见（上线前建议移除）
    return config.DEBUG
  },

  async loadUserData() {
    try {
      // 获取用户信息
      const user = app.globalData.user || {}
      this.setData({ user })

      // 获取统计数据
      try {
        const res = await api.get('/stats')
        const data = res.data || {}
        
        this.setData({
          stats: {
            total_writings: data.total_writings || 0,
            average_score: (data.average_score || 0).toFixed(1),
            consecutive_days: data.profile?.consecutive_days || 0
          }
        })
      } catch (error) {
        console.error('加载统计数据失败:', error)
      }

      // 获取备案信息
      this.setData({
        icpNumber: '京 ICP 备 XXXXXXXX 号',
        algorithmNumber: '算法备案编号'
      })
    } catch (error) {
      console.error('加载用户数据失败:', error)
    }
  },

  navToPage(e) {
    const page = e.currentTarget.dataset.page
    if (page) {
      wx.navigateTo({ url: page })
    }
  },

  goToSettings() {
    wx.navigateTo({
      url: '/pages/settings/settings'
    })
  },

  logout() {
    wx.showModal({
      title: '退出登录',
      content: '确定要退出登录吗？',
      success: (res) => {
        if (res.confirm) {
          auth.logout()
        }
      }
    })
  }
})
