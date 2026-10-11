/**
 * API 请求封装
 */
const config = require('./config')
const logger = require('./logger')

// 获取存储的 token
function getToken() {
  return wx.getStorageSync('token') || ''
}

// 统一处理请求
function request(options) {
  return new Promise((resolve, reject) => {
    const token = getToken()
    
    wx.request({
      url: config.API_BASE_URL + options.url,
      method: options.method || 'GET',
      data: options.data || {},
      header: {
        'Content-Type': 'application/json',
        'Authorization': token ? `Bearer ${token}` : ''
      },
      timeout: config.TIMEOUT,
      success: (res) => {
        // 统一处理响应
        if (res.statusCode === 200 && res.data) {
          // 业务错误处理
          if (res.data.code !== undefined && res.data.code !== 0) {
            logger.warning('API 业务错误', {
              url: options.url,
              method: options.method,
              code: res.data.code,
              message: res.data.message || res.data.error
            })
            wx.showToast({
              title: res.data.message || '请求失败',
              icon: 'none'
            })
            reject(res.data)
          } else {
            resolve(res.data)
          }
        } else if (res.statusCode === 401) {
          // 未授权，清除登录状态
          logger.warning('API 请求未授权', {
            url: options.url,
            method: options.method
          })
          wx.removeStorageSync('token')
          wx.removeStorageSync('user')
          wx.reLaunch({
            url: '/pages/login/login'
          })
          reject(res.data)
        } else {
          logger.warning('API 响应异常', {
            url: options.url,
            method: options.method,
            statusCode: res.statusCode
          })
          reject(res.data)
        }
      },
      fail: (err) => {
        logger.error('API 请求失败', {
          url: options.url,
          method: options.method,
          errMsg: err.errMsg || '网络错误'
        })
        wx.showToast({
          title: err.errMsg || '网络错误',
          icon: 'none'
        })
        reject(err)
      }
    })
  })
}

// GET 请求
function get(url, data) {
  return request({ url, method: 'GET', data })
}

// POST 请求
function post(url, data) {
  return request({ url, method: 'POST', data })
}

// PUT 请求
function put(url, data) {
  return request({ url, method: 'PUT', data })
}

// DELETE 请求
function del(url, data) {
  return request({ url, method: 'DELETE', data })
}

// 文件上传
function uploadFile(url, filePath, formData = {}) {
  const token = getToken()
  
  return new Promise((resolve, reject) => {
    wx.uploadFile({
      url: config.API_BASE_URL + url,
      filePath: filePath,
      name: 'file',
      formData: formData,
      header: {
        'Authorization': token ? `Bearer ${token}` : ''
      },
      success: (res) => {
        const data = JSON.parse(res.data)
        if (data.code === 0) {
          resolve(data)
        } else {
          reject(data)
        }
      },
      fail: (err) => {
        reject(err)
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
