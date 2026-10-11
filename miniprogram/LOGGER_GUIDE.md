# 运行日志功能说明

## 功能概述

为文芽小程序添加了运行日志记录功能，仅记录**错误 (error)** 和**警告 (warning)** 两个级别的日志，帮助开发者快速定位和解决问题。

## 日志级别

| 级别 | 说明 | 触发场景 |
|------|------|---------|
| `error` | 错误 | API 请求失败、未处理的异常、功能不可用等 |
| `warning` | 警告 | API 业务错误、登录态过期、数据异常等 |

**注意**: 普通信息日志（info）和调试日志（debug）不会记录，避免日志过多影响性能。

## 使用方式

### 1. 在代码中记录日志

```javascript
const logger = require('../../utils/logger')

// 记录错误日志
logger.error('API 请求失败', {
  url: '/api/writing',
  method: 'POST',
  errMsg: 'network timeout'
})

// 记录警告日志
logger.warning('API 业务错误', {
  url: '/api/writing',
  code: 400,
  message: '标题不能为空'
})
```

### 2. 查看日志

在个人中心页面，**开发模式下**会显示"运行日志"入口：

1. 进入"我的"页面
2. 点击"运行日志"菜单项
3. 查看日志列表（最多显示 100 条）

### 3. 日志详情

每条日志包含以下信息：
- **级别**: ERROR 或 WARNING
- **时间**: 本地格式化时间
- **页面**: 日志产生时的页面路径
- **消息**: 日志详细描述
- **详细数据**: 触发日志的附加数据（JSON 格式）
- **设备信息**: 平台、系统版本、小程序版本

### 4. 操作功能

- **刷新**: 重新加载日志列表
- **导出**: 复制日志到剪贴板（便于反馈给开发者）
- **清空**: 清空所有本地存储的日志

## 自动记录的场景

日志工具已自动集成到以下场景：

### 1. 小程序生命周期

```javascript
// app.js
- 小程序启动
- 进入前台
- 进入后台
- 初始化登录失败
- 检查登录失败
```

### 2. API 请求

```javascript
// utils/api.js
- API 请求失败（网络错误、超时等）
- API 业务错误（code !== 0）
- API 响应异常（statusCode 非 200）
- API 请求未授权（401）
```

### 3. 全局错误监听

```javascript
// utils/logger.js
- 小程序页面渲染错误
- 未处理的 Promise 拒绝
```

## 日志存储策略

### 本地存储
- **存储位置**: `wx.setStorageSync('wenya_runtime_logs')`
- **最大数量**: 100 条（超过后自动清理最旧的日志）
- **存储格式**: JSON 数组

### 可选上报
在 `utils/logger.js` 中配置：
```javascript
const ENABLE_REPORT = false  // 生产环境可开启
const REPORT_URL = '/api/log/upload'  // 日志上报接口
```

## 日志查看页面

### 统计卡片
- 错误数量（红色）
- 警告数量（黄色）
- 总数量（蓝色）

### 日志列表
- 按时间倒序显示
- 错误日志左侧红色边框
- 警告日志左侧黄色边框
- 可展开查看详细数据

### 导出格式
```
[ERROR] 2026-10-04 14:30:25 - pages/writing
  Message: API 请求失败
  Data: {
    "url": "/api/writing",
    "method": "POST",
    "errMsg": "network timeout"
  }

---

[WARNING] 2026-10-04 14:28:10 - pages/index
  Message: API 业务错误
  Data: {
    "url": "/api/stats",
    "code": 400,
    "message": "用户未登录"
  }
```

## 最佳实践

### 1. 开发环境
- 保持 `config.DEBUG = true`
- 日志会在控制台输出，便于调试
- 日志自动保存到本地存储

### 2. 生产环境
- 设置 `config.DEBUG = false`
- 开启日志上报 `ENABLE_REPORT = true`
- 定期查看用户反馈的日志

### 3. 问题排查流程
```
用户反馈问题 
  ↓
引导用户导出日志（个人中心 → 运行日志 → 导出）
  ↓
用户发送日志给开发者
  ↓
开发者分析日志定位问题
  ↓
修复并发布
```

## 性能影响

- **内存占用**: 每条日志约 1-2KB，最多存储 100 条
- **CPU 影响**: 可忽略（仅序列化 JSON）
- **网络影响**: 默认不上报，无网络请求

## 隐私保护

日志中**不会**记录以下敏感信息：
- ❌ 用户密码
- ❌ 验证码
- ❌ 完整手机号
- ❌ 身份证号
- ❌ 作文完整内容

日志中**可能**包含的信息：
- ⚠️ API 路径（不含参数）
- ⚠️ 错误消息（可能包含部分用户输入）
- ⚠️ 页面路径
- ⚠️ 设备信息

## 配置项

在 `utils/config.js` 中：

```javascript
module.exports = {
  // ... 其他配置
  
  // 是否启用调试模式
  DEBUG: true,  // 开发环境 true，生产环境 false
  
  // 日志上报开关
  ENABLE_REPORT: false,  // 默认关闭
  
  // 日志上报地址
  REPORT_URL: '/api/log/upload'
}
```

## 后续扩展

### 1. 日志分析后台
开发日志管理后台，自动收集和分析日志数据。

### 2. 告警机制
当错误日志达到阈值时，自动发送告警通知开发者。

### 3. 日志分级用户
区分普通用户、测试用户、开发者的日志记录级别。

## 相关文件

```
miniprogram/
├── utils/
│   ├── logger.js          # 日志工具核心
│   ├── api.js             # API 请求（已集成日志）
│   └── config.js          # 配置（DEBUG 开关）
├── pages/
│   └── logs/              # 日志查看页面
│       ├── logs.wxml
│       ├── logs.js
│       ├── logs.wxss
│       └── logs.json
└── app.js                 # 全局错误监听
```

## 示例代码

### 在页面中记录日志

```javascript
// pages/writing/writing.js
const logger = require('../../utils/logger')

Page({
  async loadWriting(id) {
    try {
      const res = await api.get(`/writing/${id}`)
      // ... 处理数据
    } catch (error) {
      logger.error('加载作文失败', {
        writingId: id,
        error: error.message || error
      })
      util.showError('加载失败')
    }
  },
  
  async saveDraft() {
    if (!this.data.writingId) {
      logger.warning('保存草稿：作文 ID 不存在')
      return
    }
    // ... 保存逻辑
  }
})
```

### 在工具函数中记录日志

```javascript
// utils/auth.js
const logger = require('./logger')

async function login() {
  try {
    const loginRes = await wxPromise('login')
    const res = await api.post('/auth/wx-login', { code: loginRes.code })
    return res.data
  } catch (error) {
    logger.error('微信登录失败', {
      code: error.code,
      message: error.message
    })
    throw error
  }
}
```

## 常见问题

### Q: 为什么看不到日志入口？
A: 日志入口仅在开发模式（`config.DEBUG = true`）下显示，普通用户不可见。

### Q: 日志什么时候会被清空？
A: 手动清空、存储超过 100 条时自动清理最旧的、或小程序被卸载。

### Q: 如何永久保存日志？
A: 使用"导出"功能复制到剪贴板，然后粘贴到文档中保存。

### Q: 日志会上报到服务器吗？
A: 默认不会。如需开启，设置 `ENABLE_REPORT = true` 并实现上报接口。

---

**创建时间**: 2026 年 10 月 4 日
**版本**: 1.0.0
