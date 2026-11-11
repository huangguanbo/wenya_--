const app = getApp()
const api = require('../../utils/api')
const util = require('../../utils/util')

Page({
  data: {
    title: '',
    content: '',
    wordCount: 0,
    writingId: null,
    canSubmit: false,
    messages: [],
    inputMessage: '',
    loading: false,
    saving: false,
    autoSaveStatus: '',
    showAiChat: false,
    scrollToView: '',
    quickActions: [
      { label: '💡 审题指导', sessionType: 'help_understand_prompt' },
      { label: '📚 素材启发', sessionType: 'suggest_materials' },
      { label: '✏️ 段落修改', sessionType: 'revise_paragraph' },
      { label: '📊 评分标准', sessionType: 'explain_scoring' }
    ]
  },

  autoSaveTimer: null,
  creating: false,

  onShow() {
    if (!app.isLoggedIn()) {
      wx.reLaunch({
        url: '/pages/login/login'
      })
      return
    }

    // writing 是 tabBar 页面，无法通过 url 参数传值，改用全局意图
    const intent = app.globalData.writingIntent
    if (!intent) return

    app.globalData.writingIntent = null

    if (intent.action === 'edit' && intent.id) {
      this.setData({ writingId: Number(intent.id) })
      this.loadWriting(intent.id)
      return
    }

    this.resetDraft()
  },

  resetDraft() {
    if (this.autoSaveTimer) {
      clearTimeout(this.autoSaveTimer)
      this.autoSaveTimer = null
    }

    this.setData({
      title: '',
      content: '',
      wordCount: 0,
      writingId: null,
      canSubmit: false,
      messages: [],
      inputMessage: '',
      loading: false,
      saving: false,
      autoSaveStatus: '',
      showAiChat: false,
      scrollToView: ''
    })
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
      const writing = res.data && res.data.writing

      if (!writing) {
        throw new Error('作文不存在')
      }

      if (writing.status !== 'draft') {
        wx.redirectTo({
          url: `/pages/writing-detail/writing-detail?id=${writing.id}`
        })
        return
      }

      this.setData({
        title: writing.title || '',
        content: writing.content || '',
        wordCount: util.countWords(writing.content),
        canSubmit: this.checkCanSubmit(writing.title, writing.content, writing.id)
      })

      this.loadChatHistory(id)
    } catch (error) {
      console.error('加载作文失败:', error)
      util.showError(error.message || '加载失败')
    } finally {
      util.hideLoading()
    }
  },

  async loadChatHistory(id) {
    try {
      const res = await api.get(`/writing/${id}/ai-chat`)
      this.setData({
        messages: (res.data && res.data.messages) || []
      })
    } catch (error) {
      console.error('加载对话历史失败:', error)
    }
  },

  checkCanSubmit(title, content, writingId) {
    return !!title.trim() && util.countWords(content) >= 100 && !!writingId
  },

  onTitleInput(e) {
    const title = e.detail.value
    this.setData({
      title,
      canSubmit: this.checkCanSubmit(title, this.data.content, this.data.writingId)
    })

    this.ensureWriting()
    this.scheduleAutoSave()
  },

  onContentInput(e) {
    const content = e.detail.value
    this.setData({
      content,
      wordCount: util.countWords(content),
      canSubmit: this.checkCanSubmit(this.data.title, content, this.data.writingId)
    })

    this.ensureWriting()
    this.scheduleAutoSave()
  },

  async ensureWriting() {
    if (this.data.writingId || this.creating) return

    const title = this.data.title.trim()
    const content = this.data.content

    if (!title || !util.countWords(content)) return

    this.creating = true

    try {
      const res = await api.post('/writing', {
        title,
        content
      })

      const writing = res.data && res.data.writing
      if (writing) {
        this.setData({
          writingId: writing.id,
          canSubmit: this.checkCanSubmit(title, content, writing.id)
        })
      }
    } catch (error) {
      console.error('创建作文失败:', error)
    } finally {
      this.creating = false
    }
  },

  onSaveTap() {
    this.saveDraft(true)
  },

  scheduleAutoSave() {
    if (this.autoSaveTimer) {
      clearTimeout(this.autoSaveTimer)
    }

    this.autoSaveTimer = setTimeout(() => {
      this.saveDraft()
    }, 5000)
  },

  async saveDraft(manual = false) {
    if (!this.data.writingId) {
      if (manual) {
        util.showError('请先填写标题和正文')
      }
      return
    }

    if (!this.data.content.trim()) {
      if (manual) {
        util.showError('正文不能为空')
      }
      return
    }

    this.setData({
      saving: true,
      autoSaveStatus: '保存中...'
    })

    try {
      await api.post(`/writing/${this.data.writingId}/draft`, {
        title: this.data.title,
        content: this.data.content
      })

      this.setData({ autoSaveStatus: '已保存' })
    } catch (error) {
      this.setData({ autoSaveStatus: '保存失败' })
    } finally {
      this.setData({ saving: false })
      setTimeout(() => {
        this.setData({ autoSaveStatus: '' })
      }, 2000)
    }
  },

  submitWriting() {
    if (!this.data.canSubmit) {
      util.showError(`至少 100 字才能提交评分`)
      return
    }

    wx.showModal({
      title: '提交评分',
      content: '确定要提交作文进行评分吗？提交后不可修改。',
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
      await api.post(`/writing/${this.data.writingId}/draft`, {
        title: this.data.title,
        content: this.data.content
      })
      const res = await api.post(`/writing/${this.data.writingId}/submit`)
      const message = res.message || '评分完成'

      util.hideLoading()
      wx.showToast({
        title: message,
        icon: message.indexOf('模拟') >= 0 ? 'none' : 'success'
      })

      wx.redirectTo({
        url: `/pages/writing-detail/writing-detail?id=${this.data.writingId}`
      })
    } catch (error) {
      util.hideLoading()
      util.showError(error.message || '提交失败，请稍后重试')
    }
  },

  toggleAiChat() {
    this.setData({
      showAiChat: !this.data.showAiChat
    })
  },

  onInputMessage(e) {
    this.setData({
      inputMessage: e.detail.value
    })
  },

  async sendMessage(text, sessionType = 'writing_guidance') {
    const raw = typeof text === 'string' ? text : this.data.inputMessage
    const message = raw.trim()

    if (!message || this.data.loading) return

    if (!this.data.writingId) {
      util.showError('请先填写标题和正文')
      return
    }

    const messages = this.data.messages.concat([{ role: 'user', content: message }])

    this.setData({
      messages,
      inputMessage: '',
      loading: true,
      scrollToView: `msg-${messages.length - 1}`
    })

    try {
      const res = await api.post(`/writing/${this.data.writingId}/ai-chat`, {
        message,
        session_type: sessionType
      })

      const reply = (res.data && res.data.response) || '抱歉，我暂时无法回答。'
      this.appendMessage({ role: 'assistant', content: reply })
    } catch (error) {
      this.appendMessage({ role: 'assistant', content: error.message || 'AI 教练暂时不可用，请稍后再试。' })
    }
  },

  appendMessage(message) {
    const messages = this.data.messages.concat([message])
    this.setData({
      messages,
      loading: false,
      scrollToView: `msg-${messages.length - 1}`
    })
  },

  sendQuickAction(e) {
    const action = e.currentTarget.dataset.type
    this.sendMessage(action.label.replace(/^[^\s]+\s/, ''), action.sessionType)
  }
})