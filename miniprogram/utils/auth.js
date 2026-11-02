/**
 * 认证工具函数
 */
const api = require('./api')

/**
 * 微信一键登录
 */
async function login() {
  let code

  try {
    const res = await wxPromise('login')
    code = res.code
  } catch (error) {
    throw new Error(error.errMsg || '微信登录失败')
  }

  if (!code) {
    throw new Error('微信登录失败')
  }

  const res = await api.post('/auth/wx-login', { code })
  const data = res.data || {}

  if (!data.token || !data.user) {
    throw new Error(res.message || '登录失败')
  }

  wx.setStorageSync('token', data.token)
  wx.setStorageSync('user', data.user)

  return data
}

/**
 * 获取当前用户信息
 */
async function fetchCurrentUser() {
  const res = await api.get('/auth/me')
  const user = (res.data && res.data.user) || null

  if (user) {
    wx.setStorageSync('user', user)
  }

  return user
}

/**
 * 退出登录
 */
async function logout() {
  try {
    await api.post('/auth/logout')
  } catch (error) {
    // 本地登录态仍需清理
  }

  wx.removeStorageSync('token')
  wx.removeStorageSync('user')
  wx.removeStorageSync('wenya_session_cookie')
  wx.reLaunch({
    url: '/pages/login/login'
  })
}

/**
 * 检查登录状态
 */
function checkLogin() {
  const token = wx.getStorageSync('token')
  return !!token
}

/**
 * 获取当前用户
 */
function getCurrentUser() {
  return wx.getStorageSync('user')
}

/**
 * wx 原生 API Promise 化
 */
function wxPromise(apiName, options = {}) {
  return new Promise((resolve, reject) => {
    wx[apiName]({
      ...options,
      success: resolve,
      fail: reject
    })
  })
}

module.exports = {
  login,
  logout,
  checkLogin,
  getCurrentUser,
  fetchCurrentUser,
  wxPromise
}