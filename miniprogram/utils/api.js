/**
 * API 请求封装
 */
const config = require('./config')
const logger = require('./logger')

const COOKIE_KEY = 'wenya_session_cookie'

function getToken() {
  return wx.getStorageSync('token') || ''
}

function getCookie() {
  return wx.getStorageSync(COOKIE_KEY) || ''
}

function saveSessionCookie(header) {
  const raw = header && (header['Set-Cookie'] || header['set-cookie'])
  if (!raw) return

  const cookies = Array.isArray(raw) ? raw : [raw]
  const session = cookies
    .map(item => item.split(';')[0].trim())
    .find(item => item.startsWith('session='))

  if (session) {
    wx.setStorageSync(COOKIE_KEY, session)
  }
}

function buildHeader(contentType = 'application/json') {
  const header = {}
  if (contentType) {
    header['Content-Type'] = contentType
  }

  const token = getToken()
  if (token) {
    header['Authorization'] = `Bearer ${token}`
  }

  const cookie = getCookie()
  if (cookie) {
    header['Cookie'] = cookie
  }

  return header
}

function errorMessage(data, fallback) {
  if (data && typeof data === 'object') {
    return data.message || data.error || fallback
  }
  return fallback
}

function handleUnauthorized() {
  wx.removeStorageSync('token')
  wx.removeStorageSync('user')
  wx.removeStorageSync(COOKIE_KEY)
  wx.reLaunch({
    url: '/pages/login/login'
  })
}

function request(options) {
  return new Promise((resolve, reject) => {
    wx.request({
      url: config.API_BASE_URL + options.url,
      method: options.method || 'GET',
      data: options.data || {},
      header: buildHeader(),
      timeout: config.TIMEOUT,
      success: (res) => {
        saveSessionCookie(res.header)

        if (res.statusCode >= 200 && res.statusCode < 300 && res.data) {
          if (res.data.code !== undefined && res.data.code !== 0) {
            const message = errorMessage(res.data, '请求失败')
            logger.warning('API 业务错误', {
              url: options.url,
              method: options.method,
              code: res.data.code,
              message
            })
            wx.showToast({
              title: message,
              icon: 'none'
            })
            reject(new Error(message))
            return
          }
          resolve(res.data)
          return
        }

        if (res.statusCode === 401) {
          logger.warning('API 请求未授权', {
            url: options.url,
            method: options.method
          })
          handleUnauthorized()
          reject(new Error('登录已过期，请重新登录'))
          return
        }

        const message = errorMessage(res.data, `请求失败（${res.statusCode}）`)
        logger.warning('API 响应异常', {
          url: options.url,
          method: options.method,
          statusCode: res.statusCode,
          message
        })
        wx.showToast({
          title: message,
          icon: 'none'
        })
        reject(new Error(message))
      },
      fail: (err) => {
        const message = err.errMsg || '网络错误'
        logger.error('API 请求失败', {
          url: options.url,
          method: options.method,
          errMsg: message
        })
        wx.showToast({
          title: message,
          icon: 'none'
        })
        reject(new Error(message))
      }
    })
  })
}

function get(url, data) {
  return request({ url, method: 'GET', data })
}

function post(url, data) {
  return request({ url, method: 'POST', data })
}

function put(url, data) {
  return request({ url, method: 'PUT', data })
}

function del(url, data) {
  return request({ url, method: 'DELETE', data })
}

function uploadFile(url, filePath, formData = {}) {
  return new Promise((resolve, reject) => {
    wx.uploadFile({
      url: config.API_BASE_URL + url,
      filePath: filePath,
      name: 'file',
      formData: formData,
      header: buildHeader(null),
      success: (res) => {
        saveSessionCookie(res.header)

        let data
        try {
          data = JSON.parse(res.data)
        } catch (error) {
          reject(new Error('响应解析失败'))
          return
        }

        if (data.code === 0) {
          resolve(data)
        } else {
          reject(new Error(errorMessage(data, '上传失败')))
        }
      },
      fail: (err) => {
        reject(new Error(err.errMsg || '网络错误'))
      }
    })
  })
}

module.exports = {
  get,
  post,
  put,
  delete: del,
  uploadFile
}