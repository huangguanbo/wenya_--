/**
 * 认证工具函数
 */
const api = require('./api')

/**
 * 微信登录 + 后端注册/登录
 */
async function login() {
  return new Promise(async (resolve, reject) => {
    try {
      // 1. 微信登录获取 code
      const loginRes = await wxPromise('login')
      const code = loginRes.code
      
      // 2. 发送到后端换取 token
      const res = await api.post('/auth/wx-login', { code })
      
      // 3. 存储 token 和用户信息
      if (res.data) {
        wx.setStorageSync('token', res.data.token)
        wx.setStorageSync('user', res.data.user)
        resolve(res.data)
      } else {
        reject(res)
      }
    } catch (error) {
      reject(error)
    }
  })
}

/**
 * 手机号验证登录
 */
async function loginWithPhone(phone, verificationCode) {
  try {
    const res = await api.post('/auth/login', {
      phone: phone,
      verification_code: verificationCode
    })
    
    if (res.data) {
      wx.setStorageSync('token', res.data.token)
      wx.setStorageSync('user', res.data.user)
      return res.data
    }
    throw res
  } catch (error) {
    throw error
  }
}

/**
 * 注册（需监护人验证）
 */
async function register(userData) {
  try {
    const res = await api.post('/auth/register', userData)
    return res.data
  } catch (error) {
    throw error
  }
}

/**
 * 退出登录
 */
function logout() {
  wx.removeStorageSync('token')
  wx.removeStorageSync('user')
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

/**
 * 获取手机号（需用户授权）
 */
async function getPhoneNumber() {
  return new Promise((resolve, reject) => {
    // 在需要时调用 wx.getPhoneNumber
    // 注意：2023 年后需要用户主动触发按钮
    reject(new Error('请使用按钮触发获取手机号'))
  })
}

module.exports = {
  login,
  loginWithPhone,
  register,
  logout,
  checkLogin,
  getCurrentUser,
  wxPromise,
  getPhoneNumber
}
