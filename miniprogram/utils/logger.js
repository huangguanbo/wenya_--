/**
 * 运行日志工具
 * 只记录错误 (error) 和警告 (warning) 级别的日志
 * 支持本地存储和自动上报
 */
const config = require('./config')

// 日志级别常量
const LOG_LEVEL = {
  ERROR: 'error',
  WARNING: 'warning'
}

// 日志存储键名
const STORAGE_KEY = 'wenya_runtime_logs'

// 最大存储条数（超过后自动清理旧日志）
const MAX_LOG_COUNT = 100

// 日志上报开关（生产环境可开启）
const ENABLE_REPORT = false

// 日志上报地址（可选）
const REPORT_URL = '/api/log/upload'

/**
 * 获取日志存储
 */
function getStoredLogs() {
  try {
    const logs = wx.getStorageSync(STORAGE_KEY)
    return logs ? JSON.parse(logs) : []
  } catch (error) {
    console.error('读取日志存储失败', error)
    return []
  }
}

/**
 * 保存日志到存储
 */
function saveToStorage(logs) {
  try {
    // 限制存储数量
    if (logs.length > MAX_LOG_COUNT) {
      logs = logs.slice(logs.length - MAX_LOG_COUNT)
    }
    wx.setStorageSync(STORAGE_KEY, JSON.stringify(logs))
  } catch (error) {
    // 存储失败时不递归记录日志，避免死循环
    console.error('保存日志失败', error)
  }
}

/**
 * 格式化日志数据
 */
function formatLog(level, message, data = {}) {
  const now = new Date()
  return {
    id: generateId(),
    level,
    message,
    data,
    timestamp: now.toISOString(),
    timestampLocal: now.toLocaleString('zh-CN'),
    page: getCurrentPage(),
    platform: wx.getSystemInfoSync().platform,
    system: wx.getSystemInfoSync().system,
    version: config.VERSION
  }
}

/**
 * 生成唯一 ID
 */
function generateId() {
  return 'log_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9)
}

/**
 * 获取当前页面路径
 */
function getCurrentPage() {
  const pages = getCurrentPages()
  if (pages.length === 0) return 'unknown'
  const currentPage = pages[pages.length - 1]
  return currentPage.route || 'unknown'
}

/**
 * 记录错误日志
 * @param {string} message - 错误信息
 * @param {object} data - 附加数据（可选）
 */
function error(message, data = {}) {
  const log = formatLog(LOG_LEVEL.ERROR, message, data)
  
  // 控制台输出（开发环境）
  if (config.DEBUG) {
    console.error(`[ERROR] ${log.timestampLocal} - ${log.page}`, message, data)
  }
  
  // 保存到本地存储
  const logs = getStoredLogs()
  logs.push(log)
  saveToStorage(logs)
  
  // 可选：上报到服务器
  if (ENABLE_REPORT && !config.DEBUG) {
    reportLog(log)
  }
  
  return log
}

/**
 * 记录警告日志
 * @param {string} message - 警告信息
 * @param {object} data - 附加数据（可选）
 */
function warning(message, data = {}) {
  const log = formatLog(LOG_LEVEL.WARNING, message, data)
  
  // 控制台输出（开发环境）
  if (config.DEBUG) {
    console.warn(`[WARNING] ${log.timestampLocal} - ${log.page}`, message, data)
  }
  
  // 保存到本地存储
  const logs = getStoredLogs()
  logs.push(log)
  saveToStorage(logs)
  
  // 可选：上报到服务器
  if (ENABLE_REPORT && !config.DEBUG) {
    reportLog(log)
  }
  
  return log
}

/**
 * 上报日志到服务器
 */
async function reportLog(log) {
  try {
    const token = wx.getStorageSync('token')
    wx.request({
      url: config.API_BASE_URL + REPORT_URL,
      method: 'POST',
      data: { logs: [log] },
      header: {
        'Authorization': token ? `Bearer ${token}` : ''
      },
      timeout: 5000
    })
  } catch (error) {
    // 上报失败不再记录，避免死循环
    console.error('日志上报失败', error)
  }
}

/**
 * 批量上报日志
 */
async function reportLogs() {
  const logs = getStoredLogs()
  if (logs.length === 0) return
  
  try {
    const token = wx.getStorageSync('token')
    wx.request({
      url: config.API_BASE_URL + REPORT_URL,
      method: 'POST',
      data: { logs },
      header: {
        'Authorization': token ? `Bearer ${token}` : ''
      },
      timeout: 10000,
      success: () => {
        // 上报成功后清空本地存储
        wx.removeStorageSync(STORAGE_KEY)
      }
    })
  } catch (error) {
    console.error('批量日志上报失败', error)
  }
}

/**
 * 获取存储的日志列表
 * @param {number} limit - 返回数量限制
 */
function getLogs(limit = 50) {
  const logs = getStoredLogs()
  // 按时间倒序返回
  return logs.reverse().slice(0, limit)
}

/**
 * 清空日志存储
 */
function clearLogs() {
  wx.removeStorageSync(STORAGE_KEY)
}

/**
 * 导出日志为文本
 */
function exportLogs() {
  const logs = getLogs(1000)
  const text = logs.map(log => 
    `[${log.level.toUpperCase()}] ${log.timestampLocal} - ${log.page}\n` +
    `  Message: ${log.message}\n` +
    `  Data: ${JSON.stringify(log.data, null, 2)}\n`
  ).join('\n---\n\n')
  
  return text
}

/**
 * 全局错误监听
 */
function setupGlobalErrorHandler() {
  // 监听小程序页面渲染错误
  wx.onError && wx.onError((error) => {
    error('全局错误监听', {
      type: 'app_error',
      error: error.message || error.errMsg,
      stack: error.stack
    })
  })
  
  // 监听未处理的 Promise 拒绝
  wx.onUnhandledRejection && wx.onUnhandledRejection((event) => {
    error('未处理的 Promise 拒绝', {
      type: 'unhandled_rejection',
      reason: event.reason,
      promise: event.promise
    })
  })
}

module.exports = {
  LOG_LEVEL,
  error,
  warning,
  getLogs,
  clearLogs,
  exportLogs,
  reportLogs,
  setupGlobalErrorHandler
}
