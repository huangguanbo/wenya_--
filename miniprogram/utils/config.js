module.exports = {
  // API 基础地址 - 生产环境请修改为实际域名
  // API_BASE_URL: 'https://your-backend.com/api',

  API_BASE_URL: 'http://localhost:5000/api',

  // API_BASE_URL: 'http://192.168.1.100:5001/api',
  
  // 超时时间（毫秒）
  TIMEOUT: 30000,
  
  // 版本号
  VERSION: '1.0.0',
  
  // 内容安全开关
  CONTENT_SAFE_ENABLED: true,
  
  // AI 功能开关
  AI_ENABLED: true,
  
  // 是否启用调试日志
  DEBUG: true,

  // 微信静默登录：自动注册时使用的默认资料（用户无感知，可在设置页再修改）
  WX_PASSWORD_PREFIX: 'Wx',
  WX_DEFAULT_GRADE: 6,
  WX_DEFAULT_GUARDIAN_NAME: '家长',
  WX_DEFAULT_GUARDIAN_RELATIONSHIP: 'parent'
}
