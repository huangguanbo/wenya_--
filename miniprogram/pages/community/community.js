const app = getApp()
const api = require('../../utils/api')
const util = require('../../utils/util')

Page({
  data: {
    gradeOptions: [
      { label: '全部年级', value: 'all' },
      { label: '小学', value: 'elementary' },
      { label: '初中', value: 'middle' },
      { label: '高中', value: 'high' }
    ],
    sortOptions: [
      { label: '最新发布', value: 'latest' },
      { label: '最多点赞', value: 'likes' },
      { label: '最高分', value: 'score' }
    ],
    gradeIndex: 0,
    sortIndex: 0,
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
    // 刷新列表
    this.setData({
      page: 1,
      works: []
    }, () => {
      this.loadWorks()
    })
  },

  async loadWorks() {
    if (this.data.loading) return
    
    this.setData({ loading: true })
    
    try {
      const grade = this.data.gradeOptions[this.data.gradeIndex].value
      const sort = this.data.sortOptions[this.data.sortIndex].value
      
      const res = await api.get('/community/works', {
        page: this.data.page,
        per_page: this.data.perPage,
        grade: grade === 'all' ? undefined : grade,
        sort: sort
      })
      
      const newWorks = (res.data || []).map(work => ({
        ...work,
        created_at: util.formatRelativeTime(work.created_at),
        is_liked: work.is_liked || false
      }))
      
      this.setData({
        works: this.data.page === 1 ? newWorks : [...this.data.works, ...newWorks],
        hasMore: newWorks.length === this.data.perPage,
        loading: false
      })
    } catch (error) {
      console.error('加载社区作品失败:', error)
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
      gradeIndex: e.detail.value,
      page: 1,
      works: []
    }, () => {
      this.loadWorks()
    })
  },

  onSortChange(e) {
    this.setData({
      sortIndex: e.detail.value,
      page: 1,
      works: []
    }, () => {
      this.loadWorks()
    })
  },

  async toggleLike(e) {
    const id = e.currentTarget.dataset.id
    const work = this.data.works.find(w => w.id === id)
    
    if (!work) return
    
    try {
      const endpoint = work.is_liked 
        ? `/community/works/${id}/unlike`
        : `/community/works/${id}/like`
      
      await api.post(endpoint)
      
      // 更新本地状态
      const works = this.data.works.map(w => {
        if (w.id === id) {
          return {
            ...w,
            is_liked: !w.is_liked,
            like_count: w.is_liked ? w.like_count - 1 : w.like_count + 1
          }
        }
        return w
      })
      
      this.setData({ works })
    } catch (error) {
      util.showError('操作失败')
    }
  },

  goToDetail(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({
      url: `/pages/writing-detail/writing-detail?id=${id}&type=community`
    })
  }
})
