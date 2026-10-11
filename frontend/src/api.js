import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  config => config,
  error => Promise.reject(error)
)

// 响应拦截器
api.interceptors.response.use(
  response => {
    // 统一处理后端 { code, data, message } 格式
    const body = response.data
    if (body && typeof body === 'object' && 'code' in body) {
      if (body.code === 0) {
        response.data = body
        return response
      }
      // 业务错误
      return Promise.reject({
        response: {
          status: 400,
          data: body
        },
        message: body.message || body.error || '请求失败'
      })
    }
    return response
  },
  error => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export default api
