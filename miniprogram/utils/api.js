/**
 * API 请求封装
 */
const config = require('./config')
const logger = require('./logger')
const session = require('./session')

function buildHeader(contentType = 'application/json') {
  return session.buildHeader(contentType)
}

function errorMessage(data, fallback) {
  if (data && typeof data === 'object') {
    return data.message || data.error || fallback
  }
  return fallback
}

function createError(message, extra) {
  const error = new Error(message)
  return Object.assign(error, extra)
}

function handleUnauthorized() {
  wx.removeStorageSync('user')
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

function request(options) {
  return new Promise((resolve, reject) => {
    wx.request({
      url: config.API_BASE_URL + options.url,
      method: options.method || 'GET',
      data: options.data || {},
      header: buildHeader(),
      timeout: config.TIMEOUT,
      success: (res) => {
        session.saveFromHeader(res.header)

        if (res.statusCode >= 200 && res.statusCode < 300 && res.data) {
          if (res.data.code !== undefined && res.data.code !== 0) {
            const message = errorMessage(res.data, '请求失败')
            if (!options.silent) {
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
            }
            reject(createError(message, {
              code: res.data.code,
              statusCode: res.statusCode,
              data: res.data
            }))
            return
          }
          resolve(res.data)
          return
        }

        if (res.statusCode === 401) {
          // 会话失效时先静默重新登录再重试一次，用户无感知
          if (!options.skipAuthHandler && !options.retried) {
            Promise.resolve()
              .then(() => require('./auth').silentLogin())
              .then(() => request(Object.assign({}, options, {
                retried: true,
                skipAuthHandler: true
              })))
              .then(resolve)
              .catch((error) => {
                if (error && error.statusCode === 401) {
                  logger.warning('API 请求未授权', {
                    url: options.url,
                    method: options.method
                  })
                  if (!options.silent) {
                    handleUnauthorized()
                  }
                } else if (!options.silent) {
                  wx.showToast({
                    title: (error && error.message) || '登录失败',
                    icon: 'none'
                  })
                }
                reject(error)
              })
            return
          }

          logger.warning('API 请求未授权', {
            url: options.url,
            method: options.method
          })
          if (!options.silent) {
            handleUnauthorized()
          }
          reject(createError('登录已过期，请重新登录', {
            statusCode: res.statusCode,
            data: res.data
          }))
          return
        }

        const message = errorMessage(res.data, `请求失败（${res.statusCode}）`)
        if (!options.silent) {
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
        }
        reject(createError(message, {
          statusCode: res.statusCode,
          data: res.data
        }))
      },
      fail: (err) => {
        const message = err.errMsg || '网络错误'
        if (!options.silent) {
          logger.error('API 请求失败', {
            url: options.url,
            method: options.method,
            errMsg: message
          })
          wx.showToast({
            title: message,
            icon: 'none'
          })
        }
        reject(createError(message, { errMsg: err.errMsg }))
      }
    })
  })
}

function get(url, data, options) {
  return request(Object.assign({ url, method: 'GET', data }, options))
}

function post(url, data, options) {
  return request(Object.assign({ url, method: 'POST', data }, options))
}

function put(url, data, options) {
  return request(Object.assign({ url, method: 'PUT', data }, options))
}

function del(url, data, options) {
  return request(Object.assign({ url, method: 'DELETE', data }, options))
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
        session.saveFromHeader(res.header)

        let data
        try {
          data = JSON.parse(res.data)
        } catch (error) {
          reject(createError('响应解析失败'))
          return
        }

        if (data.code === 0) {
          resolve(data)
        } else {
          reject(createError(errorMessage(data, '上传失败'), {
            code: data.code,
            statusCode: res.statusCode,
            data
          }))
        }
      },
      fail: (err) => {
        reject(createError(err.errMsg || '网络错误', { errMsg: err.errMsg }))
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