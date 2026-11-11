const app = getApp()
const api = require('../../utils/api')
const util = require('../../utils/util')

Page({
  data: {
    gradeOptions: [
      { label: '全部年级', value: '' },
      { label: '小学', value: 'elementary' },
      { label: '初中', value: 'middle' },
      { label: '高中', value: 'high' }
    ],
    gradeIndex: 0,
    works: [],
    page: 1,
    perPage: 10,
    hasMore: true,
    loading: false
  },

  onLoad() {
    this.loadWorks()
  },

  onShow() {
    this.setData({
      page: 1,
      works: [],
      hasMore: true
    }, () => {
      this.loadWorks()
    })
  },

  async loadWorks() {
    if (this.data.loading) return

    this.setData({ loading: true })

    try {
      const schoolStage = this.data.gradeOptions[this.data.gradeIndex].value
      const res = await api.get('/community/works', {
        page: this.data.page,
        per_page: this.data.perPage,
        school_stage: schoolStage || undefined
      })

      const newWorks = (res.data || []).map(work => ({
        ...work,
        author_name: (work.author && work.author.nickname) || '匿名同学',
        author_avatar: (work.author && work.author.avatar_url) || '/images/default-avatar.png',
        grade_name: work.author_grade_text || '',
        created_at: util.formatRelativeTime(work.published_at || work.created_at),
        is_liked: work.is_liked || false
      }))

      const pagination = res.pagination || {}

      this.setData({
        works: this.data.page === 1 ? newWorks : this.data.works.concat(newWorks),
        hasMore: pagination.has_next !== undefined
          ? pagination.has_next
          : newWorks.length === this.data.perPage
      })
    } catch (error) {
      console.error('加载社区作品失败:', error)
    } finally {
      this.setData({ loading: false })
    }
  },

  onReachBottom() {
    if (this.data.hasMore && !this.data.loading) {
      this.setData({
        page: this.data.page + 1
      }, () => {
        this.loadWorks()
      })
    }
  },

  onGradeChange(e) {
    this.setData({
      gradeIndex: Number(e.detail.value),
      page: 1,
      works: [],
      hasMore: true
    }, () => {
      this.loadWorks()
    })
  },

  async toggleLike(e) {
    if (!app.isLoggedIn()) {
      wx.navigateTo({
        url: '/pages/login/login'
      })
      return
    }

    const id = e.currentTarget.dataset.id

    try {
      const res = await api.post(`/community/works/${id}/like`)
      const data = res.data || {}

      this.setData({
        works: this.data.works.map(work => {
          if (work.id !== id) return work
          return {
            ...work,
            is_liked: data.is_liked,
            like_count: data.like_count
          }
        })
      })
    } catch (error) {
      util.showError(error.message || '操作失败')
    }
  },

  goToDetail(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({
      url: `/pages/writing-detail/writing-detail?id=${id}&type=community`
    })
  }
})