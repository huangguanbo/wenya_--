/**
 * 认证工具函数
 *
 * 后端只提供账号密码登录/注册，没有微信登录接口，因此用「设备级微信身份」
 * 静默换取账号：首次使用自动注册，之后复用同一账号登录，用户无需填写任何信息。
 */
const api = require('./api')
const session = require('./session')
const config = require('./config')

const UID_KEY = 'wenya_wx_uid'
const USER_KEY = 'user'

let loginTask = null

function randomHex(length) {
  const chars = '0123456789abcdef'
  let result = ''
  for (let i = 0; i < length; i += 1) {
    result += chars.charAt(Math.floor(Math.random() * chars.length))
  }
  return result
}

function getOrCreateUid() {
  let uid = wx.getStorageSync(UID_KEY)
  if (!uid) {
    uid = randomHex(24)
    wx.setStorageSync(UID_KEY, uid)
  }
  return uid
}

/**
 * 由设备身份推导后端账号，保证同一设备每次登录得到同一账号
 */
function buildIdentity() {
  const uid = getOrCreateUid()
  return {
    uid,
    username: `wx_${uid.slice(0, 20)}`,
    password: `${config.WX_PASSWORD_PREFIX}${uid.slice(0, 12)}9`
  }
}

function buildRegisterPayload(identity) {
  return {
    username: identity.username,
    password: identity.password,
    grade: config.WX_DEFAULT_GRADE,
    guardian_name: config.WX_DEFAULT_GUARDIAN_NAME,
    guardian_relationship: config.WX_DEFAULT_GUARDIAN_RELATIONSHIP
  }
}

function cacheUser(user) {
  if (user) {
    wx.setStorageSync(USER_KEY, user)
  }
  return user
}

function getCachedUser() {
  return wx.getStorageSync(USER_KEY) || null
}

function isLoggedIn() {
  return !!getCachedUser()
}

async function doLogin(identity) {
  const res = await api.post('/auth/login', {
    username: identity.username,
    password: identity.password,
    remember: true
  }, { silent: true, skipAuthHandler: true })

  const user = res.data && res.data.user
  if (!user) {
    throw new Error('登录失败')
  }
  return cacheUser(user)
}

async function doRegister(identity) {
  const res = await api.post('/auth/register', buildRegisterPayload(identity), {
    silent: true,
    skipAuthHandler: true
  })

  const user = res.data && res.data.user
  if (!user) {
    throw new Error('注册失败')
  }
  return cacheUser(user)
}

/**
 * 静默登录：账号不存在时自动注册，并发调用共用同一个登录任务
 */
function silentLogin() {
  if (loginTask) {
    return loginTask
  }

  const identity = buildIdentity()

  loginTask = (async () => {
    try {
      return await doLogin(identity)
    } catch (error) {
      if (error.statusCode !== 401) {
        throw error
      }
    }

    try {
      return await doRegister(identity)
    } catch (error) {
      // 账号已存在（例如注册重试）时直接登录
      if (error.statusCode === 409) {
        return doLogin(identity)
      }
      throw error
    }
  })()

  loginTask.then(() => {
    loginTask = null
  }, () => {
    loginTask = null
  })

  return loginTask
}

/**
 * 用户点击「微信一键登录」时调用
 */
async function login() {
  return silentLogin()
}

/**
 * 恢复本地会话；会话失效时自动重新登录
 */
async function ensureSession() {
  const cached = getCachedUser()

  if (session.hasSession()) {
    try {
      const res = await api.get('/auth/me', null, { silent: true, skipAuthHandler: true })
      const user = res.data && res.data.user
      if (user) {
        return cacheUser(user)
      }
    } catch (error) {
      if (error.statusCode !== 401) {
        return cached
      }
    }
  }

  // 没有本地登录记录时不做静默注册，交给用户在登录页确认
  if (!cached) {
    return null
  }

  try {
    return await silentLogin()
  } catch (error) {
    return null
  }
}

/**
 * 获取当前用户信息
 */
async function fetchCurrentUser() {
  const res = await api.get('/auth/me')
  const user = (res.data && res.data.user) || null

  if (user) {
    cacheUser(user)
  }

  return user
}

/**
 * 退出登录
 */
async function logout() {
  try {
    await api.post('/auth/logout', null, { silent: true, skipAuthHandler: true })
  } catch (error) {
    // 本地登录态仍需清理
  }

  wx.removeStorageSync(USER_KEY)
  session.clear()

  if (typeof getApp === 'function') {
    const app = getApp()
    if (app && app.globalData) {
      app.globalData.user = null
    }
  }

  wx.reLaunch({
    url: '/pages/login/login'
  })
}

/**
 * 检查登录状态
 */
function checkLogin() {
  return isLoggedIn()
}

/**
 * 获取当前用户
 */
function getCurrentUser() {
  return getCachedUser()
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
  silentLogin,
  ensureSession,
  logout,
  checkLogin,
  isLoggedIn,
  getCurrentUser,
  getCachedUser,
  fetchCurrentUser,
  wxPromise
}