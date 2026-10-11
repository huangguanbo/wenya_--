/**
 * 通用工具函数
 */

/**
 * 格式化日期
 */
function formatDate(dateStr, format = 'YYYY-MM-DD') {
  if (!dateStr) return '-'
  
  const date = new Date(dateStr)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  
  if (format === 'YYYY-MM-DD') {
    return `${year}-${month}-${day}`
  } else if (format === 'MM-DD') {
    return `${month}-${day}`
  } else if (format === 'HH:mm') {
    return `${hours}:${minutes}`
  } else if (format === 'full') {
    return `${year}-${month}-${day} ${hours}:${minutes}`
  }
  
  return `${year}-${month}-${day}`
}

/**
 * 格式化相对时间
 */
function formatRelativeTime(dateStr) {
  if (!dateStr) return ''
  
  const now = new Date()
  const date = new Date(dateStr)
  const diff = now - date
  
  const seconds = Math.floor(diff / 1000)
  const minutes = Math.floor(seconds / 60)
  const hours = Math.floor(minutes / 60)
  const days = Math.floor(hours / 24)
  const weeks = Math.floor(days / 7)
  
  if (seconds < 60) {
    return '刚刚'
  } else if (minutes < 60) {
    return `${minutes}分钟前`
  } else if (hours < 24) {
    return `${hours}小时前`
  } else if (days < 7) {
    return `${days}天前`
  } else if (weeks < 4) {
    return `${weeks}周前`
  } else {
    return formatDate(dateStr)
  }
}

/**
 * 格式化数字（超过 1 万显示为 1.2 万）
 */
function formatNumber(num) {
  if (num >= 10000) {
    return (num / 10000).toFixed(1) + '万'
  }
  return num.toString()
}

/**
 * 防抖函数
 */
function debounce(fn, delay = 300) {
  let timer = null
  return function(...args) {
    if (timer) clearTimeout(timer)
    timer = setTimeout(() => {
      fn.apply(this, args)
    }, delay)
  }
}

/**
 * 节流函数
 */
function throttle(fn, delay = 300) {
  let lastTime = 0
  return function(...args) {
    const now = Date.now()
    if (now - lastTime >= delay) {
      fn.apply(this, args)
      lastTime = now
    }
  }
}

/**
 * 深拷贝
 */
function deepClone(obj) {
  if (obj === null || typeof obj !== 'object') return obj
  if (obj instanceof Date) return new Date(obj)
  if (obj instanceof Array) return obj.map(item => deepClone(item))
  if (obj instanceof Object) {
    const copy = {}
    Object.keys(obj).forEach(key => {
      copy[key] = deepClone(obj[key])
    })
    return copy
  }
  return obj
}

/**
 * 验证手机号
 */
function validatePhone(phone) {
  return /^1[3-9]\d{9}$/.test(phone)
}

/**
 * 验证身份证号
 */
function validateIdCard(idCard) {
  return /(^\d{15}$)|(^\d{18}$)|(^\d{17}(\d|X|x)$)/.test(idCard)
}

/**
 * 生成随机 ID
 */
function generateId() {
  return Math.random().toString(36).substr(2) + Date.now().toString(36)
}

/**
 * 显示加载提示
 */
function showLoading(title = '加载中...') {
  wx.showLoading({
    title: title,
    mask: true
  })
}

/**
 * 隐藏加载提示
 */
function hideLoading() {
  wx.hideLoading()
}

/**
 * 显示成功提示
 */
function showSuccess(title) {
  wx.showToast({
    title: title,
    icon: 'success'
  })
}

/**
 * 显示错误提示
 */
function showError(title) {
  wx.showToast({
    title: title,
    icon: 'none'
  })
}

/**
 * 页面跳转封装
 */
function navigateTo(url) {
  wx.navigateTo({ url })
}

function redirectTo(url) {
  wx.redirectTo({ url })
}

function switchTab(url) {
  wx.switchTab({ url })
}

function navigateBack(delta = 1) {
  wx.navigateBack({ delta })
}

module.exports = {
  formatDate,
  formatRelativeTime,
  formatNumber,
  debounce,
  throttle,
  deepClone,
  validatePhone,
  validateIdCard,
  generateId,
  showLoading,
  hideLoading,
  showSuccess,
  showError,
  navigateTo,
  redirectTo,
  switchTab,
  navigateBack
}
