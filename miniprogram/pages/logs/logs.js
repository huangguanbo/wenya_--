const logger = require('../../utils/logger')
const util = require('../../utils/util')

Page({
  data: {
    logs: [],
    stats: {
      errorCount: 0,
      warningCount: 0,
      totalCount: 0
    },
    showDetails: []
  },

  onLoad() {
    this.loadLogs()
  },

  onShow() {
    // 每次显示时刷新日志
    this.loadLogs()
  },

  loadLogs() {
    const logs = logger.getLogs(100)
    const errorCount = logs.filter(l => l.level === 'error').length
    const warningCount = logs.filter(l => l.level === 'warning').length
    
    this.setData({
      logs,
      showDetails: new Array(logs.length).fill(false),
      stats: {
        errorCount,
        warningCount,
        totalCount: logs.length
      }
    })
  },

  refreshLogs() {
    util.showLoading('刷新中...')
    this.loadLogs()
    setTimeout(() => {
      util.hideLoading()
    }, 500)
  },

  toggleDetail(e) {
    const index = e.currentTarget.dataset.index
    const showDetails = this.data.showDetails
    showDetails[index] = !showDetails[index]
    this.setData({ showDetails })
  },

  formatData(data) {
    try {
      return JSON.stringify(data, null, 2)
    } catch (error) {
      return String(data)
    }
  },

  exportLogs() {
    const text = logger.exportLogs()
    
    if (!text.trim()) {
      util.showError('没有可导出的日志')
      return
    }
    
    // 复制到剪贴板
    wx.setClipboardData({
      data: text,
      success: () => {
        util.showSuccess('已复制到剪贴板')
      }
    })
  },

  clearLogs() {
    wx.showModal({
      title: '清空日志',
      content: '确定要清空所有日志吗？此操作不可恢复。',
      success: (res) => {
        if (res.confirm) {
          logger.clearLogs()
          this.loadLogs()
          util.showSuccess('已清空日志')
        }
      }
    })
  }
})
