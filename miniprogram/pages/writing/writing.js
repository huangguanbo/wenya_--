const app = getApp()
const api = require('../../utils/api')
const util = require('../../utils/util')

Page({
  data: {
    title: '',
    content: '',
    wordCount: 0,
    writingId: null,
    messages: [],
    inputMessage: '',
    loading: false,
    saving: false,
    autoSaveStatus: '',
    showAiChat: false,
    scrollToView: '',
    quickActions: [
      { label: '💡 审题指导', value: 'help_understand_prompt', sessionType: 'help_understand_prompt' },
      { label: '📚 素材启发', value: 'suggest_materials', sessionType: 'suggest_materials' },
      { label: '✏️ 段落修改', value: 'revise_paragraph', sessionType: 'revise_paragraph' },
      { label: '📊 评分标准', value: 'explain_scoring', sessionType: 'explain_scoring' }
    ]
  },

  autoSaveTimer: null,

  onLoad(options) {
    if (options.id) {
      this.setData({ writingId: options.id })
      this.loadWriting(options.id)
    }
  },

  onUnload() {
    if (this.autoSaveTimer) {
      clearTimeout(this.autoSaveTimer)
    }
  },

  async loadWriting(id) {
    util.showLoading()
    try {
      const res = await api.get(`/writing/${id}`)
      const data = res.data || {}
      
      this.setData({
        title: data.title || '',
        content: data.content || '',
        wordCount: data.word_count || 0
      })
    } catch (error) {
      console.error('加载作文失败:', error)
      util.showError('加载失败')
    } finally {
      util.hideLoading()
    }
  },

  onTitleInput(e) {
    const title = e.detail.value
    this.setData({ title })
    
    // 自动创建草稿
    if (!this.data.writingId && (title || this.data.content)) {
      this.createWriting()
    }
    this.scheduleAutoSave()
  },

  onContentInput(e) {
    const content = e.detail.value
    this.setData({
      content,
      wordCount: content.length
    })
    
    // 自动创建草稿
    if (!this.data.writingId && (title || content)) {
      this.createWriting()
    }
    this.scheduleAutoSave()
  },

  onInputMessage(e) {
    this.setData({
      inputMessage: e.detail.value
    })
  },

  scheduleAutoSave() {
    if (this.autoSaveTimer) {
      clearTimeout(this.autoSaveTimer)
    }
    
    this.autoSaveTimer = setTimeout(() => {
      if (this.data.writingId) {
        this.saveDraft()
      }
    }, 5000)
  },

  async createWriting() {
    try {
      const res = await api.post('/writing', {
        title: this.data.title || '未命名作文',
        content: this.data.content
      })
      
      this.setData({
        writingId: res.data.id
      })
    } catch (error) {
      console.error('创建作文失败:', error)
    }
  },

  async saveDraft() {
    if (!this.data.writingId) return
    
    this.setData({
      saving: true,
      autoSaveStatus: '保存中...'
    })
    
    try {
      await api.post(`/writing/${this.data.writingId}/draft`, {
        title: this.data.title,
        content: this.data.content
      })
      
      this.setData({
        autoSaveStatus: '已保存'
      })
      
      setTimeout(() => {
        this.setData({
          autoSaveStatus: ''
        })
      }, 2000)
    } catch (error) {
      this.setData({
        autoSaveStatus: '保存失败'
      })
      
      setTimeout(() => {
        this.setData({
          autoSaveStatus: ''
        })
      }, 2000)
    } finally {
      this.setData({
        saving: false
      })
    }
  },

  submitWriting() {
    if (!this.data.canSubmit) return
    
    wx.showModal({
      title: '提交评分',
      content: '确定要提交作文进行评分吗？',
      success: async (res) => {
        if (res.confirm) {
          await this.doSubmit()
        }
      }
    })
  },

  async doSubmit() {
    util.showLoading('提交中...')
    
    try {
      await api.post(`/writing/${this.data.writingId}/submit`, {
        title: this.data.title,
        content: this.data.content
      })
      
      util.hideLoading()
      wx.showToast({
        title: '已提交评分',
        icon: 'success'
      })
      
      // 跳转到详情页
      wx.navigateTo({
        url: `/pages/writing-detail/writing-detail?id=${this.data.writingId}`
      })
    } catch (error) {
      util.hideLoading()
      util.showError('提交失败，请稍后重试')
    }
  },

  toggleAiChat() {
    this.setData({
      showAiChat: !this.data.showAiChat
    })
  },

  async sendMessage() {
    if (!this.data.inputMessage.trim() || this.data.loading || !this.data.writingId) {
      return
    }

    const message = this.data.inputMessage.trim()
    const messages = this.data.messages
    messages.push({ role: 'user', content: message })
    
    this.setData({
      messages,
      inputMessage: '',
      loading: true,
      scrollToView: `msg-${messages.length - 1}`
    })

    try {
      const res = await api.post(`/writing/${this.data.writingId}/ai-chat`, {
        message: message,
        session_type: 'writing_guidance'
      })
      
      messages.push({ role: 'assistant', content: res.data.response })
      
      this.setData({
        messages,
        loading: false,
        scrollToView: `msg-${messages.length - 1}`
      })
    } catch (error) {
      messages.push({ role: 'assistant', content: 'AI 教练暂时不可用，请稍后再试。' })
      
      this.setData({
        messages,
        loading: false,
        scrollToView: `msg-${messages.length - 1}`
      })
    }
  },

  sendQuickAction(e) {
    const type = e.currentTarget.dataset.type
    this.setData({
      inputMessage: type.label.replace(/^[^\s]+\s/, '')
    })
    this.sendMessage(type.sessionType)
  },

  get canSubmit() {
    return this.data.title.trim() && this.data.content.length >= 100 && this.data.writingId
  }
})
